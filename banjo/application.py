from banjo.router import Router


class Application(Router):
    settings = None
    render_engine = 'Jade'

    def __init__(self):
        self.environ = None
        self.locals = {}

    def __call__(self, environ, start_response):
        self.environ = environ
        # self.start_response = start_response

        transform_to = self.find_router()
        current_chained_middleware = transform_to.chained_middleware()
        for middleware in Application.middlewares:
            current_chained_middleware = middleware(current_chained_middleware)
        current_chained_middleware(self.raw_request)

        status = '200 OK'  # HTTP Status
        headers = [('Content-type', 'text/plain')]  # HTTP Headers
        start_response(status, headers)
        return [b'Hello World', b'hello bird']

    @property
    def raw_request(self):
        return 'test'

    def find_router(self):
        return Router()

    def render(self, template):
        pass

    def listen(self, port):
        pass