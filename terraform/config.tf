terraform {
  backend "gcs" {
    bucket      = "terraform-backend-cs"
    prefix      = "terraform/state"
    credentials = "./secrets/terraform-sa-key.json"
  }
}

locals {
  # Store sensitive data locally
  secrets_dir = "${path.root}/secrets"
  credentials = "${local.secrets_dir}/terraform-sa-key.json"

  # GCS buckets
  raw_bucket   = "raw-${var.project}"
  stage_bucket = "stage-${var.project}"

  # Project service account IAM roles
  service_acc_project_roles = {
    batch = ["roles/storage.objectAdmin"]
  }

  # APIs to enable in GCP
  gcp_apis = [
    "iam.googleapis.com",
    "storage.googleapis.com"
  ]
}
