import abc
import cspclue
import time
import functools
import numpy as np


ROOMS = ['Conservatory', 'Hall', 'Lounge', 'Dining Room', 'Kitchen', 'Ballroom', 'Billiard Room', 'Library', 'Study']
WEAPONS = ['Candlestick', 'Revolver', 'Wrench', 'Rope', 'Lead Pipe', 'Knife']
SUSPECTS = ['Miss Scarlett', 'Mrs White', 'Mr Green', 'Mrs Peacock', 'Colonel Mustard', 'Professor Plum']

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
		for room in ROOMS:
			r = Card('Room', room, [room])
			self.rooms.append(r)
		np.random.shuffle(self.rooms)

		#Init weapons
		self.weapons = []
		for weapon in WEAPONS:
			w = Card('Weapon', weapon, [weapon])
			self.weapons.append(w)
		np.random.shuffle(self.weapons)

		#Init suspects
		self.suspects = []
		for suspect in SUSPECTS:
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

	def _distribute_cards(self):
		'''
		distributes remaining cards and returns then as hands
		must be called after _make_case_file()
		'''

		hand1 = Hand()
		hand2 = Hand()
		hand3 = Hand()

		all_cards = np.shuffle(np.array(self.rooms + self.weapons + self.suspects))

		for i in range(all_cards.len()):
			card = all_cards[i]
			if i % 3 == 0:
				hand1.add_card(card)
			elif i % 3 == 1:
				hand2.add_card(card)
			else:
				hand3.add_card(card)

		return hand1, hand2, hand3

	def add_players(self, agent1, agent2, agent3):
		'''
		Adds 3 agents, initializes them and gives them cards
		'''
		hand1, hand2, hand3 = self._distribute_cards
		agent1.give_hand(hand1)
		agent2.give_hand(hand2)
		agent3.give_hand(hand3)

		self.agents = np.shuffle(np.array([agent1, agent2, agent3]))

	def play_game(self):
		'''
		- keeping track of who's turn is it
		- is game still going/did someone win?
		- tell next player it's their turn
		- returns the player who won
		'''
		isNotEliminated = [True]*len(self.agents)
		finished = False
		i = 0

		while not finished:

			if not isNotEliminated[i]:
				# person can make a move
				suggestor = self.agents[i]
				responder = self.agents[(i + 1) % 3]
				observer = self.agents[(i + 2) % 3]

				move = suggestor.make_move()

				if isinstance(move, Suggestion):
					# suggestor made a suggestion

					card_exchanged = self._made_suggestion(move, suggestor, responder, observer)

					if not card_exchanged:
						# ask the next player
						move.responder = observer.name
						_ = self._made_suggestion(move, suggestor, observer, responder)

				else:
					# suggestor made an accusation
					was_correct = self._check_accusation(move)
					suggestor.observe_accusation(True, was_correct)
					responder.observe_accusation(False, was_correct)
					observer.observe_accusation(False, was_correct)

					if was_correct:
						return suggestor
					else:
						isNotEliminated[i] = False
					
			if not any(isNotEliminated):
				# noone can make a move
				return
			i = (i + 1) % 3
		return

	def _check_accusation(self, accusation):
		'''
		Returns True if accusation is correct
		Return False if accusation is incorrect

		accusation is a dict: keys are: <"Room", "Suspect", "Weapon"> 
		'''
		if accusation["Room"].getName() != self.caseFileRoom.getName():
			return False
		if accusation["Suspect"].getName() != self.caseFileSuspect.getName():
			return False
		if accusation["Weapon"].getName() != self.caseFileWeapon.getName():
			return False
		return True

	def _made_suggestion(self, move, suggester, responder, observer):
		response = responder.respond_to_suggestion(move)
		suggestor.update_from_response(move, response)

		card_exchanged = response is not None
		observer.update_from_response(move, card_exchanged)

		return card_exchanged



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

		self.dom = list(domain)
		self.curdom = [True] * len(domain)

		self.assignedName = name

	def getType(self):
		return (self.type)
	
	def getName(self):
		return (self.name)

	def getDomainSize(self):
		return (len(self.dom))

	def getDom(self):
		return (list(self.dom))

	def print_all(self):
		'''Also print the variable domain and current domain'''
		print("Type, Name--\"{}{}\": Dom = {}, CurDom = {}".format(self.type, self.name, self.dom, self.curdom))

	def value_index(self, name):
		'''Domain values need not be numbers, so return the index
		in the domain list of a variable value'''
		return self.dom.index(name)

	#methods for current domain
	def cur_domain(self):
		'''return list of values in CURRENT domain (if assigned 
		only assigned value is viewed as being in current domain)'''
		vals = []
		if self.is_assigned():
			vals.append(self.get_assigned_name())
		else:
			for i, val in enumerate(self.dom):
				if self.curdom[i]:
					vals.append(val)
		return vals
	
	def in_cur_domain(self, value):
		'''check if value is in CURRENT domain (without constructing list)
		   if assigned only assigned value is viewed as being in current 
		   domain'''
		if not value in self.dom:
		    return False
		if self.is_assigned():
		    return value == self.get_assigned_name()
		else:
		    return self.curdom[self.value_index(value)]
	
	def cur_domain_size(self):
		'''Return the size of the variables domain (without construcing list)'''
		if self.is_assigned():
		    return 1
		else:
		    return(sum(1 for v in self.curdom if v))
	
	def restore_curdom(self):
		'''return all values back into CURRENT domain'''
		for i in range(len(self.curdom)):
			self.curdom[i] = True
	
	#methods for assigning and unassigning
	def is_assigned(self):
	   	return self.assignedName != None
	
	def get_assigned_name(self):
		'''return assigned value .. returns None if is unassigned'''
		return self.assignedName
	
	def assign(self, name):
		'''Used by bt_search. When we assign we remove all other values
		   values from curdom. We save this information so that we can
		   reverse it on unassign'''

		if self.is_assigned() or not self.in_cur_domain(name):
		    print("ERROR: trying to assign variable", self, 
		          "that is already assigned or illegal value (not in curdom)")
		    return
		self.assignedName = name
	
	def unassign(self):
		'''Used by bt_search. Unassign and restore old curdom'''
		if not self.is_assigned():
		    print("ERROR: trying to unassign variable", self, " not yet assigned")
		    return
		self.assignedName = None   	

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

