import logging
import pytest

from vraxion.api import Api
from vraxion.middleware import Middleware, LogMiddleware

logger = logging.getLogger("vraxion")
def test_basic_route_adding(api):
    """
    Ensure that we can create a basic route
    """

    @api.route('/home', method='get')
    def home(req, resp):
        resp.text = 'home'

    @api.route('/home/{name}', method='get')
    def with_param(req, resp):
        resp.text = 'with_param'

    @api.route('/',method='get')
    def index(req, resp):
        resp.text = 'index'


def test_does_not_allow_duplicate_routes(api):
    """
    Ensure that we don't allow duplicate routes
    """

    @api.route('/home', method='get')
    def home(req, resp):
        resp.text = 'Home'

    with pytest.raises(AssertionError):
        @api.route('/home', method='get')
        def home_2(req, resp):
            resp.text = 'Home'


def test_basic_route_response_get(api, client):
    
    response_text = 'home'
    @api.route('/home', method='get')
    def home(req, resp):
        resp.text = response_text
    
    assert client.get("http://testserver.com/home").text ==  response_text


def test_basic_route_with_query_param_response_get(api, client):
    
    response_text = 'home'
    name = 'test_name'
    @api.route('/home/{name}', method='get')
    def home(req, resp, name):
        resp.text = response_text + name
    
    assert client.get(f"http://testserver.com/home/{name}").text ==  response_text + name


def test_default_404_response(client):
        
    response = client.get("http://testserver.com/doesnotexist")

    assert response.status_code == 404
    assert response.text == "Sorry mate, page not found"


@pytest.mark.skip(reason="Changes in class based handlers")
def test_class_based_handler_get(api, client):
    
    response_text = 'get'

    @api.route('/book')
    class BookResource:
        def get(self, req, resp):
            resp.text = response_text

    response = client.get("http://testserver.com/book")
    assert response.text == response_text

@pytest.mark.skip("Changes in class based handlers")
def test_class_based_handler_post(api, client):
    
    response_text = 'post'
    
    @api.route('/book')
    class BookResource:
        def post(self, req, resp):
            resp.text = response_text

    response = client.post("http://testserver.com/book")
    assert response.text == response_text

@pytest.mark.skip("Changes in class based handlers")
def test_class_based_handler_not_allowed(api, client):

    @api.route('/book')
    class BookResource:
        def post(self, req, resp):
            resp.text = 'hey'

    with pytest.raises(AttributeError):
        client.get("http://testserver.com/book")

def test_add_route(api, client):
    """
    Ensure basic functionality of Api.add_route
    Assert that a function - handler - can be 
    added to routes using add_route
    """
    response_text = "Handler response"
    
    def handler(req, resp):
        resp.text = response_text
        return resp

    api.add_route("/handler", 'get', handler)

    response = client.get("http://testserver.com/handler")
    assert response.text == response_text

@pytest.mark.skip(reason="Changes in class based handlers")
def test_add_route_with_class(api, client):
    """
    Ensure basic functionality of Api.add_route
    Assert that a function - handler - can be 
    added to routes using add_route
    """
    response_text = "Handler response"
    
    class Resource:

        def get(self, req, resp):
            resp.text = response_text
            return resp

    api.add_route("/books", Resource)
    response = client.get("http://testserver.com/books")
    assert response.text == response_text


def test_template(client):
    """
    Ensure basic functionality of Api.add_route
    Assert that a function - handler - can be 
    added to routes using add_route
    """
    title = "Awesome Test"
    name="test_template"
    
    api = Api(templates_dir="/tests/templates")
    
    @api.route("/html", method='get')
    def handler(req, resp):
        resp.body = api.template("about.html", context={"title": title, "name": name})
        return resp

    client = api.test_session()
    response = client.get("http://testserver.com/html")

    assert "text/html" in response.headers["Content-Type"]
    assert title in response.text
    assert name in response.text


def test_custom_exception_handler(api, client):

    def on_exception(req, resp, exc):
        resp.text = "AttributeErrorHappend"

    api.add_exception_handler(on_exception)

    @api.route("/home", method='get')
    def home(req, resp):
        raise AttributeError()

    response = client.get("http://testserver.com/home")
    assert response.text == "AttributeErrorHappend"


def test_404_is_returned_for_nonexistent_static_file(client):
    assert client.get(f"http://testserver.com/static/main.css)").status_code == 404


