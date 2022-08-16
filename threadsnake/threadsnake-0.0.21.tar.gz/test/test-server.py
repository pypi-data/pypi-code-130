from threadsnake.core import *
from threadsnake.testing import test, run_test
from typing import Callable, Any
import requests
import time


#set_log_config(LogLevel.ALL)
badge_async('threadsnake 0.0.19', title='version')



port:int = get_port(8088)

print(f'listening on port: {port}')

app = Application(port)

#Configuring top level middlewares
app.configure(static_files('static'))
app.configure(session(Session('threadsnake-session-id')))
app.configure(authorization)
app.configure(body_parser)
app.configure(multipart_form_data_parser('temp', 60))
app.configure(json_body_parser)
app.configure(cors)
app.configure(default_headers(build_default_headers({"purpose":"test"})))
#app.configure(identify_client)
app.configure(header_inspector("content-type", lambda a: print(a)))
app.configure(time_measure)
#app.configure(uses_php('php', 'php', 8086))
app.configure(serve_static_markdown('markdown'))

#Configuring routers
app.use_router(routes_to('routers/users'), '/users')

@app.get('/test-api/base-endpoint/{param}')
def test_api_base_endpoint(app:Application, req:HttpRequest, res:HttpResponse):
    res.end(req.params['param'])

@test({"parameter":"Pelusa"}, True)
def when_param_sent_via_querystring_on_get_it_get_returned_as_response(parameter:str = ''):
    url = f'http://localhost:{port}/test-api/base-endpoint/{parameter}'
    return requests.get(url).text == parameter
    
try:
    app.start()
    time.sleep(1)
    run_test()
except Exception as e:
    print(e)
finally:
    app.stop()