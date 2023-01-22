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
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)
from pyspark.sql.utils import AnalysisException

APP_NAME = "Stage Coincap Asset Info"

# Schema of source json files
srcschema = StructType(
    [
        StructField(
            "data",
            StructType(
                [
                    StructField("changePercent24Hr", DoubleType(), False),
                    StructField("explorer", StringType(), True),
                    StructField("id", StringType(), False),
                    StructField("marketCapUsd", DoubleType(), False),
                    StructField("maxSupply", DoubleType(), True),
                    StructField("name", StringType(), False),
                    StructField("priceUsd", DoubleType(), False),
                    StructField("rank", LongType(), False),
                    StructField("supply", DoubleType(), False),
                    StructField("symbol", StringType(), False),
                    StructField("volumeUsd24Hr", DoubleType(), False),
                    StructField("vwap24Hr", DoubleType(), False),
                ]
            ),
            True,
        ),
        StructField("timestamp", TimestampType(), False),
    ]
)
srcdatafields_expect = {
    "changePercent24Hr",
    "explorer",
    "id",
    "marketCapUsd",
    "maxSupply",
    "name",
    "priceUsd",
    "rank",
    "supply",
    "symbol",
    "volumeUsd24Hr",
    "vwap24Hr",
}


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
    df = df.select("data.*", "timestamp")

    # Check if all expected columns are present - gracefully exit if not
    src_cols = set(df.columns)
    if not check_expected_cols(srcdatafields_expect, src_cols, appname):
        return

    # Rename columns
    df = (
        df.withColumnRenamed("id", "assetName")
        .withColumnRenamed("name", "fullAssetName")
        .withColumnRenamed("timestamp", "timestampUTC")
    )

    # Extract date
    df = df.withColumn("date", F.to_date("timestampUTC"))

    # Reorder columns and sort rows
    df = df.select(
        "assetName",
        "date",
        "timestampUTC",
        "rank",
        "symbol",
        "fullAssetName",
        "supply",
        "maxSupply",
        "marketCapUsd",
        "volumeUsd24Hr",
        "priceUsd",
        "changePercent24Hr",
        "vwap24Hr",
        "explorer",
    ).sort("assetName", "timestampUTC")

    # Check for null columns before writing - raises error
    null_cols = check_null_cols(df)
    if null_cols:
        logging.error(
            f"{appname} | Failed to stage dataframe. Columns "
            f"{null_cols} are completely null"
        )
        raise RuntimeError

    df.show(20, truncate=False)
    df.printSchema()

    # Write to filesystem
    write_parquet(
        path=writepath, df=df, partition_cols=["assetName", "date"], appname=appname
    )


if __name__ == "__main__":
    parser = init_argparser()
    args = parser.parse_args()
    DATE = args.srcdate.strftime("%Y-%m-%d")
    YYYY, MM, DD = DATE.split("-")
    srcglob = (
        f"gs://{args.srcbucket}/coincap/asset_info/"
        f"year={YYYY}/month={MM}/day={DD}/*.json"
    )
    writepath = f"gs://{args.stgbucket}/coincap/asset_info"
    appname_date = f"{APP_NAME}: {DATE}"
    sparkconfig.setAppName(appname_date)
    main(appname_date, sparkconfig, srcglob, writepath)
