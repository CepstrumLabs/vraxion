FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip

COPY src/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN apk del --no-cache .build-deps

RUN mkdir -p /src
COPY src/ /src/
WORKDIR /src
RUN python setup.py build_ext
RUN python setup.py install
COPY tests/ /tests/

EXPOSE 8000

WORKDIR /src
