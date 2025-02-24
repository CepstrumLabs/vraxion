.PHONY: build test serve pyclean pypublish help

# Default target when just running 'make'
.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo "  build     - Build Docker image for development"
	@echo "  test      - Run tests in Docker container"
	@echo "  serve     - Start development server"
	@echo "  pyclean   - Clean Python build artifacts"
	@echo "  pypublish - Publish package to PyPI"

build:
	docker build -t vraxion_dev .

test: build
	docker run --rm vraxion_dev pytest -svvv /tests

serve: build
	docker run --rm -p 8000:8000 vraxion_dev gunicorn -b 0.0.0.0:8000 vraxion.app:app

pyclean:
	rm -rf src/build src/dist

pypublish: test
	@if [ -z "$(TWINE_USERNAME)" ]; then \
		echo "Error: TWINE_USERNAME is not set"; \
		exit 1; \
	fi
	cd src && \
	python3 setup.py sdist bdist_wheel && \
	twine check dist/* && \
	twine upload --skip-existing -u $(TWINE_USERNAME) dist/*

