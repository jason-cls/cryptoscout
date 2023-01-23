import logging

from commons import (
    check_expected_cols,
    check_null_cols,
    init_argparser,
    init_spark,
    read_json_strict,
    sparkconfig,
    write_parquet,
)
from pyspark import SparkConf
from pyspark.sql import functions as F
from pyspark.sql.types import (
    ArrayType,
    DoubleType,
    StructField,
    StructType,
    TimestampType,
)
from pyspark.sql.utils import AnalysisException

APP_NAME = "Stage Coincap Market History"

# Schema of source json files
srcschema = StructType(
    [
        StructField(
            "data",
            ArrayType(
                StructType(
                    [
                        StructField("close", DoubleType(), False),
                        StructField("high", DoubleType(), False),
                        StructField("low", DoubleType(), False),
                        StructField("open", DoubleType(), False),
                        StructField("period", TimestampType(), False),
                        StructField("volume", DoubleType(), False),
                    ]
                )
            ),
            True,
        ),
        StructField("timestamp", TimestampType(), False),
    ]
)
srcdatafields_expect = {"close", "high", "low", "open", "period", "volume", "timestamp"}


def main(appname: str, conf: SparkConf, srcglob: str, writepath: str):
    sc, spark = init_spark(conf)

    # Read json using schema - gracefully exit if no data found
    try:
        df = read_json_strict(srcglob, srcschema, spark, appname)
    except (AnalysisException, AssertionError):
        return

    if df.count() == 0:
        logging.warning(f"{appname} | Aborting PySpark job - no rows present")
        return

    # Restructure nested json data as columns
    df = df.select(F.explode("data").alias("dataExploded"), "timestamp").select(
        "dataExploded.*", "timestamp"
    )

    # Check if all expected columns are present - raises error otherwise
    src_cols = set(df.columns)
    check_expected_cols(srcdatafields_expect, src_cols, appname)

    # Extract filename data - set to null if no match
    regex = r"^.*market_history_(\w+)-(\w+)_\d{8}\.json$"
    df = df.withColumn(
        "exchangeName",
        F.regexp_extract(F.input_file_name(), regex, 1),
    )
    df = df.withColumn(
        "exchangeName",
        F.when(F.col("exchangeName") != "", F.col("exchangeName")).otherwise(None),
    )
    df = df.withColumn(
        "assetName",
        F.regexp_extract(F.input_file_name(), regex, 2),
    )
    df = df.withColumn(
        "assetName",
        F.when(F.col("assetName") != "", F.col("assetName")).otherwise(None),
    )

    # Rename columns
    df = df.withColumnRenamed("period", "timestampUTC").withColumnRenamed(
        "timestamp", "timestampRequestUTC"
    )

    # Extract date
    df = df.withColumn("date", F.to_date("timestampUTC"))

    # Reorder columns and sort rows
    df = df.select(
        "exchangeName",
        "assetName",
        "date",
        "timestampUTC",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "timestampRequestUTC",
    ).sort("exchangeName", "assetName", "timestampUTC")

    # Check for null columns before writing - raises error
    null_cols = check_null_cols(df)
    if null_cols:
        logging.error(
            f"{appname} | Failed to stage dataframe. Columns "
            f"{null_cols} are completely null"
        )
        raise RuntimeError

    # Write to filesystem
    write_parquet(
        path=writepath,
        df=df,
        partition_cols=["exchangeName", "assetName", "date"],
        appname=appname,
    )


if __name__ == "__main__":
    parser = init_argparser()
    args = parser.parse_args()
    DATE = args.srcdate.strftime("%Y-%m-%d")
    YYYY, MM, DD = DATE.split("-")
    srcglob = (
        f"gs://{args.srcbucket}/coincap/market_history/"
        f"year={YYYY}/month={MM}/day={DD}/*.json"
    )
    writepath = f"gs://{args.stgbucket}/coincap/market_history"
    appname_date = f"{APP_NAME}: {DATE}"
    sparkconfig.setAppName(appname_date)
    main(appname_date, sparkconfig, srcglob, writepath)
