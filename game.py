import cspclue
import time
import functools
import numpy as np

class Game(object):
	'''
	self.rooms - list of room card variables (except for room card in case file)
	self.weapons - list of weapon card variables (except for weapon card in case file)
	self.suspects - list of suspect card variables (except for suspect card in case file)

	self.caseFileRoom - Room card variable in the case file
	self.caseFileSuspect - Suspect card variable in the case file
	self.caseFileWeapon - Weapon card variable in the case file
	'''

	def __init__(self):
		'''
		- [DONE] Create all cards
		- [DONE] Assign case file (randomly)
		- Initialize agents
		- assign cards to agents (Randomly)			
		- Choose a player to go first
		'''
		self._init_cards()
		self._make_case_file()

	def _init_cards(self):
		'''
		Initialize all 21 cards
		9 rooms, 6 weapons, 6 suspects
		Return lists of each type
		'''
		#Init Rooms
		self.rooms = []
		rooms = ['Conservatory', 'Hall', 'Lounge', 'Dining Room', 'Kitchen', 'Ballroom', 'Billiard Room', 'Library', 'Study']
		for room in rooms:
			r = Card('Room', room, [room])
			self.rooms.append(r)
		np.random.shuffle(self.rooms)

		#Init weapons
		self.weapons = []
		weapons = ['Candlestick', 'Revolver', 'Wrench', 'Rope', 'Lead Pipe', 'Knife']
		for weapon in weapons:
			w = Card('Weapon', weapon, [weapon])
			self.weapons.append(w)
		np.random.shuffle(self.weapons)

		#Init suspects
		self.suspects = []
		suspects = ['Miss Scarlett', 'Mrs White', 'Mr Green', 'Mrs Peacock', 'Colonel Mustard', 'Professor Plum']
		for suspect in suspects:
			s = Card('Suspect', suspect, [suspect])
			self.suspects.append(s)
		np.random.shuffle(self.suspects)
	

	def _make_case_file(self):
		'''
		Assign Case Files from the shuffled lists
		and remove the names of the cards in the case
		file from the shuffled lists
		'''
		self.caseFileRoom = self.rooms[0]
		self.caseFileWeapon = self.weapons[0]
		self.caseFileSuspect = self.suspects[0]

		self.rooms.pop(0)
		self.weapons.pop(0)
		self.suspects.pop(0)


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
	'''
	VARIABLE CLASS:
	type = <Room, Suspect, Weapon>
	name = <Miss Scarlett, Lead Pipe, Study .. >
	owner - player that holds the card
	dom - dom is list of names card can take on or 
		- only contains name of card
	curdom - current domain
	assignedName - Name of card is known / tent assigned to
	'''
	def __init__(self, type=None, name=None, domain=[]):
		'''
		Initialize a card with a type = <Room, Suspect, Weapon>
		and a name = <Miss Scarlett, Lead Pipe, Lounge, ...>
		'''
		self.type = type
		self.name = name
		self.player = None

		self.dom = list(domain)
		self.curdom = [True] * len(domain)

		self.assignedName = name

	def assign(self, player):
		self.player = player

	def getType(self):
		return (self.type)
	
	def getName(self):
		return (self.name)
	
	def getPlayer(self):
		return (self.player)

	def getDomainSize(self):
		return (len(self.dom))

	def getDom(self):
		return (list(self.dom))

	def print_all(self):
		'''Also print the variable domain and current domain'''
		print("Type, Name--\"{}{}\": Dom = {}, CurDom = {}".format(self.type, self.name, self.dom, self.curdom))


class Hand(object):
	'''
	6 cards
	'''
	def __init__(self):
		'''
		Initialize 6 empty card objects into hand
		'''
		self.cards = [Card()]*6

	def add_card(self, card):
		'''
		Initialize an empty card as card if empty cards exist

		NOTE: MIGHT NEED TO MAKE THIS MORE SPECIFIC TO ENSURE TO TARGETS 
		THE RIGHT CARD, for now:
		'''
		for i, c in enumerate(self.cards):
			if c.getName() == None:
				c = card
				self.cards[i] = card
				break

	def isInHand(self, name):
		'''
		Returns true if a card in the hand is assigned name
		'''
		for c in self.cards:
			if c.name == name:
				return True
		return False

	def getCards(self):
		return (list(self.cards))


class Agent(object):
	'''
	Hand

	create blank instance of Hand for each other player

	instance of csp or something
	gabes a bitch
	'''
	def __init__(self):
		'''
		init hand and shit
		opponents

		- Initialize their own hand (given from game class)
		- Initialize ghost hands for 2 oponents (csp*2)
		- Initialize ghost cards for case file (csp)
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

		Update CSPs
		'''
		pass


if __name__ == '__main__':
	game = Game()