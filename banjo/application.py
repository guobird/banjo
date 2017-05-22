import re
from banjo.router import Router
from banjo.request import Request
from banjo.response import Response
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

    # Currently, only router.url() support route parameters(:name), router.middleware() and
    #     router.router() need to use exact string match with url.
    # Also not support regular expr url pattern yet.
    # If the given path and request method doesn't match a view in the _routeMap, return None
    # if matched, return a list and a dict:
    #     matched_middlewares_and_view: [matched_middleware1, matched_middleware2, ..., matched_view]
    #     named_route_params: {named_route_param1: value1, named_route_param2: value2, ...}
    def match(self, path, method_str):
        matched_middlewares = []
        named_route_params = {}

        for item in self._routeMap:
            '''
            item[0]: url pattern
            item[1]: accepted methods(int repr)
            item[2]: middlewares(tuple)/view
            '''
            # 1. Test if request method match
            if RouteMap.method2int(method_str) & item[1] == 0b0000:
                continue
            # 2. Test if url path pattern match, also write named_route_params if match
            if not Application.pattern_match(item[0], path, named_route_params):
                continue
            # 3. Now the path matches, check if it matches a middleware list or a view
            if type(item[2]) is tuple: # matched a middleware item
                matched_middlewares.extend(list(item[2]))
            else: # matched a view item, should stop search
                matched_middlewares.append(item[2])
                return matched_middlewares, named_route_params

        return None

    # todo: support % encoded character
    @staticmethod
    def pattern_match(pattern, path, named_route_params):
        '''
        :param pattern:
        :param path:
        :param named_route_params: an empty dict, if match, fill this dict
        :return: boolean
        '''
        path = path.strip()
        if path[-1] == '/':
            path = path[:-1]
        if path[0] == '/':
            path = path[1:]

        pattern_segs = pattern.split('/')
        path_segs = path.split('/')

        if pattern_segs[-1] != '*':
            if len(pattern_segs) != len(path_segs):
                return False
        else:
            pattern_parts = pattern_segs[0:-1]
            if len(path_segs) < len(pattern_parts):
                return False

        for index, pattern_part in enumerate(pattern_segs):
            if not Application.segment_match(pattern_part, path_segs[index], named_route_params):
                named_route_params.clear()
                return False

        return True

    @staticmethod
    def segment_match(pattern_seg, path_seg, named_route_params):
        '''

        :param pattern_seg: a path segment, possibly include :name route parameter pattern
        :param path_seg: path segment of a http request
        :param named_route_params: a dict possibly with partly filled params, if match, should append this dict
        :return: False if not match, True if match
        '''
        allowed_chars = r'[a-zA-Z0-9_:-]+'
        assert re.fullmatch(allowed_chars, pattern_seg)
        assert re.fullmatch(allowed_chars, path_seg)

        pattern_parts = pattern_seg.split('-')
        path_parts = path_seg.split('-')
        if len(pattern_parts) != len(path_parts):
            return False

        route_params = {}
        PARAM_RE = r':[a-zA-Z0-9_]+'
        for index, ptnpart in enumerate(pattern_parts):
            if re.fullmatch(PARAM_RE, ptnpart):
                route_params[ptnpart[1:]] = path_parts[index]
            elif ptnpart != path_parts[index]:
                return False
            else:
                continue
        named_route_params.update(route_params)
        return True