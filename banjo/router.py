from banjo.middleware import Middleware


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
            raise 'Wrong middlewares parameter specified'


    def router(self, basePath, subRouter):
        subRouter.setBasePath(basePath)
        self._routeMap.appendRouteMap(basePath, subRouter.getRouteMap())

    def url(self, exactPath, view, methods='get'):
        self._routeMap.addUrl(exactPath, view, methods)


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




