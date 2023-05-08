#! /usr/bin/env bash

# Copies terraform generated service account keys and .env files to local target directories
# to facilitate local development.

set -eou pipefail

abs_scriptdir="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
parent_dir="$(dirname "$abs_scriptdir")"
base_dir="$(dirname "$parent_dir")"

cp "${parent_dir}/secrets/airflow-sa-key.json" "${base_dir}/airflow/.secrets/airflow-sa-key.json" \
&& cp "${parent_dir}/secrets/airflow-req.env" "${base_dir}/airflow/req.env" \
&& cp "${parent_dir}/secrets/batch-sa-key.json" "${base_dir}/batch_ingest/src/batch_ingest/.secrets/batch-sa-key.json" \
&& cp "${parent_dir}/secrets/batchingest.env" "${base_dir}/batch_ingest/src/batch_ingest/.env" \
&& cp "${parent_dir}/secrets/dataproc-sa-key.json" "${base_dir}/spark_batch/src/spark_batch/.secrets/dataproc-sa-key.json" \
&& cp "${parent_dir}/secrets/dbt-sa-key.json" "${base_dir}/dbt/cryptoscout/.secrets/dbt-sa-key.json" \
&& echo "Successfully copied files to child directories under ${base_dir}" \
|| echo "Source files to copy may not exist. Run 'terraform apply' beforehand to generate source files."
