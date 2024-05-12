import requests
import json
import datetime
import time, os
import logging

import http.server
from socketserver import TCPServer
import threading, subprocess

# helpers ------------------------
def getCredentials() -> dict:
	with open('credentials.json') as f:
		creds = json.load(f)
	return creds

class Comment:
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
def logRes(logLvl, method, res: requests.Response, data):
	url = res.url.replace(CREDENTIALS['access_token'], '###')
	data = json.dumps(data, indent=4) if isinstance(data, dict) else data
	logging.log(logLvl, f'{method} {res.status_code} {url}\n{data}\n')
	if logLvl != logging.INFO:
		logging.error('ERROR in request')
		exit(1)
def handleRes(res: requests.Response, method, logLvl=logging.ERROR) -> dict:
	try:
		data = json.loads(res.content)
		if res.ok: logLvl = logging.INFO
	except json.JSONDecodeError: data = res.content
	logRes(logLvl, method, res, data)
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
		while self.PORT < 8010:
			try:
				self.server = TCPServer(('', self.PORT), Handler)
				break
			except OSError:
				self.PORT += 1
				logging.warning(f'Error in setting up TCPServer, trying PORT={self.PORT}')
		self.serverThread = threading.Thread(target=self.server.serve_forever)
		self.serverThread.start()

	def spawnNgrok(self):
		self.ngrok = subprocess.Popen(['ngrok', 'http', str(self.PORT)], stdout=subprocess.PIPE)
		time.sleep(2)
		try:
			res = requests.get('http://localhost:4040/api/tunnels')
			self.serverUrl = res.json()['tunnels'][0]['public_url']
		except Exception:
			logRes(logging.INFO, 'GET', res, json.loads(res.content))
			raise
		logging.info('Server URL: ' + self.serverUrl)
	def imageUrl(self, path):
		assert os.path.exists(path)
		return self.serverUrl + '/' + path
	def shutdown(self):
		self.server.shutdown()
		self.ngrok.terminate()
		self.serverThread.join()

def createMediaObject(caption: str, imageUrl: str) -> str:
	res = callApi(ACCOUNT_ID + '/media', 'POST', caption=caption, image_url=imageUrl)
	return res['id']
def isMediaFinished(mediaId) -> bool:
	res = callApi(mediaId, fields='status_code')
	finished = res['status_code'] == 'FINISHED'
	if not finished: logging.info('media status: ' + res['status_code'] + ', waiting...')
	return finished
def publishMedia(mediaId) -> str:
	res = callApi(ACCOUNT_ID + '/media_publish', 'POST', creation_id=mediaId)
	return res['id']
def postImage(caption, filepath) -> str:
	try:
		server = Server()
		mediaId = createMediaObject(caption, server.imageUrl(filepath))
		while not isMediaFinished(mediaId):
			time.sleep(5)
		postId = publishMedia(mediaId)
	finally:
		try:
			server.shutdown()
		except Exception: pass
	return postId
