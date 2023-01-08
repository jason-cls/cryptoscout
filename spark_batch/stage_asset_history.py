import logging
import sys

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
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

# SRC_DATE = sys.argv[1]
# GCS_BKT_SOURCE = sys.argv[2]
# GCS_BKT_STAGE = sys.argv[3]

# APP_NAME = f"Stage Coincap Asset History: {SRC_DATE}"
APP_NAME = "Stage Coincap Asset History"

conf = (
    SparkConf()
    .setAppName(APP_NAME)
    .set(
        "spark.hadoop.fs.AbstractFileSystem.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
    )
    .set("spark.hadoop.fs.gs.auth.type", "APPLICATION_DEFAULT")
    .set("spark.sql.session.timeZone", "UTC")
)

srcglob = "gs://raw-cryptoscout/coincap/asset_history/year=2022/month=01/day=01/*.json"
writepath = "gs://stage-cryptoscout/coincap/asset_history"
srcschema = StructType(
    [
        StructField(
            "data",
            ArrayType(
                StructType(
                    [
                        StructField("circulatingSupply", DoubleType(), True),
                        StructField("date", TimestampType(), False),
                        StructField("priceUsd", DoubleType(), False),
                        StructField("time", LongType(), False),
                    ]
                )
            ),
        ),
        StructField("timestamp", TimestampType(), False),
    ]
)


def init_spark():
    sparkcontext = SparkContext.getOrCreate(conf)
    sparksession = SparkSession(sparkcontext)
    return sparkcontext, sparksession


def main():
    sc, spark = init_spark()

    # Read json using schema - gracefully exit if no data found
    print(f"{APP_NAME} | Reading source data from {srcglob}")
    try:
        df = spark.read.json(srcglob, schema=srcschema)
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

    # Reorder columns to write
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

    df.show(20, truncate=False)
    df.printSchema()
    # spark.sparkContext.getConf().getAll()


if __name__ == "__main__":
    main()
