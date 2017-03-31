from cspclue import *
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

ROOMS = ['Conservatory', 'Hall', 'Lounge', 'Dining Room', 'Kitchen', 'Ballroom', 'Billiard Room', 'Library', 'Study']
WEAPONS = ['Candlestick', 'Revolver', 'Wrench', 'Rope', 'Lead Pipe', 'Knife']
SUSPECTS = ['Miss Scarlett', 'Mrs White', 'Mr Green', 'Mrs Peacock', 'Colonel Mustard', 'Professor Plum']

# Seems like we will no longer need to do the conversion
# total = ROOMS + WEAPONS + SUSPECTS
# word_to_num = {k:v for k,v in list(enumerate(total))}
# num_to_word = {v:k for k,v in word_to_num.items()}

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
		Paul, i started doing this just to test my implementation of the CSP.
		'''
		self.hand = Hand()

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
	#don't know where to put this

	# 1st goal AI: deduces by direct information (only what it is directly shown)
	# 1 CSP, 1 main constraint: all diff constraint on the case Files

	rooms = ['Conservatory', 'Hall', 'Lounge', 'Dining Room', 'Kitchen', 'Ballroom', 'Billiard Room', 'Library', 'Study']
	rooms = list(map(lambda x: Card('Rooms', x), rooms))
	weapons = ['Candlestick', 'Revolver', 'Wrench', 'Rope', 'Lead Pipe', 'Knife']
	weapons = list(map(lambda x: Card('Weapons', x), weapons))
	suspects = ['Miss Scarlett', 'Mrs White', 'Mr Green', 'Mrs Peacock', 'Colonel Mustard', 'Professor Plum']
	suspects = list(map(lambda x: Card('Suspects', x), suspects))
	big_list = rooms+weapons+suspects
	np.random.shuffle(big_list)
	non_casefile_list = []


	# Initiate all agents manually
	player1 = Agent()
	player2 = Agent()
	player3 = Agent()
	not_casefile_list = [] #creates a list without the casefile cards, since they can't be the same for the players
	for i in range(len(big_list)):
		if big_list[i] not in game.case_file_cards():
			non_casefile_list.append(big_list[i])

	player1.hand.cards = non_casefile_list[0:6]
	player2.hand.cards = non_casefile_list[7:12]
	player3.hand.cards = non_casefile_list[13:18]

	#Now, list all variables into the CSP (hands of 3 players and the case file variables)
	variables = player1.hand.cards + player2.hand.cards + player3.hand.cards + game.case_file_cards()

	# Create CSP instances for every player
	player1CSP = CSP('player1CSP', game.case_file_cards())
	player2CSP = CSP('player2CSP', game.case_file_cards())
	player3CSP = CSP('player3CSP', game.case_file_cards())
	csp_list = [player1CSP, player2CSP, player3CSP]

	# Add constraints to each player's CSP. This is for the first,
	#simple AI where the only constrains are that the case files are
	#different and one is of each type (3 in total)

	# Add one constraint for each card, that constraint being that
	#the card has to be one of either the room type, or the weapon type
	#type, or person type

	# Room card constraint
	player1_CF1 = Card('Room', 'p1cfcard', ROOMS)
	player2_CF1 = Card('Room', 'p2cfcard', ROOMS)
	player3_CF1 = Card('Room', 'p3cfcard', ROOMS)
	player1_CF2 = Card('weapons', 'p1cfcard2', WEAPONS)
	player2_CF2 = Card('weapons', 'p2cfcard2', WEAPONS)
	player3_CF2 = Card('weapons', 'p3cfcard2', WEAPONS)
	player1_CF3 = Card('person', 'p1cfcard3', SUSPECTS)
	player2_CF3 = Card('person', 'p2cfcard3', SUSPECTS)
	player3_CF3 = Card('person', 'p3cfcard3', SUSPECTS)

	p1con0 = Constraint('con1', scope = [player1_CF1])
	# Person card constraint
	p1con1 = Constraint('con1', scope = [player1_CF2])
	# Weapon card constraint
	p1con2 = Constraint('con1', scope = [player1_CF3])
	p2con0 = Constraint('con1', scope = [player2_CF1])
	# Person card constraint
	p2con1 = Constraint('con1', scope = [player2_CF2])
	# Weapon card constraint
	p2con2 = Constraint('con1', scope = [player2_CF3])
	p3con0 = Constraint('con1', scope = [player3_CF1])
	# Person card constraint
	p3con1 = Constraint('con1', scope = [player3_CF2])
	# Weapon card constraint
	p3con2 = Constraint('con1', scope = [player3_CF3])
	con_list = [p1con0, p1con1, p1con2]
	print("con1.scope", p1con1.scope)

	# Add the satisfying tuples
	p1con0.add_satisfying_tuples([(['Conservatory']), (['Hall']), (['Lounge']), (['Dining Room']), (['Kitchen']), (['Ballroom']), (['Billiard Room']), (['Library']), (['Study'])])
	p1con1.add_satisfying_tuples([(['Candlestick']), (['Revolver']), (['Wrench']), (['Rope']), (['Lead Pipe']), (['Knife'])])
	p1con2.add_satisfying_tuples([(['Miss Scarlett']), (['Mrs White']), (['Mr Green']), (['Mrs Peacock']), (['Colonel Mustard']), (['Professor Plum'])])

	# Add these to all player's CSP
	player1CSP.add_constraint(p1con0)
	player1CSP.add_constraint(p1con1)
	player1CSP.add_constraint(p1con2)

	for csp in csp_list:
		map(lambda x: csp.add_constraint(x), con_list)

	pdb.set_trace()
