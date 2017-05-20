# a test middleware
def MethodParserMiddleware(get_response):

    def middleware(request):
        request.method = request.app.environ['REQUEST_METHOD']
        response = get_response(request)
        return response

    return middleware