from cspclue import *
import abc
import time
import functools
import numpy as np
from PruneEnemies import *
from SimpleRandom import *
from CSPAgent import *
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
			print("player {}'s cards: {}".format(i, self.agents[i].hand.get_cards()))

		for agent in self.agents:
			agent.init_player_orders(player_order_dict)

	def play_game(self):
		'''
		- keeping track of who's turn is it
		- is game still going/did someone win?
		- tell next player it's their turn
		- returns the player who won's name, and the number of turns it took
		'''
		print("Game Starting!")
		print("Case file cards: {}".format(self.case_file_cards()))

		isNotEliminated = [True]*len(self.agents)
		finished = False
		i = 0
		turn_num = 0

		while not finished:
			#print("in the while not finished")
			#print(isNotEliminated)
			if not any(isNotEliminated):
				# noone can make a move
				print("All Players Eliminated!")
				return None, turn_num

			elif isNotEliminated[i]:
				# person can make a move
				suggester = self.agents[i]
				responder = self.agents[(i + 1) % 3]
				observer = self.agents[(i + 2) % 3]
				print("ROUND {}: {}'s TURN TO MOVE".format(turn_num, suggester.name))

				move = suggester.make_move()

				if isinstance(move, Suggestion):
					# suggester made a suggestion

					self._print_suggestion(suggester.name, move)

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
				turn_num += 1

		return suggester.name, turn_num

	def reset(self):
		self._init_cards()
		self._make_case_file()
		players = self.agents
		p1, p2, p3 = players[0], players[1], players[2]
		p1.reset()
		p2.reset()
		p3.reset()
		self.init_players(p1, p2, p3)

	def _check_accusation(self, accusation):
		'''
		Returns True if accusation is correct
		Return False if accusation is incorrect

		accusation is a dict: keys are: <"Room", "Suspect", "Weapon">
		'''
		if accusation["Room"].get_assigned_value() != self.caseFileRoom.get_assigned_value():
			return False
		if accusation["Suspect"].get_assigned_value() != self.caseFileSuspect.get_assigned_value():
			return False
		if accusation["Weapon"].get_assigned_value() != self.caseFileWeapon.get_assigned_value():
			return False
		return True

	def _made_suggestion(self, move, suggester, responder, observer):
		response = responder.respond_to_suggestion(move)
		suggester.update_from_response(move, response)

		card_exchanged = response is not None
		observer.observe_suggestion(move, card_exchanged)

		if card_exchanged:
			print("{} showed {} to {}".format(responder.name, response.get_assigned_value(), suggester.name))
		else:
			print("{} didn't have any of those cards".format(responder.name))

		return card_exchanged

	def case_file_cards(self):
		return [self.caseFileRoom, self.caseFileWeapon, self.caseFileSuspect]

	def _print_suggestion(self, suggester, suggestion):
		cards = suggestion.get_cards()
		print("suggester suggests: {}".format(cards))

if __name__ == '__main__':
	game = Game()
	p1 = SimpleRandom('paul')
	p2 = CSPAgent('grace')
	p3 = PruneEnemiesAgent('gabe')

	game.init_players(p1, p2, p3)

	name, i = game.play_game()
	print("{} won after {} turns".format(name, i))

#	game.reset()

#	name, i = game.play_game()
#	print("{} won after {} turns".format(name, i))
