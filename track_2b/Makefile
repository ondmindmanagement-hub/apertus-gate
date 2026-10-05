.PHONY: run test build

IMAGE ?= apertus-gate
PORT ?= 8787

build:
	docker build -f Dockerfile -t $(IMAGE) ../..

run:
	docker build -f Dockerfile -t $(IMAGE) ../..
	docker run --rm -p $(PORT):8787 \
		-e APERTUS_API_KEY \
		-e APERTUS_API_URL \
		-e APERTUS_MODEL \
		$(IMAGE)

test:
	python3 -m unittest discover -s tests -v
