from functools import wraps
import inspect
import os 

from webob import Request, Response
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWsgiAdapter
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise
import parse



class Api:
    def __init__(self, templates_dir="templates", static_dir="static/"):
        self.routes = {}
        self.exception_handler = None
        self._template_env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

    def __call__(self, environ, start_response):
        return self.whitenoise(environ, start_response)
    
    def wsgi_app(self, environ, start_response):
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
            try:
                handler(request, response, **kwargs)
            except Exception as e:
                if self.exception_handler is None:
                    raise e
                self.exception_handler(request, response, e)
        else:
            self.default_response(response)
        return response

    def default_response(self, response):
        response.status_code = 404
        response.text = 'Sorry mate, page not found'

    def route(self, path):   
        def wrapper(handler):
            self.add_route(path=path, handler=handler)
            return handler
        return wrapper

    def add_route(self, path, handler):
        assert not path in self.routes, f"Route {path} already exists"
        self.routes[path] = handler

    def test_session(self, base_url="http://testserver.com"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWsgiAdapter(self))
        return session

    def template(self, template_name, context=None):
        if context is None:
            context = {}
        return self._template_env.get_template(template_name).render(**context)

    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler
