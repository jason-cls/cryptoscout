terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.39.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.2.3"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone

  credentials = local.credentials
}

resource "google_service_account" "batch" {
  account_id   = var.batch_service_account_id
  display_name = "Batch Ingestor"
  description  = "Executes batch ingestion jobs"
}

resource "google_service_account_key" "batch" {
  service_account_id = google_service_account.batch.id
}

resource "local_sensitive_file" "batch_service_account_key" {
  filename        = "${local.secrets_dir}/batch-sa-key.json"
  content         = base64decode(google_service_account_key.batch.private_key)
  file_permission = "0444"
}

resource "google_project_iam_member" "batch" {
  for_each = toset(local.service_acc_project_roles.batch)

  project = var.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.batch.email}"
}

resource "google_service_account_iam_member" "batch_account_iam" {
  service_account_id = google_service_account.batch.name

  role   = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${var.terraform_service_account_id}@${var.project}.iam.gserviceaccount.com"
}

resource "google_project_service" "api" {
  for_each = toset(local.gcp_apis)

  service = each.value

  timeouts {
    create = "30m"
    update = "40m"
  }
}

resource "google_storage_bucket" "raw" {
  name          = local.raw_bucket
  location      = var.region
  force_destroy = false

  versioning {
    enabled = true
  }
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 30
    }
  }
}

resource "google_storage_bucket" "stage" {
  name          = local.stage_bucket
  location      = var.region
  force_destroy = false
}
