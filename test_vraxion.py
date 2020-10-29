import pytest

from api import Api


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