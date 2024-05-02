import requests
import json
import datetime
import time, os

import http.server
from socketserver import TCPServer
import threading, subprocess

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
ACCOUNT_ID = CREDENTIALS['instagram_account_id']

# requests --------------------------------
def prepareParams(params):
	params['access_token'] = CREDENTIALS['access_token']
def handleRes(res: requests.Response, method) -> dict:
	print(method, res.url.replace(CREDENTIALS['access_token'], '###'))
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
	return handleRes(res, method)

def getComments(postId) -> list[Comment]:
	res = callApi(postId + '/comments', fields='id,text,like_count,from,timestamp')
	comments = [Comment(c) for c in res['data']]
	return comments

# posting -----------
class Server:
	PORT = 8000
	def __init__(self):
		self.spawnHttpServer()
		self.spawnNgrok()
	def spawnHttpServer(self):
		Handler = http.server.SimpleHTTPRequestHandler
		self.server = TCPServer(('', self.PORT), Handler)
		self.serverThread = threading.Thread(target=self.server.serve_forever)
		self.serverThread.start()

	def spawnNgrok(self):
		self.ngrok = subprocess.Popen(['ngrok', 'http', str(self.PORT)], stdout=subprocess.PIPE)
		time.sleep(2)
		res = requests.get('http://localhost:4040/api/tunnels')
		self.serverUrl = res.json()['tunnels'][0]['public_url']
	def imageUrl(self, path):
		assert os.path.exists(path)
		return self.serverUrl + '/' + path
	def shutdown(self):
		self.ngrok.terminate()
		self.server.shutdown()
		self.serverThread.join()

def createMediaObject(caption: str, imageUrl: str) -> str:
	res = callApi(ACCOUNT_ID + '/media', 'POST', caption=caption, image_url=imageUrl)
	return res['id']
def isMediaFinished(mediaId) -> bool:
	res = callApi(mediaId, fields='status_code')
	finished = res['status_code'] == 'FINISHED'
	if not finished: print('media status: ' + res['status_code'] + ', waiting...')
	return finished
def publishMedia(mediaId) -> str:
	res = callApi(ACCOUNT_ID + '/media_publish', 'POST', creation_id=mediaId)
	return res['id']
def postImage(caption, filepath) -> str:
	server = Server()
	mediaId = createMediaObject(caption, server.imageUrl(filepath))
	while not isMediaFinished(mediaId):
		time.sleep(5)
	postId = publishMedia(mediaId)
	server.shutdown()
	return postId
