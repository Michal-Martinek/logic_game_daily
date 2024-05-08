import random
import logging
import pickle

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
	FILENAME = 'logik.pkl'
	def __init__(self, load=True):
		fields = { 'solution': self.genRandomGuess() }
		if load and (o := self.tryLoad()):
			fields = o.__dict__
		self.init(**fields)
	def init(self, solution: Guess, guesses:list[Guess]=[], postIds:list[str]=[], gameNum=1):
		self.solution = solution
		self.guesses = guesses
		self.postIds = postIds
		self.gameNum = gameNum
	def tryLoad(self):
		try:
			with open(self.FILENAME, 'rb') as f:
				return pickle.load(f)
		except (FileNotFoundError, pickle.PickleError):
			logging.warning(f"File '{self.FILENAME}' not found or corrupted, logik reinitialized")
			return False
	def save(self, backup=False):
		filename = f'logikBackups/logik_{self.gameNum}.pkl' if backup else self.FILENAME
		with open(filename, 'wb') as f:
			pickle.dump(self, f)
	def getDescriptor(self):
		return f'L{self.gameNum}G{len(self.guesses)}'
	def genRandomGuess(self):
		colors = list(COLORS)
		random.shuffle(colors)
		return Guess(colors[:COUNT])
	def addGuess(self, guess):
		if isinstance(guess, str): guess = Guess(guess)
		self.guesses.append(guess)
	def getGuesses(self) -> list[str]:
		return [g.s for g in self.guesses] + [''] * (NUM_GUESSES - len(self.guesses))
	def evalGuess(self, guess: Guess) -> tuple[int, int]:
		correctColors = sum(c in self.solution for c in guess)
		correctPositions = sum(c == g for c, g in zip(guess, self.solution))
		return correctPositions, correctColors
	def won(self):
		return self.evalGuess(self.guesses[-1])[0] == COUNT
	def newGame(self):
		self.save(True)
		self.init(self.genRandomGuess(), postIds=self.postIds[-1:], gameNum=self.gameNum+1)
