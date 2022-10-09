#! /usr/bin/env bash

# Generates a random 256 bit (32 byte) Base64-encoded key using OpenSSL CLI and outputs
# it to the relative terraform/secrets directory.
# If the filename already exists, it is not replaced.

OUTPUT_KEYFILE="encryptionkey.gcs.tfbackend"

abs_scriptdir="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
parent_dir="$(dirname "$abs_scriptdir")"
OUTPUT_PATH="${parent_dir}/secrets/${OUTPUT_KEYFILE}"

if [ -f $OUTPUT_PATH ]; then
  echo "WARNING - No encryption key was generated. Output keyfile already exists at $OUTPUT_PATH"
else
  mkdir ${parent_dir}/secrets > /dev/null 2>&1
  KEY=$(openssl rand -base64 32)
  echo "encryption_key = \"$KEY\"" > $OUTPUT_PATH
  echo "SUCCESS - Generated encryption keyfile saved to: $OUTPUT_PATH"
fi
