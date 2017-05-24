from wsgiref.validate import validator
from wsgiref.simple_server import make_server
from demo.main_app import app

class TempApp:
    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)

        elist = []

        if environ['PATH_INFO'] != '/favicon.ico':
            for key in environ:
                elist.append(str(key)+':'+str(environ[key]))
            elist.sort()

            print('==========================================')
            for e in elist:
                print(e)

        return [b'Hello World']

tempApp = TempApp()


httpd = make_server('', 8000, app)
print("Serving HTTP on port 8000...")

# Respond to requests until process is killed
httpd.serve_forever()

# Alternative: serve one request, then exit
httpd.handle_request()
