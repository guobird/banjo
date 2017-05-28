import unittest
from banjo.middleware.cookie import CookieMiddleware
from banjo import Request


def mock_middleware(request):
    return request


class TestCookieMiddleware(unittest.TestCase):
    def test_call(self):
        request = Request()
        request.environ['HTTP_COOKIE'] = \
        '''vjuids=-1fb6d72f7.15; __utma=32066017.119922; __utmz=utmcsr=baidu|utmccn=(organic)|utmcmd=organic; dev-sel=1; \
            gn12=w:1; gj12=w:1; sohutag=8HsmeSc5NCwm; IPLOC=CN3100; SUV=1603291602278952; vjlast=146540557344.11'''

        filtered = CookieMiddleware(mock_middleware)(request)
        cookie_dict = filtered.cookie_dict
        self.assertEqual(cookie_dict['sohutag'], '8HsmeSc5NCwm')
        self.assertEqual(cookie_dict['__utmz'], 'utmcsr=baidu|utmccn=(organic)|utmcmd=organic')


if __name__ == '__main__':
    unittest.main()