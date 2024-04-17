import requests
import json

# helpers ------------------------
def getCredentials() -> dict:
	with open('credentials.json') as f:
		creds = json.load(f)
	return creds
def displayJson(data):
	s = json.dumps(data, indent = 4)
	print(s)

CREDENTIALS = getCredentials()
API_BASE_URL = 'https://graph.facebook.com/v19.0'
ACCOUNT_SPECIFIC_URL = API_BASE_URL + '/' + CREDENTIALS['instagram_account_id']

def prepareParams(params):
	params['access_token'] = CREDENTIALS['access_token']
def callApi(endpoint: str, method='GET', **params):
	prepareParams(params)
	url = API_BASE_URL + endpoint
	res = requests.request(method, url, params=params)
	return json.loads(res.content)


r = callApi('/me')
displayJson(r)
