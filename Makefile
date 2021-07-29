build:
	docker build -t vraxion_dev .

test: build
	docker run -ti vraxion_dev pytest /tests  --cov=/tests

serve: build
	docker run -ti -p 8000:8000 vraxion_dev gunicorn -b 0.0.0.0:8000 vraxion.app:app

all: test