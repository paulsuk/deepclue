from cspclue import *
import abc
import time
import functools
import numpy as np
from SimpleRandom import *
import pdb

'''
Gabe - csp base and how to instantiate and stuff , how to add constraints and stuff
Paul - players doing stuff
Grace - hands

Goals are written in order of importance
CSP based: able to make an accusation once the player has directly received all necessary information.
CSP based: able to make an accusation once the player has indirectly received all necessary information (inferring from answers of other players).
CSP based: able to make a guessed accusation by noticing that other players have received 100% of their required information.
Information Theory Based: able to ask the least amount of questions necessary to attain the goal.

'''

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

		all_cards = self.rooms + self.weapons + self.suspects
		np.random.shuffle(all_cards)

		for i in range(len(all_cards)):
			card = all_cards[i]
			if i % 3 == 0:
				hand1.add_card(card)
			elif i % 3 == 1:
				hand2.add_card(card)
			else:
				hand3.add_card(card)

		return hand1, hand2, hand3

	def init_players(self, agent1, agent2, agent3):
		'''
		Adds 3 agents, initializes them and gives them cards

		TODO: check if agents are all classes/subclasses of Agent
		'''
		hand1, hand2, hand3 = self._distribute_cards()
		agent1.give_hand(hand1)
		agent2.give_hand(hand2)
		agent3.give_hand(hand3)

		self.agents = [agent1, agent2, agent3]
		np.random.shuffle(self.agents)

		player_order_dict = {}
		for i in range(len(self.agents)):
			player_order_dict[i] = self.agents[i].name

		for agent in self.agents:
			agent.init_player_orders(player_order_dict)

	def play_game(self):
		'''
		- keeping track of who's turn is it
		- is game still going/did someone win?
		- tell next player it's their turn
		- returns the player who won's name, and the number of turns it took
		'''
		isNotEliminated = [True]*len(self.agents)
		finished = False
		i = 0

		while not finished:
			if not any(isNotEliminated):
				# noone can make a move
				print("All Players Eliminated!")
				return None, i

			if not isNotEliminated[i]:
				# person can make a move
				suggester = self.agents[i]
				responder = self.agents[(i + 1) % 3]
				observer = self.agents[(i + 2) % 3]
				print("ROUND {}: {}'s TURN TO MOVE".format(i, suggester.name))

				move = suggester.make_move()

				if isinstance(move, Suggestion):
					# suggester made a suggestion

					self._print_suggestion(suggester.name, suggestion)

					card_exchanged = self._made_suggestion(move, suggester, responder, observer)

					if not card_exchanged:
						# ask the next player
						move.responder = observer.name
						card_exchanged = self._made_suggestion(move, suggester, observer, responder)

				else:
					# suggester made an accusation
					was_correct = self._check_accusation(move)
					accuser_name = suggester.name
					suggester.observe_accusation(accuser_name, was_correct)
					responder.observe_accusation(accuser_name, was_correct)
					observer.observe_accusation(accuser_name, was_correct)

					if was_correct:
						finished = True
					else:
						isNotEliminated[i] = False

				i = (i + 1) % 3

		return suggester.name, i

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
		suggester.update_from_response(move, response)

		card_exchanged = response is not None
		observer.update_from_response(move, card_exchanged)

		if card_exchanged:
			print("{} showed {} to {}".format(responder.name, response.getName(), suggester.name))
		else:
			print("{} didn't have any of those cards".format(responder.name))

		return card_exchanged

	def case_file_cards(self):
		return [self.caseFileRoom, self.caseFileWeapon, self.caseFileSuspect]

	def _print_suggestion(self, suggester, suggestion):
		cards = suggestion.get_cards()
		print("suggester suggests: {}".format(cards))

