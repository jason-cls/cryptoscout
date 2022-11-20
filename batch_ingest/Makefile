build-img:
	@echo "Building docker image..."
	docker build . -t cryptoscout-batch-ingest-api

local-container:
	@echo "Running docker container..."
	docker run -d --rm \
		-p 8080:8080 \
		--env-file ./src/batch_ingest/.env \
		--env GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/batch-sa-key.json \
		-v "$(shell pwd)/src/batch_ingest/.secrets/batch-sa-key.json:/tmp/keys/batch-sa-key.json:ro" \
		--name cryptoscout-batchingestor \
		cryptoscout-batch-ingest-api

test:
	python -m pytest