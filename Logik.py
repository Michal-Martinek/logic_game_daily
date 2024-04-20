import random

from Const import *

class Guess:
	def __init__(self, s=''):
		if isinstance(s, (list, tuple)): s = ''.join(s)
		self.s = s.upper().strip()
	def __str__(self) -> str:
		return self.s
	def __repr__(self) -> str:
		return 'Guess<' + str(self) + '>'
	def __iter__(self):
		return iter(self.s)
	def __eq__(self, other):
		return self.s == other.s

class Logik:
	def __init__(self):
		self.solution = self.generateSolution()
		self.guesses: list[Guess] = []
		self.lastPostId = ''
	def generateSolution(self):
		colors = list(COLORS)
		random.shuffle(colors)
		return Guess(colors[:COUNT])
	def addGuess(self, s: str):
		self.guesses.append(Guess(s))
	def getGuesses(self) -> list:
		return self.guesses + [''] * (NUM_GUESSES - len(self.guesses))
	def evalGuess(self, guess: Guess) -> tuple[int, int]:
		correctColor = sum(c in self.solution for c in guess)
		correctPosition = sum(c == g for c, g in zip(guess, self.solution))
		return correctColor - correctPosition, correctPosition
