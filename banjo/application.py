import urllib.parse
from banjo import Router, Request, Response
from banjo.router import RouteMap


class Application(Router):
    settings = None

    def __init__(self):
        super().__init__()
        self.locals = {}

    def __call__(self, environ, start_response):
        request = Request()
        request.path = environ['PATH_INFO']
        request.method = environ['REQUEST_METHOD']

        # fill request headers
        for key in environ:
            if key.startswith('HTTP_'):
                request.headers[key[5:]] = environ[key]

        # fill request query parameters
        request.query = urllib.parse.parse_qs(environ['QUERY_STRING'])

        middleware_chain = self._route_map.find_match(request)
        if middleware_chain is not None:
            middleware_chain.reverse()
            cur_chained = middleware_chain[0]
            for middleware in middleware_chain[1:]:
                cur_chained = middleware(cur_chained)
            response = Response(cur_chained(request))
            status = '200 OK'  # HTTP Status
            headers = [('Content-Type', 'text/html')]  # HTTP Headers
        else:
            status = '404 Not Found'
            headers = []
            response = Response("Can not find page")

        start_response(status, headers)
        return [bytes(response.body, encoding='utf-8')]
