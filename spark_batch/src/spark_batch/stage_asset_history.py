import logging

from commons import init_argparser, init_spark, sparkconfig
from pyspark import SparkConf
from pyspark.sql import functions as F
from pyspark.sql.types import (
    ArrayType,
    DoubleType,
    LongType,
    StructField,
    StructType,
    TimestampType,
)
from pyspark.sql.utils import AnalysisException

APP_NAME = "Stage Coincap Asset History"

# Schema of source json files
srcschema = StructType(
    [
        StructField(
            "data",
            ArrayType(
                StructType(
                    [
                        StructField("circulatingSupply", DoubleType(), True),
                        StructField("date", TimestampType(), False),
                        StructField("priceUsd", DoubleType(), True),
                        StructField("time", LongType(), False),
                    ]
                )
            ),
            True,
        ),
        StructField("timestamp", TimestampType(), False),
    ]
)


def main(conf: SparkConf, srcglob: str, writepath: str):
    sc, spark = init_spark(conf)

    # Read json using schema - gracefully exit if no data found
    print(f"{APP_NAME} | Reading source data from {srcglob}")
    try:
        df = spark.read.option("mode", "FAILFAST").json(srcglob, schema=srcschema)
    except AnalysisException as e:
        logging.warning(f"{APP_NAME} | Aborting PySpark job - no data read:\n {e}")
        return

    # Extract filename data
    df = df.withColumn(
        "assetName",
        F.regexp_extract(
            F.input_file_name(), r"^.*asset_history_(\w+)_\d{8}\.json$", 1
        ),
    )

    # Restructure nested json data as columns
    df = df.select(
        "assetName", F.explode("data").alias("dataExploded"), "timestamp"
    ).select("assetName", "dataExploded.*", "timestamp")

    # Rename columns
    df = (
        df.withColumnRenamed("date", "timestampUTC")
        .withColumnRenamed("time", "timestampUnixMs")
        .withColumnRenamed("timestamp", "timestampRequestUTC")
    )

    # Extract date
    df = df.withColumn("date", F.to_date("timestampUTC"))

    # Reorder columns and sort rows
    df = df.select(
        "assetName",
        "date",
        "timestampUTC",
        "timestampUnixMs",
        "circulatingSupply",
        "priceUsd",
        "timestampRequestUTC",
    ).sort("assetName", "timestampUTC")

    # Write to filesystem
    print(f"{APP_NAME} | Writing data to {writepath}")
    df.write.partitionBy("assetName", "date").mode("overwrite").parquet(writepath)
    print(
        f"{APP_NAME} | Done staging data to {writepath} with"
        f" schema:\n{df.schema.simpleString()}"
    )


if __name__ == "__main__":
    parser = init_argparser()
    args = parser.parse_args()
    DATE = args.srcdate.strftime("%Y-%m-%d")
    YYYY, MM, DD = DATE.split("-")
    srcglob = (
        f"gs://{args.srcbucket}/coincap/asset_history/"
        f"year={YYYY}/month={MM}/day={DD}/*.json"
    )
    writepath = f"gs://{args.stgbucket}/coincap/asset_history"
    sparkconfig.setAppName(f"{APP_NAME}: {DATE}")
    main(sparkconfig, srcglob, writepath)
