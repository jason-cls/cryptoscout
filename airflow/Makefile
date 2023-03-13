AIRFLOW_UID := $(shell id -u)

airflow-init:
	@echo "Initializing Airflow..."
	echo "AIRFLOW_UID=$(AIRFLOW_UID)" > .env
	set -a && . ./.env && . ./req.env && set +a && \
	docker compose up --build airflow-init

up:
	@echo "Starting Airflow in detached mode..."
	set -a && . ./.env && . ./req.env && set +a && \
	docker compose up -d --build

down:
	@echo "Stopping Airflow..."
	set -a && . ./.env && . ./req.env && set +a && \
	docker compose down --remove-orphans

dev-env:
	@echo "Installing Airflow into current local Python environment"
	./install/pip-airflow-constrain.sh

dev-requirements: dev-env
	@echo "Building dev-requirements.txt from local Python environment"
	python -m pip freeze > dev-requirements.txt