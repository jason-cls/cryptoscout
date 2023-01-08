import argparse
from datetime import datetime

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

sparkconfig = (
    SparkConf()
    .set(
        "spark.hadoop.fs.AbstractFileSystem.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
    )
    .set("spark.hadoop.fs.gs.auth.type", "APPLICATION_DEFAULT")
    .set("spark.sql.session.timeZone", "UTC")
)


def init_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "srcdate",
        help="The date to process data in YYYY-MM-DD format",
        type=_validate_date,
    )
    parser.add_argument("srcbucket", help="The GCS bucket to source data from")
    parser.add_argument("stgbucket", help="The GCS bucket to stage output data")
    return parser


def init_spark(conf: SparkConf | None = None) -> tuple[SparkContext, SparkSession]:
    sparkcontext = SparkContext.getOrCreate(conf)
    sparksession = SparkSession(sparkcontext)
    sparksession.sparkContext.setLogLevel("WARN")
    return sparkcontext, sparksession


def _validate_date(arg: str) -> datetime:
    try:
        return datetime.strptime(arg, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date: {arg}. Must be formatted as YYYY-MM-DD."
        )
