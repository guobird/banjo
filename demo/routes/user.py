from middleware import Authenticate

from vase.router import Router


class UserRouter(Router):
    middlewares = [
        Authenticate
    ]

    def get(self, request, response):
        response.render('user.html')

    def post(self, request, response):
        pass


class BirdRouter(Router):
    pass


class GuoRouter(Router):
    pass