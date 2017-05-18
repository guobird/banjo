from routes.index import IndexRouter
from routes.user import UserRouter
from vase.application import Application


class App(Application):
    routers = {
        '/': IndexRouter,
        '/users/': UserRouter
    }
    middlewares = [
        BodyParser.json(),
        BodyParser.urlencoded(),
        CookieParser,
    ]

