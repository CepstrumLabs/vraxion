from api import Api

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

app.add_route("/sample", handler)
