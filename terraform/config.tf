locals {
  credentials = "${path.root}/secrets/terraform-sa-key.json"
  project     = "cryptoscout"
  region      = "us-central1"
  zone        = "us-central1-b"

  terraform_sa_name = "terraform"
}

terraform {
  backend "gcs" {
    bucket      = "terraform-backend-cs"
    prefix      = "terraform/state"
    credentials = "./secrets/terraform-sa-key.json"
  }
}
