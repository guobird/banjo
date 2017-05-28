class CookieMiddleware(object):
    def __init__(self, next_middleware):
        self.next_middleware = next_middleware
        # One-time configuration and initialization.

    def __call__(self, request):
        cookie_dict = {}
        cookie_string_list = request.environ['HTTP_COOKIE'].split(';')
        for cookie in cookie_string_list:
            sep_pos = cookie.index('=')
            cookie_dict[cookie[0:sep_pos].strip()] = cookie[sep_pos+1:].strip()

        request.cookie_dict = cookie_dict

        response = self.next_middleware(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
