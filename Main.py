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
def drawCircle(img, pos, color):
	color = CHAR_TO_COLOR[color] if isinstance(color, str) else color
	draw.circle(img, (128, 128, 128), pos + SHADOW_OFFSET, CIRCLE_RAD)
	draw.circle(img, color, pos, CIRCLE_RAD)
	draw.circle(img, BOUNDARY_COLOR, pos, CIRCLE_RAD, width=CIRCLE_BOUNDARY)
def drawCircles(img: Surface, row, logik: Logik, guess: str, isEval: bool):
	pos = (EVAL_OFFSET if isEval else GUESSES_OFFSET) + Vector2(0, row * Y_SPACING)
	for col in range(COUNT):
		if not guess: color = BLANK_COLOR
		elif isEval:
			correctPositions, correctColors = logik.evalGuess(guess)
			color = (0, 0, 0) if col < correctPositions else 'W' if col < correctColors else BLANK_COLOR
		else: color = guess[col]
		drawCircle(img, pos, color)
		pos.x += X_SPACING
def drawGuesses(img, logik: Logik):
	for row, guess in enumerate(logik.getGuesses()):
		drawCircles(img, row, logik, guess, False)
		drawCircles(img, row, logik, guess, True)
def drawBackground():
	img = Surface((IMG_SIZE, IMG_SIZE))
	img.fill(BACKGROUND_COLOR)
	return img

def saveImage(img: Surface, logik: Logik):
	path = f'posts/img_{logik.getDescriptor()}.jpg'
	if not os.path.exists('posts'): os.mkdir('posts')
	image.save(img, path)
	return path
def renderGame(logik: Logik) -> str:
	img = drawBackground()
	drawGuesses(img, logik)
	return saveImage(img, logik)
def post(logik: Logik, filepath: str):
	postId = postImage(f'{logik.getDescriptor()} - new guess {logik.guesses[-1]}\nBy Michal Martínek\n\n#logik', filepath)
	logik.postIds.append(postId)
	logging.info(f'postId: {postId}')

def main():
	initLogging()
	logik = Logik()
	logging.info('Started after ' + logik.getDescriptor())

	getGuess(logik)
	filepath = renderGame(logik)
	post(logik, filepath)
	logik.save()
	logging.info(f'Posted {logik.getDescriptor()}, closing\n\n')

if __name__ == '__main__':
	runFuncLogged(main)
