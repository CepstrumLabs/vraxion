FROM python:3.8-alpine

RUN apk add --no-cache bash
RUN apk add --no-cache gcc
RUN apk add --no-cache g++
RUN apk add --no-cache musl-dev
RUN apk add --no-cache --virtual .build-deps python3-dev
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
