import re
import urllib.parse

class Request:
    def __init__(self):
        self._headers = {}
        self._body = None
        self._path = None
        self._method = None
        self.locals = {}
        self._named_params = {}
        self._params = []
        self._query = {}
        self._app = None

    def set_headers(self, header_dict):
        self._headers = header_dict

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path_info):
        self._path = path_info

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, header_dict):
        self._headers = header_dict

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, application):
        self._app = application

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
    def query(self):
        return self._query

    @query.setter
    def query(self, query_dict):
        self._query = query_dict

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, request_method):
        self._method = request_method

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, route_params):
        self._params = route_params

    @property
    def named_params(self):
        return self._named_params

    @named_params.setter
    def named_params(self, named_route_params):
        self._named_params = named_route_params


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
#    then we should convert it to '/blog/bird/*' before saving to _route_map,
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

    def add_middlewares(self, base_path, middlewares, methods):
        methods_int_repr = RouteMap.method2int(methods)
        item = (re.compile(base_path), methods_int_repr, middlewares)
        self._map.append(item)

    def append_route_map(self, basePath, subRouter):
        pass

    def add_url(self, url_pattern, view, methods):
        methods_int_repr = RouteMap.method2int(methods)
        item = (re.compile(url_pattern), methods_int_repr, view)
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
            raise Exception('Wrong request methods specified')
        return result

    def __iter__(self):
        for item in self._map:
            yield item


class Router:
    def __init__(self):
        self._base_path = None
        self._route_map = RouteMap()

    @property
    def base_path(self):
        return self._base_path

    # called when calling app.router()
    # eg. calling app.router('/user', router) will set _base_path to '/user'
    @base_path.setter
    def base_path(self, path):
        self._base_path = path

    def getSubRouterMap(self, router):
        return self._route_map

    def chained_middleware(self):
        pass

    # add a middleware to route map
    def middleware(self, base_path, middlewares, methods='all'):
        if callable(middlewares):
            self._route_map.add_middlewares(base_path, [middlewares, ], methods)
        elif type(middlewares) is list or tuple:
            for mid in middlewares:
                if not callable(mid):
                    raise Exception('Wrong middleware specified, middleware should be callable.')
            self._route_map.add_middlewares(base_path, list(middlewares), methods)
        else:
            raise Exception('Wrong middlewares parameter specified.')

    def router(self, basePath, subRouter):
        subRouter.setBasePath(basePath)
        self._route_map.append_route_map(basePath, subRouter.getRouteMap())

    def url(self, exactPath, view, methods='get'):
        self._route_map.add_url(exactPath, view, methods)


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

        middleware_chain = self.find_match(request)
        if middleware_chain is not None:
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

    def find_match(self, request):
        '''
        Write request.param if request match a view item in self._route_map
        :param request:
        :return: If the given path and request method doesn't match a view in the _route_map, return None;
                 If matched, return a list:
                     matched_middlewares_and_view: [matched_middleware1, matched_middleware2, ..., matched_view]
        '''
        matched_middlewares = []

        for item in self._route_map:
            '''
            item[0]: url pattern(compiled regex)
            item[1]: accepted request methods(int repr)
            item[2]: middlewares(list)/view
            '''
            # 1. Test if request method match
            if RouteMap.method2int(request.method) & item[1] == 0b0000:
                continue
            # 2. Test if url path pattern match, also write named_route_params if match
            match_obj = item[0].match(request.path)
            if not match_obj:
                continue
            # 3. Now the path matches, check if it matches a middleware list or a view
            if type(item[2]) is list: # matched a middleware item
                matched_middlewares.extend(item[2])
            else: # matched a view item, should stop search
                matched_middlewares.append(item[2])
                request.params = match_obj.groups()
                request.named_params = match_obj.groupdict()
                return matched_middlewares

        return None


