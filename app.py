from api import Api

app = Api()


@app.route('/home')
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route('/about')
def about(request, response):
    response.text = "Hello from the ABOUT page"