class UrlParser:
    def __init__(self, ulrpattern):
        self._urlpattern = ulrpattern

    def parse(self):
        pass

    def named_route_params(self):
        return {}

    def unnamed_route_params(self):
        return []

    def query_params(self):
        return {}

    def is_match(self, url):
        # Is the url match current instance's url pattern
        pass