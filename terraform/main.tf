terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.39.0"
    }
  }
}

provider "google" {
  project = local.project
  region  = local.region
  zone    = local.zone

  credentials = local.credentials
}

resource "google_service_account" "batch" {
  account_id   = var.batch_service_account_id
  display_name = "Batch Ingestor"
  description  = "Executes batch ingestion jobs"
}

resource "google_project_iam_member" "object_admin" {
  project = local.project
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.batch.email}"
}

resource "google_project_service" "iam" {
  service = "iam.googleapis.com"

  timeouts {
    create = "30m"
    update = "40m"
  }
}