def test_200_is_returned_for_existing_static_files(api, tmpdir_factory):

    FILE_DIR = "css"
    FILE_NAME = "main.css"
    FILE_CONTENTS = "body {background-color: red}"


    def _create_static_file(static_dir):
        asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
        asset.write(FILE_CONTENTS)

    static_dir = tmpdir_factory.mktemp("static")
    _create_static_file(static_dir)
    api = Api(static_dir=str(static_dir))
    client = api.test_session()
    
    response = client.get(f"http://testserver.com/static/{FILE_DIR}/{FILE_NAME}")
    
    assert response.status_code == 200
    assert FILE_CONTENTS in response.text


def test_can_add_middleware(api, client):

    process_request_called = False
    process_response_called = False

    class CallMiddleWareMethods(Middleware):
        
        def __init__(self, app):
            super().__init__(app)
            self.app = app

        def process_request(self, request):
            nonlocal process_request_called
            process_request_called = True

        def process_response(self, request, response):
            nonlocal process_response_called
            process_response_called = True

    api.add_middleware(CallMiddleWareMethods)
    
    @api.route('/', method='get')
    def index(req, res):
        res.text = "YOLO"

    client.get('http://testserver.com/')

    assert process_request_called == True    
    assert process_response_called == True


def test_allowed_methods(api, client):

    @api.route("/about", method='get')
    def about(request, response):
        response.text = "Hey"
    
    url = "http://testserver.com/about"
    with pytest.raises(AttributeError):
        client.post(url, data={})
    
    assert client.get(url).status_code == 200
    assert client.get(url).content == b"Hey"

def test_text_with_custom_response_class(api, client):
    
    @api.route("/about", 'get', allowed_methods=['get'])
    def about(request, response):
        response.text = "Hey"
    
    response = client.get("http://testserver.com/about")
    
    assert response.status_code == 200
    assert "Hey" in response.text
    
def test_json_response_helper(api, client):
    @api.route("/json", 'get')
    def json_handler(req, resp):
        resp.json = {"name": "vraxion"}

    response = client.get("http://testserver.com/json")
    json_body = response.json()

    assert response.headers["Content-Type"] == "application/json"
    assert json_body["name"] == "vraxion"

def test_html_response_helper(api, client):
    @api.route("/html", 'get')
    def html_handler(req, resp):
        resp.html = api.template("about.html", context={"title": "Best Title", "name": "Best Name"})

    response = client.get("http://testserver.com/html")

    assert "text/html" in response.headers["Content-Type"]
    assert "Best Title" in response.text
    assert "Best Name" in response.text

def test_same_route_different_method(api, client):
    
    base_url = "http://testserver.com"

    @api.route("/books", 'get')
    def list_books(req, resp):
        resp.json = {"books": ['book1', 'book2', 'book3']}

    @api.route("/books", 'post')
    def create_book(req, resp):
        resp.status_code = 201
        resp.json = {"book": 'book1'}

    list_response = client.get(base_url + '/books')
    create_response = client.post(base_url + '/books')


    assert list_response.status_code == 200
    assert create_response.status_code == 201

    assert list_response.json() == {"books": ['book1', 'book2', 'book3']}
    assert create_response.json() ==  {"book": 'book1'}


class TestLogMiddleware:

    def test_logs_request(self, api, client, caplog):
        caplog.clear()
        base_url = "http://testserver.com"
        caplog.set_level(logging.DEBUG, "vraxion")

        
        api.add_middleware(LogMiddleware)

        @api.route("/books", method='get')
        def list_books(req, resp):
            resp.json = {"books": ['book1', 'book2', 'book3']}


        _ = client.get(base_url + '/books')
        assert LogMiddleware.LOG_MESSAGE_FMT.format(method="GET", url="http://testserver.com/books", body="") in caplog.text

    def test_logs_post_request(self, api, client, caplog):
        caplog.clear()
        
        base_url = "http://testserver.com"
        caplog.set_level(logging.DEBUG, "vraxion")
        api.add_middleware(LogMiddleware)

        @api.route("/books", method='post')
        def list_books(req, resp):
            resp.json = {"books": ['book1', 'book2', 'book3']}


        _ = client.post(base_url + '/books', json={"a": "b"})
        assert LogMiddleware.LOG_MESSAGE_FMT.format(method="POST", url="http://testserver.com/books", body="{'a': 'b'}") in caplog.text