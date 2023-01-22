import argparse
import logging
from datetime import datetime

from pyspark import SparkConf, SparkContext
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType
from pyspark.sql.utils import AnalysisException

sparkconfig = (
    SparkConf()
    .set(
        "spark.hadoop.fs.AbstractFileSystem.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
    )
    .set("spark.hadoop.fs.gs.auth.type", "APPLICATION_DEFAULT")
    .set("spark.sql.sources.partitionOverwriteMode", "dynamic")
    .set("spark.sql.session.timeZone", "UTC")
)


def check_expected_cols(
    cols_expect: set[str], cols_tocheck: set[str], appname: str
) -> bool:
    """Returns True if cols_expect is a subset of cols_tocheck."""
    if not cols_expect.issubset(cols_tocheck):
        missing_cols = cols_expect - cols_tocheck
        logging.warning(
            f"{appname} | Aborting PySpark job - columns {missing_cols} are missing"
            f" from the read data columns {cols_tocheck}. Expected all columns in"
            f" {cols_expect}."
        )
        return False
    return True


def check_null_cols(df: DataFrame) -> list[str]:
    """Returns a list of column names in a DataFrame which are completely null."""
    null_cols: list[str] = []
    num_rows = df.count()
    for c in df.columns:
        num_null = df.where(F.col(c).isNull()).count()
        if num_null == num_rows:
            null_cols.append(c)
    return null_cols


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


def read_json_strict(
    path: str, jsonschema: StructType, spark: SparkSession, appname: str
) -> DataFrame:
    """
    Read json using a schema. Fails if upon schema mismatch.
    Raises pyspark.sql.utils.AnalysisException if no data is read.
    """
    print(f"{appname} | Reading source data from {path}")
    try:
        df = spark.read.option("mode", "FAILFAST").json(path, schema=jsonschema)
        df.show()  # Trigger lazy evaluation early to fail as soon as possible
        return df
    except AnalysisException as e:
        logging.warning(f"{appname} | Aborting PySpark job - no data read:\n {e}")
        raise AnalysisException


def write_parquet(path: str, df: DataFrame, partition_cols: list[str], appname: str):
    print(f"{appname} | Writing data to {path}")
    df.write.partitionBy(partition_cols).mode("overwrite").parquet(path)
    print(
        f"{appname} | Done staging data to {path} with"
        f" schema:\n{df.schema.simpleString()}"
    )


def _validate_date(arg: str) -> datetime:
    try:
        return datetime.strptime(arg, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date: {arg}. Must be formatted as YYYY-MM-DD."
        )
