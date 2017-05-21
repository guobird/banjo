class Request:
    def __init__(self):
        self.rawHeaders = {}
        self.rawBody = None
        self.locals = {}
        self.named_route_params = {}
        self.unnamed_route_params = []

    @property
    def app(self):
        pass

    @property
    def baseUrl(self):
        pass

    @property
    def body(self):
        pass

    @property
    def cookies(self):
        pass

    @property
    def method(self):
        pass

