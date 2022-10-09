terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.39.0"
    }
  }
}

provider "google" {
  project = "cryptoscout"
  region  = local.region
  zone    = local.zone

  credentials = local.credentials
}