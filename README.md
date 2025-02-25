# Vraxion: Python Web Framework

![purpose](https://img.shields.io/badge/purpose-learning-green.svg)
![PyPI](https://img.shields.io/pypi/v/vraxion.svg)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/vraxion)
![Build](https://github.com/michael-karotsieris/vraxion/actions/workflows/build.yml/badge.svg)
![PyPI - License](https://img.shields.io/pypi/l/vraxion)


vraxion is a Python web framework.
It's a WSGI framework and can be used with any WSGI application server such as Gunicorn.

## Installation

```shell
pip install vraxion
```

## Usage

```python

# Define an API route

from vraxion.api import Api

api = Api()

@api.route(path="/resource/")
def get_resource(request, response):
    response.json = {"text": "Hello"}

```