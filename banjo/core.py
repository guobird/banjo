import re


class Request:
    def __init__(self):
        self._headers = {}
        self._body = None
        self.locals = {}
        self.named_route_params = {}

    def set_headers(self, header_dict):
        self._headers = header_dict

    @property
    def app(self):
        pass

    @app.setter
    def app(self):
        pass

    @property
    def base_url(self):
        pass

    @base_url.setter
    def base_url(self):
        pass

    @property
    def body(self):
        pass

    @body.setter
    def body(self):
        pass

    @property
    def cookies(self):
        pass

    @cookies.setter
    def cookie(self):
        pass

    @property
    def method(self):
        pass

    @method.setter
    def method(self):
        pass


class Response:
    def append(self, value):
        pass

    def setCookie(self, name, value, option):
        pass

    def json(self, body):
        pass

    def status(self):
        pass

    def headers(self):
        pass

    def body(self):
        pass

    def set_body(self):
        pass


# todo: convert base path of a middleware route to regexp that include sub path
#    eg: if the basepath given by user calling router.middleware(basepath) is '/blog/bird',
#    then we should convert it to '/blog/bird/*' before saving to _routeMap,
#    this will ease the work when matching a path
class RouteMap:
    def __init__(self):
        '''
        An item of self._map is a tuple which has following structure:
        (urlpattern, request_methods_int_repr, middleware_tuple, view)
        There are two kinds of items: middleware item & view item.
        eg. middleware item: ('/user/bird', 0b0001, (BodyParserMiddleware, CookieMiddleware,), None)
        eg. view item:  ('/user/bird', 0b0001, None, about_view)
        Remember that for middleware item, the url pattern is the base path, all sub paths will match the pattern;
        and for view item, sub path are not included.
        '''
        self._map = []

    def addMiddlewares(self, basePath, middlewares, methods):
        methods_int_repr = RouteMap.method2int(methods)
        item = (basePath, methods_int_repr, middlewares, None)
        self._map.append(item)

    def appendRouteMap(self, basePath, subRouter):
        pass

    def addUrl(self, url, view, methods):
        methods_int_repr = RouteMap.method2int(methods)
        item = (url, methods_int_repr, None, view)
        self._map.append(item)

    @staticmethod
    def method2int(method_str):
        result = 0b0000
        methods = method_str.split(' ')
        for index, method in enumerate(methods):
            methods[index] = method.strip().lower()

        if 'get' in methods:
            result &= 0b0001
        if 'post' in methods:
            result &= 0b0010
        if 'put' in methods:
            result &= 0b0100
        if 'delete' in methods:
            result &= 0b1000
        if result==0:
            raise 'Wrong request methods specified'
        return result


class Router:
    def __init__(self):
        self._basePath = None
        self._routeMap = RouteMap()

    # called when calling app.router()
    # eg. calling app.router('/user', router) will set _basePath to '/user'
    def setBasePath(self, path):
        self._basePath = path

    def basePath(self):
        return self._basePath

    def getSubRouterMap(self, router):
        return self._routeMap

    def chained_middleware(self):
        pass

    # add a middleware to route map
    def middleware(self, basePath, middlewares, methods='all'):
        if type(middlewares) is Middleware:
            self._routeMap.addMiddlewares(basePath, (middlewares,), methods)
        elif type(middlewares) is list or tuple:
            self._routeMap.addMiddlewares(basePath, tuple(middlewares), methods)
        else:
            raise Exception('Wrong middlewares parameter specified')

    def router(self, basePath, subRouter):
        subRouter.setBasePath(basePath)
        self._routeMap.appendRouteMap(basePath, subRouter.getRouteMap())

    def url(self, exactPath, view, methods='get'):
        self._routeMap.addUrl(exactPath, view, methods)


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

