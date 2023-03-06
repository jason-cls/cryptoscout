#!/usr/bin/env bash

# Configures Application Default Credentials for Docker container initialization.
# Sets the GOOGLE_APPLICATION_CREDENTIALS to the path of a valid service account
# JSON private key file only if the path exists.

SA_KEY_FILE=/opt/airflow/.secrets/airflow-sa-key.json

if [ -f "${SA_KEY_FILE}" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="${SA_KEY_FILE}"
    echo "GOOGLE_APPLICATION_CREDENTIALS env variable has been set"
else
    echo "GOOGLE_APPLICATION_CREDENTIALS was not set. File ${SA_KEY_FILE} not found."
fi
