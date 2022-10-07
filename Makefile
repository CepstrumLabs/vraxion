build:
	docker build -t vraxion_dev .

test: build
	docker run --rm vraxion_dev pytest -s  /tests

serve: build
	docker run --rm -p 8000:8000 vraxion_dev gunicorn -b 0.0.0.0:8000 vraxion.app:app

pyclean:
	rm -rf src/build src/dist

pypublish:
	cd src && \
	python3 setup.py sdist bdist_wheel && \
	twine check dist/* && \
	twine upload  --skip-existing -u ${TWINE_USERNAME} dist/*

all: test pypublish pyclean
