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
		r1 = Card('Room', 'Conservatory')
		r2 = Card('Room', 'Hall')
		r3 = Card('Room', 'Lounge')
		r4 = Card('Room', 'Dining Room')
		r5 = Card('Room', 'Kitchen')
		r6 = Card('Room', 'Ballroom')
		r7 = Card('Room', 'Billiard Room')
		r8 = Card('Room', 'Library')
		r9 = Card('Room', 'Study')
		self.rooms = [r1, r2, r3, r4, r5, r6, r7, r8, r9]
		np.random.shuffle(self.rooms)

		#Init weapons
		w1 = Card('Weapon', 'Candlestick')
		w2 = Card('Weapon', 'Revolver')
		w3 = Card('Weapon', 'Wrench')
		w4 = Card('Weapon', 'Rope')
		w5 = Card('Weapon', 'Lead Pipe')
		w6 = Card('Weapon', 'Knife')
		self.weapons = [w1, w2, w3, w4, w5, w6]
		np.random.shuffle(self.weapons)

		#Init suspects
		s1 = Card('Suspect', 'Miss Scarlett')
		s2 = Card('Suspect', 'Mrs White')
		s3 = Card('Suspect', 'Mr Green')
		s4 = Card('Suspect', 'Mrs Peacock')
		s5 = Card('Suspect', 'Colonel Mustard')
		s6 = Card('Suspect', 'Professor Plum')
		self.suspects = [s1, s2, s3, s4, s5, s6]
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
	assignedType - Type of the card is known
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
		self.assignedType = None

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


if __name__ == '__main__':
	hand = Hand()
	hand.add_card(Card('Weapon', 'Lead Pipe'))
	for c in hand.getCards():
		print (c.getType())
