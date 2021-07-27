build:
	docker build -t vraxion_dev .

test: build
	docker run -ti vraxion_dev pytest /tests

all: test