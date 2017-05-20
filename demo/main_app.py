from banjo.application import Application
from banjo.middleware import BodyParserMiddleware, CookieParserMiddleware, LoggerMiddleware
from demo import user_module
from demo import main_views


app = Application()

# app level middlewares
app.middleware('/', [
    LoggerMiddleware,
    BodyParserMiddleware.json(),
    BodyParserMiddleware.urlencoded(),
    CookieParserMiddleware
])

app.url('/', main_views.index_view, 'get')
app.url('/about', main_views.about_view, 'get')
app.router('/users/', user_module.router)


