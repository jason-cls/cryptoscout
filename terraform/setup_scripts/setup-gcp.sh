#! /usr/bin/env bash

# Helper script which sets up GCP provider Terraform prerequisites. 
# Run prior to initializing and running Terraform.
# Uses gcloud cli to configure the following resources in an existing GCP project:
#   - Service account for Terraform. A corresponding key is saved locally.
#   - GCS bucket to store Terraform remote state


GCP_PROJECT="cryptoscout"
SERVICEACC_NAME="terraform"
SERVICEACC_ROLES=("roles/editor" "roles/storage.objectAdmin")
GCS_TFBACKEND_BKT_NAME="terraform-backend-cs"
GCS_BKT_LOCATION="us-central1"

abs_scriptdir="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
parent_dir="$(dirname "$abs_scriptdir")"

# Create IAM service account for Terraform
gcloud iam service-accounts create $SERVICEACC_NAME \
  --project=$GCP_PROJECT \
  --description="Terraform service account used to provision GCP resources" \
  --display-name="Terraform"

for role in ${SERVICEACC_ROLES[@]}; do
  gcloud projects add-iam-policy-binding $GCP_PROJECT \
    --member="serviceAccount:${SERVICEACC_NAME}@${GCP_PROJECT}.iam.gserviceaccount.com" \
    --role=$role
done

# Generate a service account key if not present
KEYOUTPUT_PATH="${parent_dir}/secrets/terraform-sa-key.json"

if [ -f $KEYOUTPUT_PATH ]; then
  echo "WARNING - No service account key was generated. Key already exists at $KEYOUTPUT_PATH"
else
  mkdir ${parent_dir}/secrets > /dev/null 2>&1
  gcloud iam service-accounts keys create $KEYOUTPUT_PATH \
    --project=$GCP_PROJECT \
    --iam-account="${SERVICEACC_NAME}@${GCP_PROJECT}.iam.gserviceaccount.com"
fi

# Configure GCS bucket for Terraform backend
gcloud storage buckets create gs://${GCS_TFBACKEND_BKT_NAME} \
  --project=$GCP_PROJECT \
  --default-storage-class="standard" \
  --location=$GCS_BKT_LOCATION \
  --public-access-prevention \
  --uniform-bucket-level-access

# Enable object versioning for Terraform state
gcloud storage buckets update gs://${GCS_TFBACKEND_BKT_NAME} \
  --project=$GCP_PROJECT \
  --versioning
