# Batch Ingestion: REST API service
Data ingestion of different sources to the raw zone of the data lake is facilitated by API calls made to the batch ingestion service. Data contracts are used to validate ingested data schema.

## Running the service locally
To deploy a local instance of the service in a Docker container, first, build the image from the Dockerfile. In the current directory execute:
```bash
make build-img
```
To run the container from the built image, execute:
```bash
make local-container
```
**Note**: running the container requires `.env` and a valid GCP service account keyfile `batch-sa-key.json`. Refer to the [*Local Dev Environment Config* section of the Terraform README](../terraform/README.md#local-dev-environment-config) for details.

Once the container is running, API calls can be made to the exposed port at http://localhost:8080/

## Pushing the image to GCP Artifact Registry
A prerequisite to [deploying the containerized service on Cloud Run](https://cloud.google.com/run/docs/deploying) is adding the image to an Artifact Registry repository. After building the image locally via ```make build-img```:

1. [Configure Docker authentication via gcloud](https://cloud.google.com/artifact-registry/docs/docker/store-docker-container-images#auth)
    ```bash
    make docker-auth-config
    ```
2. [Tag the image with a registry name](https://cloud.google.com/artifact-registry/docs/docker/store-docker-container-images#tag)
    ```bash
    make docker-tag
    ```
3. [Push the image to Artifact Registry](https://cloud.google.com/artifact-registry/docs/docker/store-docker-container-images#push)
    ```bash
    make docker-push-artifactregistry
    ```
**Note**: The steps above assume a GCP project id of `cryptoscout`; this may need to be changed.