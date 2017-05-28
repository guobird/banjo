class Response:
    def __init__(self, content=''):
        self.app = None
        self.header_sent = None
        self.locals = None

        self._body = content
        self._headers = {'Content-Type': 'text/html'}

    def append(self, field, value=None):
        pass

    def attachment(self, filename=None):
        pass

    def cookie(self, name, value, *options):
        pass

    def clear_cookie(self, name, *options):
        pass

    def download(self, path, filename=None):
        pass

    def format(self, obj):
        pass

    def get(self, field):
        pass

    def json(self, body):
        pass

    def jsonp(self, body):
        pass

    def links(self, links):
        pass

    def location(self, path):
        pass

    def redirect(self, path, status=301):
        pass

    def set(self, field, value=None):
        if type(field) is str:
            assert value is str
            self._headers[field] = value
        elif type(field) is dict:
            self._headers.update(field)

    def status(self, code):
        pass

    def content_type(self, content_type):
        pass

    def vary(self, field):
        pass

