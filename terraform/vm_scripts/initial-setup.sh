#! /usr/bin/env bash

# First time provisioning script

set -eou pipefail

TARGET_CLONE_DIR=/opt

# Setup apt repository
sudo apt-get update
sudo apt-get -y install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install software packages
sudo apt-get update
sudo apt-get -y install git make docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Setup Docker without sudo for future logins
echo "Docker setup without sudo..."
sudo groupadd -f docker
sudo usermod -aG docker $USER

# Clone git repo
echo "Cloning cryptoscout repo..."
cd "$TARGET_CLONE_DIR"
sudo git clone https://github.com/jason-cls/cryptoscout.git
sudo chmod -R 777 "${TARGET_CLONE_DIR}/cryptoscout/"

# Place provisioned files into cloned directory
echo "Moving provisioned files..."
mv /tmp/dbt-sa-key.json "${TARGET_CLONE_DIR}/cryptoscout/dbt/cryptoscout/.secrets/"
mv /tmp/req.env "${TARGET_CLONE_DIR}/cryptoscout/airflow/"

# Initialize + start airflow
echo "Starting airflow..."
cd "${TARGET_CLONE_DIR}/cryptoscout/airflow/"
sudo make airflow-init
sudo make up
