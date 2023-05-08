tf-setup: gcp-prep backend-encryptionkey tf-init ssh-key

tf-init:
	terraform init -backend-config=./secrets/encryptionkey.gcs.tfbackend

gcp-prep:
	./setup_scripts/setup-gcp.sh

backend-encryptionkey:
	./setup_scripts/gen-encryptkey.sh

ssh-key:
	ssh-keygen -t rsa -f ./secrets/tf-ssh-key -C terraform -b 2048 -N ''

dev-creds:
	./setup_scripts/config-dev-credentials.sh