class Suggestion(object):

	def __init__(self, suggestor, responder, weapon, room, suspect):
		self.suggestor = suggestor
		self.responder = responder
		self.weapon = weapon
		self.room = room
		self.suspect = suspect

	def get_cards(self):
		return [self.room, self.weapon, self.suspect]

class Agent(object):
	__metaclass__ = abc.ABCMeta
	'''
	Hand

	create blank instance of Hand for each other player

	instance of csp or something
	gabes a bitch
	'''
	def __init__(self, name):
		'''
		init hand and shit
		opponents

		- DONE Initialize their own hand (given from game class)
		- Initialize ghost hands for 2 oponents (csp*2)
		- DONE Initialize ghost cards for case file (csp)
		'''
		self.name = name
		self.caseFileWeapon = Card(type="Weapon", domain=WEAPONS)
		self.caseFileSuspect = Card(type="Suspect", domain=SUSPECTS)
		self.caseFileRoom = Card(type="Room", domain=ROOMS)

		#NEED a pruning method to prune our current cards from the casefile


	# def assign_order(self, order):
	# 	'''
	# 	Assign an order to agent given. 
	# 	1 goes first, asks 2, 2 asks 3, 3 asks 1. (order is 1->2->3->1...)
	# 	'''
	# 	self.order = order

	def give_hand(self, hand):
		'''
		Ayo hand
		'''
		self.hand = hand

	@abc.abstractmethod
	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card
		'''
		return

	@abc.abstractmethod
	def respond_to_suggestion(self, move):
		'''
		update knowledge base with whatever from game

		Update CSPs

		give a response of a card if you have a card in suggestion, or None otherwise
		'''
		return

	@abc.abstractmethod
	def observe_suggestion(self, suggestion, did_respond):
		'''
		used for observation
		observe a suggestion, and see the response
		suggestion - of type SUGGESTION
		did_respond - boolean to see if the responder sent a card back or not
		'''
		return

	@abc.abstractmethod
	def update_from_response(self, suggestion, response):
		'''
		after making a suggestion, this method will be called to respond to a response

		'''
		return

	@abc.abstractmethod
	def observe_accusation(self, was_accuser, was_correct):
		'''
		made to respond to an accusation
		was_accuser is true if the accusation was made by self, False otherwise
		was_correct is true if the accusation was correct (and the game ends)
		'''
		return

if __name__ == '__main__':
	game = Game()
	# different agents must be initialized here, and then added to the game
