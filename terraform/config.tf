locals {
  project = "cryptoscout"
  region  = "us-central1"
  zone    = "us-central1-b"

  terraform_sa_name = "terraform"
  secrets_dir       = "${path.root}/secrets"
  credentials       = "${local.secrets_dir}/terraform-sa-key.json"
}

terraform {
  backend "gcs" {
    bucket      = "terraform-backend-cs"
    prefix      = "terraform/state"
    credentials = "./secrets/terraform-sa-key.json"
  }
}
