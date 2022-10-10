output "storage_bucket_raw_url" {
  description = "The URL of the raw storage bucket."
  value       = google_storage_bucket.raw.url
}

output "storage_bucket_stage_url" {
  description = "The URL of the stage storage bucket."
  value       = google_storage_bucket.stage.url
}
