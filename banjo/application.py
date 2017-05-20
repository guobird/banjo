from banjo.router import Router
from banjo.response import Response
from banjo.request import Request
from banjo.router import RouteMap
import re

class Application(Router):
    settings = None

    def __init__(self):
        super().__init__()
        self.environ = None
        self.locals = {}

    def __call__(self, environ, start_response):
        self.environ = environ
        # self.start_response = start_response

        # todo: set self.raw_request to a banjo.Request object

        match_result = self.match(environ['PATH_INFO'], environ['REQUEST_METHOD'])
        if match_result is not None:
            matched_middlewares = match_result[0:-1]
            matched_view = match_result[-1]
            cur_chained = matched_view
            for middleware in matched_middlewares:
                cur_chained = middleware(cur_chained)
            response = cur_chained(self.raw_request)
            status = response.status()  # HTTP Status
            headers = response.headers()  # HTTP Headers
        else:
            status = '404 Not Found'
            headers = []
            response = Response()
        start_response(status, headers)
        return response.body()

    @property
    def raw_request(self):
        return 'test'

    # if matched, return true, write to parameter all_middlewares, matched_view
    def match(self, path, method_str):
        all_middlewares = []
        for item in self._routeMap:
            [pattern, methods, middlewares, view] = item
            # todo: use regexp match instead
            if RouteMap.method2int(method_str)==methods:
                if item[2] is not None: # matched a middleware item, then we need include sub path
                    if pattern.startswith(path): # startswith is not correct, waiting for correct
                        all_middlewares.append(list(middlewares))
                elif item[3] is not None: # matched a view item
                    if pattern == path:
                        return all_middlewares, item[3]
        return None
