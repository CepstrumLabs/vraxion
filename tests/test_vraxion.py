import logging
import pytest
import os

from vraxion.api import Api

logger = logging.getLogger("tests")

@pytest.fixture
def api():
    return Api()

@pytest.fixture
def client(api):
    return api.test_session()

def test_basic_route_adding(api):
    """
    Ensure that we can create a basic route
    """

    @api.route('/home')
    def home(req, resp):
        resp.text = 'home'

    @api.route('/home/{name}')
    def with_param(req, resp):
        resp.text = 'with_param'

    @api.route('/')
    def index(req, resp):
        resp.text = 'index'


def test_does_not_allow_duplicate_routes(api):
    """
    Ensure that we don't allow duplicate routes
    """

    @api.route('/home')
    def home(req, resp):
        resp.text = 'Home'

    with pytest.raises(AssertionError):
        @api.route('/home')
        def home_2(req, resp):
            resp.text = 'Home'


def test_basic_route_response_get(api, client):
    
    response_text = 'home'
    @api.route('/home')
    def home(req, resp):
        resp.text = response_text
    
    assert client.get("http://testserver.com/home").text ==  response_text


def test_basic_route_with_query_param_response_get(api, client):
    
    response_text = 'home'
    name = 'test_name'
    @api.route('/home/{name}')
    def home(req, resp, name):
        resp.text = response_text + name
    
    assert client.get(f"http://testserver.com/home/{name}").text ==  response_text + name


def test_default_404_response(client):
        
    response = client.get("http://testserver.com/doesnotexist")

    assert response.status_code == 404
    assert response.text == "Sorry mate, page not found"


def test_class_based_handler_get(api, client):
    
    response_text = 'get'

    @api.route('/book')
    class BookResource:
        def get(self, req, resp):
            resp.text = response_text

    response = client.get("http://testserver.com/book")
    assert response.text == response_text

def test_class_based_handler_post(api, client):
    
    response_text = 'post'
    
    @api.route('/book')
    class BookResource:
        def post(self, req, resp):
            resp.text = response_text

    response = client.post("http://testserver.com/book")
    assert response.text == response_text


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

    api.add_route("/handler", handler)

    response = client.get("http://testserver.com/handler")
    assert response.text == response_text

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
    
    @api.route("/html")
    def handler(req, resp):
        resp.body = api.template("about.html", context={"title": title, "name": name}).encode()
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

    @api.route("/home")
    def home(req, resp):
        raise AttributeError()

    response = client.get("http://testserver.com/home")
    assert response.text == "AttributeErrorHappend"


def test_404_is_returned_for_nonexistent_static_file(client):
    assert client.get(f"http://testserver.com/main.css)").status_code == 404


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
    
    response = client.get(f"http://testserver.com/{FILE_DIR}/{FILE_NAME}")
    
    assert response.status_code == 200
    assert FILE_CONTENTS in response.text
