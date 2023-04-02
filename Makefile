pipx-devtools: install-pipx
	chmod +x ./dev-tools/install_pipx_pkgs.sh
	./dev-tools/install_pipx_pkgs.sh

install-pipx:
	python3 -m pip install --user pipx
	python3 -m pipx ensurepath

format:
	isort .
	black -l 88 --preview .
	sqlfluff fix ./dbt/ --dialect=bigquery --force

type:
	mypy --ignore-missing-imports .

lint:
	flake8 .
	sqlfluff lint ./dbt/ --dialect=bigquery

ci:	format type lint
