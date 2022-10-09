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

resource "google_project_iam_member" "batch" {
  for_each = toset(var.service_account_roles.batch)

  project = local.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.batch.email}"
}

resource "google_service_account_iam_member" "batch_account_iam" {
  service_account_id = google_service_account.batch.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${local.terraform_sa_name}@${local.project}.iam.gserviceaccount.com"
}

resource "google_project_service" "iam" {
  service = "iam.googleapis.com"

  timeouts {
    create = "30m"
    update = "40m"
  }
}
