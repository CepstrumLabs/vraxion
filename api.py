from webob import Request, Response


class Api:

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request=request)
        return response(environ, start_response)

    def handle_request(self, request):
        user_agent = request.environ.get("HTTP_USER_AGENT", "No User-Agent found")
        response = Response()
        response.text = f"Hello my friend with user agent -> {user_agent}"
        return response