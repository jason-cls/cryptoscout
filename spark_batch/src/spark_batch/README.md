## Running Locally
PySpark applications can be run locally via the `spark-submit` command.

```
spark-submit <command-options> <pyspark-application> <application-args>
```

For example we can run the `stage_asset_history.py` PySpark app locally.
```
spark-submit --py-files commons.py stage_asset_history.py 2022-01-01 raw-cryptoscout stage-cryptoscout
```

### Local Prerequisites
1. Install PySpark locally via pip in a virtualenv using `dev-requirements.txt`
2. Clone [this repo of hadoop connectors](https://github.com/GoogleCloudDataproc/hadoop-connectors)
3. [Build the Cloud Storage Connector](https://github.com/GoogleCloudDataproc/hadoop-connectors#building-the-cloud-storage-connector)
4. Copy the Cloud Storage connector shaded JAR from the `gcs/target/` directory to the virtualenv `pyspark/jars/` directory.
    ```
    cp hadoop-connectors/gcs/target/gcs-connector-3.0.0-SNAPSHOT-shaded.jar ~/.pyenv/versions/3.10.9/envs/crypto-pyspark-3.10.9/lib/python3.10/site-packages/pyspark/jars/
    ```
5. Place a JSON service account key named `dataproc-sa-key.json` in the relative `.secrets/` directory which has the necessary permissions to access GCS.
6. Set the environment variables `GOOGLE_APPLICATION_CREDENTIALS` and `SPARK_HOME`. Update `PATH` and `PYTHONPATH` to include `SPARK_HOME`. The helper file `dev.env` can be modified if necessary and sourced to do this.
    ```
    source dev.env
    ```
