variable "project" {
  description = "The default GCP project to manage resources in."
  type        = string
  default     = "cryptoscout"
}

variable "region" {
  description = "The default region to manage resources in."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The default zone to manage resources in."
  type        = string
  default     = "us-central1-b"
}

variable "terraform_service_account_id" {
  description = "The id of the service account Terraform will use."
  type        = string
  default     = "terraform"
}

variable "batch_service_account_id" {
  description = "The id of the service account used for batch ingestion."
  type        = string
  default     = "batch-ingestor"
}

variable "repository" {
  description = "The id of the Artifact Registry repository to create."
  type        = string
  default     = "docker-repo"
}

variable "batchingest_image" {
  description = "The name of the Docker image in the Artifact Registry repository to be deployed on Cloud Run as a batch ingestion service."
  type        = string
  default     = "batch-ingest-api"
}
