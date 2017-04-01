from cspclue import *
import abc
import time
import functools
import numpy as np
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

# Seems like we will no longer need to do the conversion
# total = ROOMS + WEAPONS + SUSPECTS
# word_to_num = {k:v for k,v in list(enumerate(total))}
# num_to_word = {v:k for k,v in word_to_num.items()}


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

	def init_players(self, agent1, agent2, agent3):
		'''
		Adds 3 agents, initializes them and gives them cards

		TODO: check if agents are all classes/subclasses of Agent
		'''
		hand1, hand2, hand3 = self._distribute_cards
		agent1.give_hand(hand1)
		agent2.give_hand(hand2)
		agent3.give_hand(hand3)

		self.agents = np.shuffle(np.array([agent1, agent2, agent3]))

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
						finished = True
					else:
						isNotEliminated[i] = False

			if not any(isNotEliminated):
				# noone can make a move
				return
			i = (i + 1) % 3
		return suggestor

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

	def case_file_cards(self):
		return [self.caseFileRoom, self.caseFileWeapon, self.caseFileSuspect]


class Hand(object):
	'''
	6 cards
	'''
	def __init__(self):
		'''
		Initialize 6 empty card objects into hand
		'''
		self.cards = [Card('Room', 'needtochangethis')]*6

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
		for card in self.hand:
			if card.typ == 'Weapon':
				self.caseFileWeapon.prune_value(card.assignedValue)
			else if card.typ == 'Room':
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
	def observe_accusation(self, was_accuser, was_correct):
		'''
		made to respond to an accusation
		was_accuser is true if the accusation was made by self, False otherwise
		was_correct is true if the accusation was correct (and the game ends)
		'''
		return


if __name__ == '__main__':
	game = Game()
	agent1 = Agent()
	game.init_players()
	game.play
