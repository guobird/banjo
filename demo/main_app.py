from banjo import Application
#from banjo.middleware import BodyParserMiddleware, CookieParserMiddleware, LoggerMiddleware
#from demo import user_module
from demo import main_views


def index_view(request):
    return '<h1 style="color: red">Home Page</h1>'


app = Application()

'''
# app level middlewares
app.middleware('/', [
    LoggerMiddleware,
    BodyParserMiddleware.json(),
    BodyParserMiddleware.urlencoded(),
    CookieParserMiddleware
])
'''
app.url('/', index_view, 'get')
app.url('/about', main_views.about_view, 'get')
app.url('/user', main_views.user_view, 'get')

#app.router('/users/', user_module.router)




