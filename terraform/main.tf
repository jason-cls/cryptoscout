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

resource "google_project_service" "api" {
  for_each = toset(local.gcp_apis)

  service            = each.value
  disable_on_destroy = false

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

resource "google_storage_bucket" "temp" {
  name          = local.temp_bucket
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket" "dependencies" {
  name          = local.deps_bucket
  location      = var.region
  force_destroy = false
}

resource "google_storage_bucket_object" "pyspark_deps" {
  for_each = fileset("${path.root}/../spark_batch/src/spark_batch/", "*.py")

  name   = "dependencies/spark_batch/${each.value}"
  bucket = google_storage_bucket.dependencies.name
  source = "${path.root}/../spark_batch/src/spark_batch/${each.value}"
}

resource "google_artifact_registry_repository" "docker" {
  repository_id = var.repository
  format        = "DOCKER"
  location      = var.region
  description   = "Docker repository"
}

resource "google_cloud_run_service" "batch_ingest_api" {
  name     = "cryptoscout-batchingestor"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project}/${var.repository}/${var.batchingest_image}"
        env {
          name  = "COINCAP_API_KEY"
          value = data.local_sensitive_file.coincap_key.content
        }
      }
      container_concurrency = 0
      timeout_seconds       = 1800
      service_account_name  = google_service_account.batch.email
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }
}
