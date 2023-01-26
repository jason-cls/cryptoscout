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
  temp_bucket  = "temp-${var.project}"
  deps_bucket  = "deps-${var.project}"

  # Project service account IAM roles
  service_acc_project_roles = {
    batch = ["roles/storage.objectAdmin"]
    airflow = [
      "roles/storage.objectViewer",
      "roles/run.invoker",
      "roles/dataproc.editor"
    ]
    dataproc = ["roles/dataproc.worker"]
  }

  # APIs to enable in GCP
  gcp_apis = [
    "iam.googleapis.com",
    "storage.googleapis.com",
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "run.googleapis.com",
    "dataproc.googleapis.com"
  ]
}

data "local_sensitive_file" "coincap_key" {
  filename = "${local.secrets_dir}/coincap-api-key.txt"
}
