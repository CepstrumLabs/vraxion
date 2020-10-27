from webob import Request, Response
from functools import wraps


class Api:

    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request=request)
        return response(environ, start_response)

    def handle_request(self, request):
        response = Response()
        try:
            handler = self.routes[request.path]
            handler(request, response)
        except KeyError:
            response.status = 404
        finally:
            return response

    def route(self, path):   
        # @wraps(handler)
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper
