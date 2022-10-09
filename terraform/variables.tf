variable "batch_service_account_id" {
  description = "The account id that is used to generate the service account email address and a stable unique id."
  type        = string
  default     = "batch-ingestor"
}