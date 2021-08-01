build:
	docker build --rm -t vraxion_dev .

test: build
	docker run --rm -ti vraxion_dev pytest -s /tests

serve: build
	docker run --rm -ti -p 8000:8000 vraxion_dev gunicorn -b 0.0.0.0:8000 vraxion.app:app

all: test