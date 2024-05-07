import re, os
import logging, traceback
import datetime

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame import Surface, draw, Vector2, image

from Const import *
from GraphAPI import getComments, postImage, Comment
from Logik import Logik

# helpers --------------------------------
LOGGING_LVL = 'INFO'
def initLogging():
	if not os.path.exists('logs'): os.mkdir('logs')
	filename = 'logs/%s.log' % datetime.datetime.now().strftime('%Y-%m-%d')
	handlers = [logging.FileHandler(filename), logging.StreamHandler()]
	logging.basicConfig(handlers=handlers, level=LOGGING_LVL, format='[%(levelname)s] %(asctime)s %(filename)s:%(lineno)i:%(funcName)s:	%(message)s')
def runFuncLogged(func):
	try:
		func()
	except Exception as e:
		strs = traceback.format_exception(type(e), e, e.__traceback__)
		msg = 'UNCATCHED EXCEPTION\n' + ''.join(strs[1:])
		logging.critical(msg)
		raise SystemExit()

def chooseGuess(logik: Logik, comments: list[Comment]):
	comments.sort(key=lambda c: c.timestamp)
	comments.sort(key=lambda c: c.likes)
	regex = '\\b[%s]{%s}\\b' % (COLORS, COUNT)
	matches = [re.findall(regex, c.text) for c in comments]
	matches = [m[0] for m in matches if m]
	if not matches:
		logging.warning('No guesses found, generating randomly')
		return logik.genRandomGuess()
	return matches[-1]
def getGuess(logik: Logik):
	if not logik.postIds: return
	comments = getComments(logik.postIds[-1])
	guess = chooseGuess(logik, comments)
	logik.addGuess(guess)
	logging.info('Guesses: ' + ', '.join(map(str, logik.guesses)))

# drawing -----------------------------------
def drawCircle(img, pos, colorChar):
	draw.circle(img, (128, 128, 128), pos + SHADOW_OFFSET, CIRCLE_RAD)
	draw.circle(img, CHAR_TO_COLOR[colorChar], pos, CIRCLE_RAD)
	draw.circle(img, BOUNDARY_COLOR, pos, CIRCLE_RAD, width=CIRCLE_BOUNDARY)
def drawGuess(row, img: Surface, guess):
	topleft = GUESSES_OFFSET + Vector2(0, row * GUESSES_Y_OFFSET)
	for col in range(COUNT):
		pos = topleft + Vector2(CIRCLE_RAD + CIRCLES_X_OFFSET * col, CIRCLE_RAD)
		colorChar = guess.s[col] if guess else ''
		drawCircle(img, pos, colorChar)
def drawGuesses(img, logik: Logik):
	for i, guess in enumerate(logik.getGuesses()):
		drawGuess(i, img, guess)
		res = logik.evalGuess(guess)
def drawBackground():
	img = Surface((IMG_SIZE, IMG_SIZE))
	img.fill(BACKGROUND_COLOR)
	return img
def renderGame(logik: Logik):
	img = drawBackground()
	drawGuesses(img, logik)
	return img
def saveImage(img: Surface, logik: Logik):
	path = f'posts/img_{logik.getDescriptor()}.jpg'
	image.save(img, path)
	return path
def post(img: Surface, logik: Logik):
	filepath = saveImage(img, logik)
	postId = postImage(f'{logik.getDescriptor()} - new guess {logik.guesses[-1]}\nBy Michal Martínek\n\n#logik', filepath)
	logik.postIds.append(postId)
	logging.info(f'postId: {postId}')

def main():
	initLogging()
	logik = Logik()
	logging.info('Started after ' + logik.getDescriptor())

	getGuess(logik)
	img = renderGame(logik)
	post(img, logik)
	logik.save()
	logging.info(f'Posted {logik.getDescriptor()}, closing\n\n')

if __name__ == '__main__':
	runFuncLogged(main)