class Hand(object):
	'''
	6 cards
	'''
	def __init__(self):
		'''
		Initialize 6 empty card objects into hand
		'''
		self.cards = [Card('Room', 'needtochangethis', WEAPONS+ROOMS+SUSPECTS)]*6

	def add_card(self, card):
		'''
		Initialize an empty card as card if empty cards exist

		NOTE: MIGHT NEED TO MAKE THIS MORE SPECIFIC TO ENSURE TO TARGETS
		THE RIGHT CARD, for now:
		'''
		for i, c in enumerate(self.cards):
			if c.get_assigned_value() == None:
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

	def get_cards(self):
		return (list(self.cards))

	def pruneHand(self, opponent_hand):
		'''
		Prunes opponent_hand of card values in self.hand 
		'''
		for my_card in self.hand:
			for op_card in opponent_hand:
				op_card.prune_vale(my_card.assignedValue)
		return opponent_hand

class Suggestion(object):

	def __init__(self, suggester, responder, weapon, room, suspect):
		self.suggester = suggester
		self.responder = responder
		self.weapon = weapon
		self.room = room
		self.suspect = suspect

	def get_cards(self):
		return [self.room, self.weapon, self.suspect]

class Agent(metaclass=abc.ABCMeta):
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

		self.caseFileWeapon = Card(typ="Weapon", domain=WEAPONS)
		self.caseFileSuspect = Card(typ="Suspect", domain=SUSPECTS)
		self.caseFileRoom = Card(typ="Room", domain=ROOMS)

		self.CSP = CSP(name, [self.caseFileRoom, self.caseFileSuspect, self.caseFileWeapon])
		roomConstraint = Constraint('Room', scope=[self.caseFileRoom])
		suspectConstraint = Constraint('Suspect', scope=[self.caseFileSuspect])
		weaponConstraint = Constraint('Weapon', scope=[self.caseFileWeapon])

		roomSatisfyingTuples = [[x] for x in ROOMS]
		suspectSatisfyingTuples = [[x] for x in SUSPECTS]
		weaponSatisfyingTuples = [[x] for x in WEAPONS]

		roomConstraint.add_satisfying_tuples(roomSatisfyingTuples)
		suspectConstraint.add_satisfying_tuples(suspectSatisfyingTuples)
		weaponConstraint.add_satisfying_tuples(weaponSatisfyingTuples)

		self.CSP.add_constraint(roomConstraint)
		self.CSP.add_constraint(suspectConstraint)
		self.CSP.add_constraint(weaponConstraint)
		
	def init_player_orders(self, order_dict):
		'''
		order_dict is a dictionary that maps player numbers to their names
		'''

		for key in order_dict:
			if order_dict[key] == self.name:
				self.playerNum = key
				break

		self.firstOppName = order_dict[(self.playerNum + 1) % 3]
		self.secondOppName = order_dict[(self.playerNum + 2) % 3]


	def give_hand(self, hand):
		'''
		Initalize hand
		Prune cards in hand from the casefile domain
		'''
		self.hand = hand
		for card in self.hand.get_cards():
			if card.typ == 'Weapon':
				self.caseFileWeapon.prune_value(card.assignedValue)
			elif card.typ == 'Room':
				self.caseFileRoom.prune_value(card.assignedValue)
			else:
				self.caseFileSuspect.prune_value(card.assignedValue)	

	@abc.abstractmethod
	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card
		'''
		return

	@abc.abstractmethod
	def respond_to_suggestion(self, suggestion):
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
	def observe_accusation(self, accuser_name, was_correct):
		'''
		made to respond to an accusation
		was_accuser is true if the accusation was made by self, False otherwise
		was_correct is true if the accusation was correct (and the game ends)
		'''
		return

if __name__ == '__main__':
	game = Game()
	p1 = SimpleRandom('paul')
	p2 = SimpleRandom('grace')
	p3 = SimpleRandom('gabe')
	game.init_players(p1, p2, p3)

	name, i = game.play_game()
	print("{} won after {} turns".format(name, i))
