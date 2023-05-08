#! /usr/bin/env bash

# Contingency: Rerun airflow services after unexpected VM restarts / GCP maintenance events
# Executed as the root user upon VM boot and reboots.

set -eou pipefail

REPO_DIR=/opt/cryptoscout

# Start airflow only if provisioned and docker files exist in cloned repository
if [ -d "$REPO_DIR" ] \
&& [ -f "${REPO_DIR}/dbt/cryptoscout/.secrets/dbt-sa-key.json" ] \
&& [ -f "${REPO_DIR}/airflow/req.env" ] \
&& [ -f "${REPO_DIR}/airflow/Dockerfile" ] \
&& [ -f "${REPO_DIR}/airflow/docker-compose.yaml"]; then
  cd "${REPO_DIR}/airflow/"
  make airflow-init
  make up
else
  echo "Unable to start Airflow services. Required files in ${REPO_DIR} are missing."
fi
