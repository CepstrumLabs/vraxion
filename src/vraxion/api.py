import inspect
import os
import logging

from webob import Request
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWsgiAdapter
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise
import parse

from vraxion.middleware import Middleware
from vraxion.response import Response

ALLOWED_METHODS = ["get", "post", "put", "patch", "delete", "options"]

logger = logging.getLogger(__name__)

class Api:
    def __init__(self, templates_dir="templates", static_dir="static/"):
        logger.info(f"Using {templates_dir} as a template directory")
        logger.info(f"Using {static_dir} as a static directory")
        self.routes = {}
        self.exception_handler = None
        self._template_env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))
        self.middleware = Middleware(self)
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

    def __call__(self, environ, start_response):
        pathinfo = environ["PATH_INFO"]
        if pathinfo.startswith("/static"):
            environ["PATH_INFO"] = pathinfo[len("/static"):]
            return self.whitenoise(environ, start_response)
        return self.middleware(environ, start_response)
    
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request=request)
        return response(environ, start_response)

    def find_handler(self, request_path):
        for path, handler_data in self.routes.items(): 
            parsed_result = parse.parse(path, request_path)
            if parsed_result:
                return handler_data, parsed_result.named
        return None, None

    def handle_request(self, request):
        response = Response()
        handler_data, kwargs = self.find_handler(request_path=request.path)
        request_method = request.method.lower()
        handler = handler_data.get("handler") if handler_data is not None else None
        allowed_methods = handler_data.get("allowed_methods") if handler_data is not None else None
        if handler is not None:
            if inspect.isclass(handler):
                handler = getattr(handler(), request_method, None)
                if handler is None:
                    raise AttributeError(f"method {request_method} not allowed")
            try:
                if request_method not in allowed_methods:
                    raise AttributeError(f"method {request_method} not allowed")
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

    def route(self, path, allowed_methods=ALLOWED_METHODS):   
        def wrapper(handler):
            self.add_route(path=path, handler=handler, allowed_methods=allowed_methods)
            return handler
        return wrapper

    def add_route(self, path, handler, allowed_methods=ALLOWED_METHODS):
        assert not path in self.routes, f"Route {path} already exists"
        self.routes[path] = {"handler": handler, "allowed_methods": allowed_methods}

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

    def add_middleware(self, middleware):
        self.middleware.add(middleware)