#!/usr/bin/env bash

# Installs Airflow locally using known-to-be-working constraints.

set -eou pipefail

AIRFLOW_VERSION=2.5.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

python -m pip install "apache-airflow[google,celery]==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
echo "Done installing Airflow ${AIRFLOW_VERSION} for Python ${PYTHON_VERSION} via pip"
