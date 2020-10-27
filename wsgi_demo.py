
from typing import Callable
from wsgiref.simple_server import make_server

def application(environ: dict, start_response: Callable):
    response_body = [f"{key}: {value}" for key, value in sorted(environ.items())]
    response_body = "\n".join(response_body)
    status = "200 OK"
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [response_body.encode('utf-8')]


server = make_server('localhost', 8000, app=application)
server.serve_forever()