from banjo import Router, Request, Response
from banjo.router import RouteMap
from banjo.utils.urlparser import UrlParser

class Application(Router):
    settings = None

    def __init__(self):
        super().__init__()
        self.locals = {}

    def __call__(self, environ, start_response):
        # todo: fill request according to environ
        request = Request()

        # todo: fill request with query parameters

        match_result = self.match(environ['PATH_INFO'], environ['REQUEST_METHOD'])
        if match_result is not None:
            middleware_chain, request.named_route_params, request.unnamed_route_params = match_result
            middleware_chain.reverse()
            cur_chained = middleware_chain[0]
            for middleware in middleware_chain[1:]:
                cur_chained = middleware(cur_chained)
            response = cur_chained(request)
            status = response.status()  # HTTP Status
            headers = response.headers()  # HTTP Headers
        else:
            status = '404 Not Found'
            headers = []
            response = Response()
        start_response(status, headers)
        return response.body()

    # If the given path and request method doesn't match a view in the _routeMap, return None
    # if matched, return two list and a dict:
    #     matched_middlewares_and_view: [matched_middleware1, matched_middleware2, ..., matched_view]
    #     named_route_params: {named_route_param1: value, named_route_param2: value, ...}
    #     unnamed_route_params: [unnamed_route_param1, unnamed_route_param2, ...]
    # Path doesn't include host part or query parameters, eg. for url 'http://www.banjo.com/commutity/blogs/?user=bird',
    #     the path is '/comunity/blogs'
    def match(self, path, method_str):
        matched_middlewares = []
        named_route_params = {}
        unnamed_route_params = []

        for item in self._routeMap:
            '''
            item[0]: url pattern
            item[1]: accepted methods(int repr)
            item[2]: middlewares(tuple)/None
            item[3]: view/None
            '''
            # 1. Test if request method match
            if RouteMap.method2int(method_str) & item[1] == 0b0000:
                continue
            # 2. Test if url path pattern match, also write named_route_params and unnamed_route_params if match
            if not Application.pattern_match(item[0], path, named_route_params, unnamed_route_params):
                continue
            # 3. Now the path matches, check if it matches a middleware list or a view
            if item[2] is not None: # matched a middleware item
                matched_middlewares.extend(list(item[2]))
            elif item[3] is not None: # matched a view item, should stop search
                matched_middlewares.append(item[3])
                return matched_middlewares, named_route_params, unnamed_route_params
            else:
                # if the format of _routeMap items are correct, we shouldn't get here
                raise 'Internal Error, should caused by a wrong formatted _routeMap item'
        return None

    @staticmethod
    def pattern_match(pattern, path, named_route_params, unnamed_route_params):
        '''
        :param pattern:
        :param path:
        :param named_route_params: an empty dict, if match, fill this dict
        :param unnamed_route_params: an empty list, if match, fill this list
        :return: boolean
        '''
        pass