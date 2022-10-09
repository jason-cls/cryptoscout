tf-setup: gcp-prep backend-encryptionkey tf-init

tf-init:
	terraform init -backend-config=./secrets/encryptionkey.gcs.tfbackend

gcp-prep:
	./setup_scripts/setup-gcp.sh

backend-encryptionkey:
	./setup_scripts/gen-encryptkey.sh
