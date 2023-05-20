# Terraform & Project Configuration & Deployment
## Initial Setup
To allow Terraform to interact with a new GCP project, the following needs to be done:
- Create GCP service account credentials used by Terraform
- Create a GCS bucket to store Terraform remote state
- Enable GCP APIs to interface with Terraform

The convenience script [`setup-gcp.sh`](setup_scripts/setup-gcp.sh) has been prepared to handle these setup steps. Since GCP project ids and GCS buckets require globally unique names, you'll likely need to change variables `GCP_PROJECT` and `GCS_TFBACKEND_BKT_NAME` at the top of the script.

Additionally, the project requires the following:
- An encryption key for the Terraform GCS backend
- SSH key credentials used by Terraform to provision Cloud Compute VMs
- Initialization of the Terraform backend

To execute all the initial setup steps:
1. In gcloud CLI, log in and set the current user to the owner of the newly created GCP project.
2. In the current directory, run:
    ```bash
    make tf-setup
    ```
    This will create sensitive keys in the `./secrets` directory.

## Creating Infrastructure
**WARNING: You will be charged for setting up infrastructure on GCP.**

First, make sure the `GCS_TFBACKEND_BKT_NAME` value selected in the prior section matches the `terraform.backend.gcs.bucket` value defined in the [terraform config file](config.tf).

Before creating infrastructure, create a `terraform.tfvars` file in the current directory with the following content:

```
project         = "<gcp_project_id>"
coincap_api_key = "<key_value>"
local_ip_cidr   = "<your_ipv4_cidr_range>"
```

A CoinCap API key can be requested [here](https://coincap.io/api-key). The local ip is used to create a firewall rule allowing external ingress to the Airflow webserver.

To create GCP infrastructure, in a terminal run:
```bash
terraform apply
```

***Note:*** *During first-time execution, Terraform will fail to deploy the Cloud Run service (and other resources dependant) because the referenced Docker image is not yet uploaded to Artifact Registry. After Terraform throws an error, follow the steps [here](../batch_ingest/README.md#pushing-the-image-to-gcp-artifact-registry) to build and upload the image to Artifact Registry before rerunning `terraform apply`.*

## Cleaning Up
To tear down all GCP infrastructure, in a terminal run:
```bash
terraform destroy
```

Individual resources can be deleted by specifying the `-target` flag:
```bash
terraform destroy -target <RESOURCE_TYPE>.<NAME>
```

## Local Dev Environment Config
After successfully running `terraform apply`, the `./secrets` directory will have multiple service account keys and `.env` files created. To execute and test services locally, these files need to be distributed to the appropriate project directories.

Run the following command which calls [this helper script](setup_scripts/config-dev-credentials.sh) to copy the files to the necessary directories:

```bash
make dev-creds
```
