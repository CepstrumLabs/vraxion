from api import Api

app = Api()


@app.route('/home')
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route('/about')
def about(request, response):
    response.text = "Hello from the ABOUT page"

@app.route('/hello/{name:s}')
def hello(request, response, name=None):
    response.text = f"Hello {name}"
