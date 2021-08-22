build:
	docker build --rm -t vraxion_dev .

test: build
	docker run --rm --it vraxion_dev pytest -s /tests

serve: build
	docker run --rm -p 8000:8000 vraxion_dev gunicorn -b 0.0.0.0:8000 vraxion.app:app

pyclean:
	rm -rf src/build src/dist

all: test
