from pygame import Vector2

NUM_GUESSES = 8
COUNT = 4
COLORS = 'RGBOYW'
CHAR_TO_COLOR = {
	'R': (255, 0, 0),
	'G': (0, 255, 0),
	'B': (0, 0, 255),
	'O': (255, 165, 0),
	'Y': (255, 255, 0),
	'W': (255, 255, 255), 
}

IMG_SIZE = 1080
BACKGROUND_COLOR = (210, 153, 138)
BOUNDARY_COLOR = (0, 0, 0)
BLANK_COLOR = (128, 0, 0)

CIRCLE_RAD = 40
CIRCLE_BOUNDARY = 3

X_SPACING = 2 * CIRCLE_RAD + 20
Y_SPACING = X_SPACING + 25

GUESSES_OFFSET = Vector2(580, 100)
SHADOW_OFFSET = Vector2(12, 20)
EVAL_OFFSET = Vector2(CIRCLE_RAD + 40, GUESSES_OFFSET.y)
