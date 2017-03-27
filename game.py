import time
import functools

class Game(object):

	def __init__(self):
		'''
		- Create all cards
		- Assign case file (randomly)
		- Initialize agents
		- assign cards to agents (Randomly)
		- Choose a player to go first
		'''
		pass
	
	def start(self):
		'''
		- keeping track of who's turn is it
		- is game still going/did someone win?
		- tell next player it's their turn
		'''
		pass

	def _made_suggestion(self, player, suggestion):
		'''
		- tell all agents the suggestion
		- update all players with proof if proof was made
		'''
		pass

	def _made_accusation(self, player, suggestion):
		'''
		- tell all players an accusation was made
		- show case file to Agent
		- if they won end game, otherwise make them inactive, continue game
		'''
		pass


class Card(object):
	pass
	'''
	type
	name
	?owner
	'''
	def __init__(self, type, name):
		'''
		init it with the things
		'''
		pass

	def assign(self, player):
		'''
		self explanatory
		'''
		pass


class Hand(object):
	'''
	6 cards
	'''
	def __init__(self):
		'''
		Initialize 6 empty card objects into hand
		'''
		pass

	def add_card(self, card):
		'''
		Initialize an empty card as card if empty cards exist
		'''
		pass


class Agent(object):
	'''
	Hand

	create blank instance of Hand for each other player

	instance of csp or something
	'''
	def __init__(self):
		'''
		init hand and shit
		opponents
		'''
		pass


	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		'''
		pass

	def update(self, move):
		'''
		update knowledge base with whatever from game
		'''
		pass




