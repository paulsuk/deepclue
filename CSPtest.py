''' This file is an example file for how to use the CSP with the desired variables
and for the desired application. Use this as an example to build the game with the CSP'''

from cspclue import *
import time
import functools
import numpy as np
import pdb
from game import *

if __name__ == '__main__':

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

	# Create CSP instances for every player
	player1CSP = CSP('player1CSP', [player1_CF1 ,player1_CF2 ,player1_CF3])
	player2CSP = CSP('player2CSP', [player2_CF1 ,player2_CF2 ,player2_CF3])
	player3CSP = CSP('player3CSP', [player3_CF1 ,player3_CF2 ,player3_CF3])
	csp_list = [player1CSP, player2CSP, player3CSP]

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
