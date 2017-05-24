import unittest
from banjo.core import RouteMap
import re
from banjo import Request


def user_view(request):
    return 'user view'

def about_view(request):
    return 'about view'


class TestRouteMap(unittest.TestCase):
    def setUp(self):
        self.route_map = RouteMap()
        self.route_map.add_url('/bird/user', user_view, 'get')
        self.route_map.add_url('/bird/about', about_view, 'post get')
        self.route_map.add_url(r'/(?P<name>[a-zA-Z0-9_]+)/about', about_view, 'post get')

    def test_method2int(self):
        self.assertTrue(RouteMap.method2int('get')==0b0001)
        self.assertTrue(RouteMap.method2int('post') == 0b0010)
        self.assertTrue(RouteMap.method2int('put') == 0b0100)
        self.assertTrue(RouteMap.method2int('delete') == 0b1000)
        self.assertTrue(RouteMap.method2int('gEt') == 0b0001)
        self.assertTrue(RouteMap.method2int('post delete') == 0b1010)
        self.assertRaises(Exception, RouteMap.method2int, 'postt')

    def test_add_url(self):
        self.assertTrue(self.route_map._map[0] == (re.compile('/bird/user'), 0b0001, user_view))
        self.assertTrue(self.route_map._map[1] == (re.compile('/bird/about'), 0b0011, about_view))

    def test_find_match(self):
        request = Request()
        request.method = 'get'
        request.path = '/haha'
        self.assertTrue(self.route_map.find_match(request) is None)
        request.path = '/bird/about'
        chain = self.route_map.find_match(request)
        self.assertTrue(chain == [about_view])

        request.path = '/zhenbird/about'
        chain = self.route_map.find_match(request)
        self.assertTrue(chain == [about_view])
        self.assertTrue(request.named_params['name'] == 'zhenbird')


if __name__ == '__main__':
    unittest.main()