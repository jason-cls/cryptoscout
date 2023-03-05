AIRFLOW_UID := $(shell id -u)

airflow-init:
	echo "AIRFLOW_UID=$(AIRFLOW_UID)" > .env
	docker compose up --build airflow-init

up:
	docker compose up -d --build

down:
	docker compose down --remove-orphans

dev-env:
	./install/pip-airflow-constrain.sh

dev-requirements: dev-env
	python -m pip freeze > dev-requirements.txt