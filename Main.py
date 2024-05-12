import re, os
import logging, traceback
import datetime

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame import Surface, draw, Vector2, image

os.chdir(os.path.dirname(__file__))
from Const import *
from GraphAPI import getComments, postImage, Comment
from Logik import Logik, Guess

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

def chooseGuess(comments: list[Comment]) -> tuple[str, Comment]:
	comments.sort(key=lambda c: c.timestamp)
	comments.sort(key=lambda c: c.likes)
	regex = '\\b[%s]{%s}\\b' % (COLORS, COUNT)
	matches = [re.findall(regex, c.text) for c in comments]
	matches = [(m[-1], c) for m, c in zip(matches, comments) if m]
	if not matches:
		logging.warning('No guesses found, aborting')
		exit()
	return matches[-1]
def getGuess(logik: Logik):
	if not logik.postIds:
		logging.error('no post Id supplied, aborting')
		exit()
	comments = getComments(logik.postIds[-1])
	guess, comment = chooseGuess(comments)
	logik.addGuess(guess, comment.username, comment.likes)
	logging.info('Guesses: ' + ', '.join(map(repr, logik.guesses)))

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
def genDesc(logik: Logik) -> str:
	guess = logik.guesses[-1]
	correctPositions, correctColors = logik.evalGuess(guess)
	evalStr = f'This guess contains {correctColors} correct colors'
	if correctPositions: evalStr += f' and {correctPositions} of them are in the right position!'
	else: evalStr += '.'
	if logik.won(): evalStr = f"Correct! '{guess}' is indeed the right solution!\nYou won this game in {len(logik.guesses)} guesses, congrats! 🎉\n🔄 Comment new guess here to start a new logik game."
	likeStr = f' with {guess.likes} ❤️' if guess.likes else ''
	desc = f"""
{logik.getDescriptor()} New guess {guess} by @{guess.username}{likeStr}
{evalStr}

❓ For more info see the gray info post below ⬇️

Made with ❤️ by Michal Martínek ©2024
This post was posted automatically through my server.
GitHub: https://github.com/Michal-Martinek/logic_game_daily

#logik #interactive #game #puzzle #voting #colors #audience #GraphAPI
"""
	return desc

def post(logik: Logik, filepath: str):
	desc = genDesc(logik)
	postId = postImage(desc, filepath)
	logik.postIds.append(postId)
	logging.info(f'postId: {postId}')

def main():
	initLogging()
	logik = Logik()
	logging.info('Started after ' + logik.getDescriptor())

	getGuess(logik)
	filepath = renderGame(logik)
	post(logik, filepath)

	if logik.won():
		logging.info(f'Game {logik.getDescriptor()} won, starting new\n\n')
		logik.newGame()
	else:
		logging.info(f'Posted {logik.getDescriptor()}, closing\n\n')
	logik.save()

if __name__ == '__main__':
	runFuncLogged(main)
