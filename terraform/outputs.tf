resource "local_sensitive_file" "airflow_req_dotenv" {
  filename        = "${local.secrets_dir}/airflow-req.env"
  file_permission = "0777"
  content         = <<-EOT
  CLOUD_RUN_BATCHINGEST_URL=${google_cloud_run_service.batch_ingest_api.status.0.url}
  GCP_PROJECT_ID=${var.project}
  GCS_RAW_BUCKET=${google_storage_bucket.raw.name}
  GCS_STAGE_BUCKET=${google_storage_bucket.stage.name}
  GCS_DEPS_BUCKET=${google_storage_bucket.dependencies.name}
  DATAPROC_REGION=${var.region}
  DATAPROC_SERVICEACCOUNT=${google_service_account.dataproc.email}
  DATAPROC_SUBNET_URI=${google_compute_subnetwork.vm_subnet.self_link}
  EOT
}

resource "local_sensitive_file" "batchingest_dotenv" {
  filename        = "${local.secrets_dir}/batchingest.env"
  file_permission = "0777"
  content         = <<-EOT
  COINCAP_API_KEY=${var.coincap_api_key}
  GOOGLE_APPLICATION_CREDENTIALS=./.secrets/batch-sa-key.json
  EOT
}

output "storage_bucket_raw_url" {
  description = "The URL of the raw storage bucket."
  value       = google_storage_bucket.raw.url
}

output "storage_bucket_stage_url" {
  description = "The URL of the stage storage bucket."
  value       = google_storage_bucket.stage.url
}

output "storage_bucket_dependencies_url" {
  description = "The URL of the dependencies storage bucket."
  value       = google_storage_bucket.dependencies.url
}

output "artifact_registry_repository_id" {
  description = "ID of the repository in Artifact Registry."
  value       = google_artifact_registry_repository.docker.id
}

output "cloud_run_service_batchingestor_url" {
  description = "URL of the batch ingest Cloud Run service."
  value       = google_cloud_run_service.batch_ingest_api.status.0.url
}

output "compute_network_vpc_id" {
  description = "ID of the created VPC network."
  value       = google_compute_network.vpc.id
}

output "compute_subnetwork_vm_subnet_id" {
  description = "ID of the created subnetwork in the VPC network."
  value       = google_compute_subnetwork.vm_subnet.id
}

output "compute_instance_airflow_vm_external_ip" {
  description = "External IP of the Airflow VM."
  value       = google_compute_instance.airflow_vm.network_interface.0.access_config.0.nat_ip
}
