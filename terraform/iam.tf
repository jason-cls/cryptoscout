# -- SERVICE ACCOUNTS --
resource "google_service_account" "airflow" {
  account_id   = var.airflow_service_account_id
  display_name = "Airflow"
  description  = "Allows Airflow interaction with other GCP services"
}

resource "google_service_account" "batch" {
  account_id   = var.batch_service_account_id
  display_name = "Batch Ingestor"
  description  = "Executes batch ingestion jobs"
}

resource "google_service_account" "dataproc" {
  account_id   = var.dataproc_service_account_id
  display_name = "Dataproc Worker"
  description  = "Associated with VMs which run Dataproc workloads"
}


# -- PRIVATE KEYS --
resource "google_service_account_key" "airflow" {
  service_account_id = google_service_account.airflow.id
}

resource "google_service_account_key" "batch" {
  service_account_id = google_service_account.batch.id
}

resource "google_service_account_key" "dataproc" {
  service_account_id = google_service_account.dataproc.id
}

resource "local_sensitive_file" "airflow_service_account_key" {
  filename        = "${local.secrets_dir}/airflow-sa-key.json"
  content         = base64decode(google_service_account_key.airflow.private_key)
  file_permission = "0444"
}

resource "local_sensitive_file" "batch_service_account_key" {
  filename        = "${local.secrets_dir}/batch-sa-key.json"
  content         = base64decode(google_service_account_key.batch.private_key)
  file_permission = "0444"
}

resource "local_sensitive_file" "dataproc_service_account_key" {
  filename        = "${local.secrets_dir}/dataproc-sa-key.json"
  content         = base64decode(google_service_account_key.dataproc.private_key)
  file_permission = "0444"
}


# -- IAM --
resource "google_project_iam_member" "airflow" {
  for_each = toset(local.service_acc_project_roles.airflow)

  project = var.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.airflow.email}"
}

resource "google_project_iam_member" "batch" {
  for_each = toset(local.service_acc_project_roles.batch)

  project = var.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.batch.email}"
}

resource "google_project_iam_member" "dataproc" {
  for_each = toset(local.service_acc_project_roles.dataproc)

  project = var.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.dataproc.email}"
}

resource "google_service_account_iam_member" "airflow_account_iam" {
  service_account_id = google_service_account.airflow.name

  role   = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${var.terraform_service_account_id}@${var.project}.iam.gserviceaccount.com"
}

resource "google_service_account_iam_member" "batch_account_iam" {
  service_account_id = google_service_account.batch.name

  role   = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${var.terraform_service_account_id}@${var.project}.iam.gserviceaccount.com"
}

resource "google_service_account_iam_member" "dataproc_account_iam" {
  for_each = toset([
    var.terraform_service_account_id,
    var.dataproc_service_account_id
  ])

  service_account_id = google_service_account.dataproc.name

  role   = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${each.key}@${var.project}.iam.gserviceaccount.com"
}
