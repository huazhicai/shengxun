from requests.auth import HTTPBasicAuth
import requests

url = 'http://{0}/api/query_incoming_sms?flag=all'.format("192.168.20.44")
auth = HTTPBasicAuth('admin', 'admin')
# data = {"timestamp": "2018-05-26"}
resp = requests.delete(url, auth=auth)
print(resp.status_code)