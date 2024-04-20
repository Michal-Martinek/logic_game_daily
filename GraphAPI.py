import requests
import json
import datetime

# helpers ------------------------
def getCredentials() -> dict:
	with open('credentials.json') as f:
		creds = json.load(f)
	return creds
def displayJson(data, indent=4):
	s = json.dumps(data, indent=indent)
	print(s)

class Comment: # TODO test
	def __init__(self, comment: dict):
		self.id: str = comment['id']
		self.username: str = comment['from']['username']
		self.userId: str = comment['from']['id']
		self.text: str = comment['text']
		self.likes: int = comment['like_count']
		self.timestamp = datetime.datetime.strptime(comment['timestamp'], r'%Y-%m-%dT%X%z')
	def __str__(self) -> str:
		return self.username  + ': "' + self.text + '"'
	def __repr__(self) -> str:
		return 'Comment<' + str(self) + '>'

CREDENTIALS = getCredentials()
API_BASE_URL = 'https://graph.facebook.com/v19.0'
ACCOUNT_SPECIFIC_URL = API_BASE_URL + '/' + CREDENTIALS['instagram_account_id']

# requests --------------------------------
def prepareParams(params):
	params['access_token'] = CREDENTIALS['access_token']
def handleRes(res: requests.Response) -> dict:
	print(res.url.replace(CREDENTIALS['access_token'], '###'))
	try:
		data = json.loads(res.content)
		displayJson(data)
	except: print(res.content, end='\n\n')
	assert res.ok, f'Request returned status code {res.status_code}'
	return data
def callApi(endpoint: str, method='GET', **params):
	prepareParams(params)
	url = API_BASE_URL + '/' * (endpoint[0] != '/') + endpoint
	res = requests.request(method, url, params=params)
	return handleRes(res)

def getComments(postId) -> list[Comment]:
	res = callApi(postId + '/comments', postId, fields='id,text,like_count,from,timestamp')
	comments = [Comment(c) for c in res['data']]
	return comments
