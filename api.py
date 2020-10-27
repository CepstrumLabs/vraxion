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
        for path, handler in self.routes.items(): 
            if path == request.path:
                handler(request, response)
        self.default_response(response)
        return response

    def default_response(self, response):
        response.status_code = 404
        response.text = 'Sorry mate, page not found'

    def route(self, path):   
        # @wraps(handler)
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper
