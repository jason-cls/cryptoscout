variable "batch_service_account_id" {
  description = "The account id that is used to generate the service account email address and a stable unique id."
  type        = string
  default     = "batch-ingestor"
}

variable "service_account_roles" {
  description = "Defines a mapping of service accounts to their IAM roles."
  type = object({
    batch = list(string)
  })
  default = {
    batch = ["roles/storage.objectAdmin"]
  }
}
