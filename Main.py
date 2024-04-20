import re, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame import Surface, draw, Vector2, image

from Const import *
from GraphAPI import getComments, Comment
from Logik import Logik

def chooseGuess(logik: Logik, comments: list[Comment]):
	comments.sort(key=lambda c: c.timestamp)
	comments.sort(key=lambda c: c.likes)
	regex = '\\b[%s]{%s}\\b' % (COLORS, COUNT)
	matches = [re.findall(regex, c.text) for c in comments]
	matches = [m[0] for m in matches if m]
	assert matches, 'No guesses found'
	match = matches[-1]
	logik.addGuess(match)

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
def post(img, logik: Logik):
	pass
def main():
	logik = Logik()
	logik.addGuess('YBRO')

	comments = getComments('18286471126165707')
	chooseGuess(logik, comments)

	img = renderGame(logik)
	image.save(img, 'img.jpg')
	post(img, logik)

if __name__ == '__main__':
	main()
