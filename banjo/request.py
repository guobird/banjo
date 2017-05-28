class Request:
    def __init__(self):
        self.app = None
        self.base_url = None
        self.body = None
        self.cookies = {}
        self.fresh = None
        self.hostname = None
        self.ip = None
        self.ips = None
        self.method = None
        self.original_url = None
        self.params = {}  # named router parameters
        self.path = None
        self.protocol = None
        self.query = {}
        self.route = None  # contains the currently-matched route, a string
        self.secure = None
        self.signed_cookies = None
        self.stale = None
        self.subdomains = None
        self.xhr = None
        self._headers = {}
        self._body = None

        self.locals = {}
        self.environ = {}

    def accetpts(self, types):
        pass

    def accepts_charsets(self, *charsets):
        pass

    def accepts_encodings(self, *encodings):
        pass

    def accepts_languages(self, *langs):
        pass

    def get(self, field):
        '''Aliased as request.header(field)'''
        pass

    def header(self, field):
        pass

    def is_type(self, content_type):
        pass

    def range(self, size, *options):
        pass