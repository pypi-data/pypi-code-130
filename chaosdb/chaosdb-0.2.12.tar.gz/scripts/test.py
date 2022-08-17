from chaosdb.grafana_api_token import configure_control, after_method_control
import logging
import requests

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

configure_control({
    'grafana_api_token': {
#       'host': 'grafana.us.mgmt-aws.ottrpe.com',
      'host': 'grafana.tools.cosmic.sky',
      'port': 80,
      'dashboardId': 516,
      'protocol': 'http',
#       'api_token': 'eyJrIjoiRUpMTmo2STVUekMyMWNET2JQTWl3dWJpeGloTFhwaHEiLCJuIjoibWFyY28ubWFzZXR0aUBza3kudWsiLCJpZCI6MX0=',
#       'cert_file': None
    }
}, {})

after_method_control({'description': 'foo', 'title': 'bar'})
