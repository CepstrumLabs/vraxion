from functools import wraps
import inspect

from webob import Request, Response
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWsgiAdapter
import parse


class Api:

    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request=request)
        return response(environ, start_response)

    def find_handler(self, request_path):
        for path, handler in self.routes.items(): 
            parsed_result = parse.parse(path, request_path)
            if parsed_result:
                return handler, parsed_result.named
        return None, None

    def handle_request(self, request):
        response = Response()
        handler, kwargs = self.find_handler(request_path=request.path)
        if handler is not None:
            if inspect.isclass(handler):
                handler = getattr(handler(), request.method.lower(), None)
                if handler is None:
                    raise AttributeError(f"method {request.method.lower()} not allowed")
            handler(request, response, **kwargs)
        else:
            self.default_response(response)
        return response

    def default_response(self, response):
        response.status_code = 404
        response.text = 'Sorry mate, page not found'

    def route(self, path):   
        assert not path in self.routes, f"Route {path} already exists"

        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper

    def test_session(self, base_url="http://testserver.com"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWsgiAdapter(self))
        return session
