import logging
from webob import Request
import json

logger = logging.getLogger("vraxion.log")


class Middleware:
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.app.handle_request(request)
        return response(environ, start_response)

    def add(self, middleware_cls):
        self.app = middleware_cls(self.app)
    
    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def handle_request(self, request):
        self.process_request(request)
        response = self.app.handle_request(request)
        self.process_response(request, response)
        return response


class LogMiddleware(Middleware):
    """
    A logger to help for debugging
    """
    LOG_MESSAGE_FMT = "{method} {url} {body}"
    
    def process_request(self, request):
        body = json.loads(request.body.decode()) if request.body else None
        logger.debug(msg=self.LOG_MESSAGE_FMT.format(method=request.method, url=request.url, body=body))

        