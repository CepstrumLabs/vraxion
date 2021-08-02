from vraxion.api import Api
from vraxion.middleware import Middleware

app = Api()


@app.route('/home')
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route('/about')
def about(request, response):
    response.text = "Hello from the ABOUT page"

@app.route('/hello/{name}')
def hello(request, response, name=None):
    response.text = f"Hello {name}"


@app.route('/book')
class Book:

    def get(self, request, response):
        response.text = "Book Page GET"
    
    def post(self, request, response):
        response.text = "Book Page POST"

def handler(req, resp):
    resp.text = "sample"

def handler_with_template(req, resp):
    resp.body = app.template(template_name="about.html", context={"title": "Awesome Framework", "name": "Vraxion"})

app.add_route("/sample", handler)
app.add_route("/awesome", handler_with_template)

class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Processing request", req.url)

    def process_response(self, req, res):
        print("Processing response", req.url)

app.add_middleware(SimpleCustomMiddleware)