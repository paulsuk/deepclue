''' This Agent assumes that all suggestions made by other Agents indicate that the respective agent does not
possess those cards, and after all enemy agent hands are pruned, the casefile cards are pruned.
This agent accounts for the fact that it operates based off of an assumption, and uses a logic clause
to recognize when this assumption has been broken and it then makes a random accusation.  '''

from game import *
from cspclue import *

class SATAgent(Agent):

	def __init__(self, name):
		super().__init__(name)

		self.pruned_hand_from_casefile = False

		# Initialize CSPs for other Agents
		# Begin by initializing the opposing agent's possible cards (and removing my cards)
		domain = WEAPONS + ROOMS + SUSPECTS
		self.p2cards = [Card(typ = None, domain=domain), Card(typ = None, domain=domain), Card(typ = None, domain=domain), Card(typ = None, domain=domain), Card(typ = None, domain=domain), Card(typ = None, domain=domain)]
		self.p3cards = [Card(typ = None, domain=domain), Card(typ = None, domain=domain), Card(typ = None, domain=domain), Card(typ = None, domain=domain), Card(typ = None, domain=domain), Card(typ = None, domain=domain)]

	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card
		'''

		# INITIAL CHECK ROUTINES
		if not self.pruned_hand_from_casefile:
			for my_card in self.hand.get_cards():
				# Prune values in my hand from enemies hands
				for cards_list in [self.p2cards, self.p3cards]:
					for card in cards_list:
						card.prune_value(my_card.get_assigned_value())

				# Also prune the values that I hold in my hand from the casefile
				if my_card.get_assigned_value() in ROOMS:
					self.caseFileRoom.prune_value(my_card.get_assigned_value())
				elif my_card.get_assigned_value() in WEAPONS:
					self.caseFileWeapon.prune_value(my_card.get_assigned_value())
				elif my_card.get_assigned_value() in SUSPECTS:
					self.caseFileSuspect.prune_value(my_card.get_assigned_value())

			self.pruned_hand_from_casefile = True

		room_copy = ROOMS
		weapon_copy = WEAPONS
		suspect_copy = SUSPECTS
		np.random.shuffle(weapon_copy)
		np.random.shuffle(room_copy)
		np.random.shuffle(suspect_copy)

		weapon_dom = self.caseFileWeapon.cur_domain()
		room_dom = self.caseFileRoom.cur_domain()
		suspect_dom = self.caseFileSuspect.cur_domain()
		np.random.shuffle(weapon_dom)
		np.random.shuffle(room_dom)
		np.random.shuffle(suspect_dom)

		# Check if the weapon, room, and suspect domains are 1.
		if (len(weapon_dom) == 1 and len(room_dom) == 1 and len(suspect_dom) == 1):
			accusation = {}
			self.caseFileWeapon.assign(weapon_dom[0])
			self.caseFileRoom.assign(room_dom[0])
			self.caseFileSuspect.assign(suspect_dom[0])
			accusation['Room'] = self.caseFileRoom
			accusation['Weapon'] = self.caseFileWeapon
			accusation['Suspect'] = self.caseFileSuspect

			# If the enemy player domains are of size 6, then the accusation was
			# determined from information gathered from the enemies. This requires
			# checking that all SAT constraints are satisfied (that the agent assumption
			# is correct).
			if (self.p3cards[0].cur_domain_size() == 6) and (self.p2cards[0].cur_domain_size() == 6):
				if self.check_SAT():
					print("*****Attained a solution through indirect information, SAT Clause Satisfied****")
					return accusation
				else:
					print("*****Assumption was broken, return random accusation*****")
					accusation['Room'] = room_copy[0]
					accusation['Weapon'] = weapon_copy[0]
					accusation['Suspect'] = suspect_copy[0]
					return accusation

			else:
				print("****Attained a solution through direct information*****")
				return accusation
		else:
			suggestion = Suggestion(self.name, self.firstOppName, weapon_dom[0], room_dom[0], suspect_dom[0])
			return suggestion

	def respond_to_suggestion(self, suggestion):
		'''
		update knowledge base with whatever from game

		Update CSPs

		give a response of a card if you have a card in suggestion, or None otherwise
		'''

		for card in self.hand.get_cards():
			if card.get_assigned_value() == suggestion.weapon:
				return card
			elif card.get_assigned_value() == suggestion.room:
				return card
			elif card.get_assigned_value() == suggestion.suspect:
				return card
		return None

	def observe_suggestion(self, suggestion, did_respond):
		'''
		used for observation
		observe a suggestion, and see the response
		suggestion - of type SUGGESTION
		did_respond - boolean to see if the responder sent a card back or not
		'''

		# ASSUMPTION: The suggester does not possess the cards that he suggested
		# Prune suggested cards from suggester, assume player1 is suggester

		if suggestion.suggester == self.firstOppName:
			for card in self.p2cards:
				card.prune_value(suggestion.weapon)
				card.prune_value(suggestion.room)
				card.prune_value(suggestion.suspect)

		elif suggestion.suggester == self.secondOppName:
			for card in self.p3cards:
				card.prune_value(suggestion.weapon)
				card.prune_value(suggestion.room)
				card.prune_value(suggestion.suspect)

		# If all enemy player cards are known, can prune from the casefile
		# Since all cards are pruned at once every time an information is received, only have to check one card

		# If Know one enemy's cards for certain, prune the casefile.
		#for cards_list in [self.p2cards, self.p3cards]:
		if (self.p2cards[0].cur_domain_size() == 6) and (self.p3cards[0].cur_domain_size() == 6):
			for cards_list in [self.p2cards, self.p3cards]:
				dom = cards_list[0].cur_domain()

				#Get the domain of all cards (the same for all cards)
				for value in dom:
					if value in ROOMS:
						self.caseFileRoom.prune_value(value)
					elif value in WEAPONS:
						self.caseFileWeapon.prune_value(value)
					elif value in SUSPECTS:
						self.caseFileSuspect.prune_value(value)

			# Case file domain sizes should now be 1.
		return

	def update_from_response(self, suggestion, response):
		'''
		after making a suggestion, this method will be called to respond to a response
		# IDEA: could prune the shown card from 3rd player's possible cards
		'''

		if response is not None:
			if response.typ == 'Weapon':
				self.caseFileWeapon.prune_value(response.get_assigned_value())
			elif response.typ == 'Room':
				self.caseFileRoom.prune_value(response.get_assigned_value())
			else:
				self.caseFileSuspect.prune_value(response.get_assigned_value())

		return

	def observe_accusation(self, was_accuser, was_correct):
		'''
		made to respond to an accusation
		was_accuser is true if the accusation was made by self, False otherwise
		was_correct is true if the accusation was correct (and the game ends)
		'''

		return

	def reset(self):
		''' Resets all the init values so that the game can be re-run '''

		super().reset()
		self.pruned_hand_from_casefile = False

		# Initialize CSPs for other Agents
		# Begin by initializing the opposing agent's possible cards (and removing my cards)
		domain = WEAPONS + ROOMS + SUSPECTS
		self.p2cards = [Card(typ = None, domain=domain)]*6
		self.p3cards = [Card(typ = None, domain=domain)]*6

		return

	def check_SAT(self):
		''' Check the Satisfiability clause constraint '''

		# First, populate the dictionary which will test the satisfiability clause
		SAT_dict = {v:{"CF": False, "p1": False, "p2": False, "p3": False} for v in ROOMS+WEAPONS+SUSPECTS}
		for card in self.hand.cards:
			SAT_dict[card.get_assigned_value()]["p1"] = True
		for card in [self.caseFileSuspect, self.caseFileWeapon, self.caseFileRoom]:
			SAT_dict[card.get_assigned_value()]["CF"] = True
		for value in self.p2cards[0].cur_domain():
			SAT_dict[value]["p2"] = True
		for value in self.p3cards[0].cur_domain():
			SAT_dict[value]["p3"] = True

		# Now, have to check that all statements satisfy the main clause that encompasses
		# The rules of the game.

		# We perform the AND operation using multiplication *. The OR operation is done using a +.
		# We form a set of conjuctions and the final clause must be True
		# for the accusation to hold

		locations = ["CF", "p1", "p2", "p3"]
		one_place = 1
		only_one_place = 1
		room_category = 1
		weapon_category = 1
		suspect_category = 1
		for value in ROOMS+WEAPONS+SUSPECTS:

			# 1. Each card in at least one place
			one_place *= SAT_dict[value]["CF"] or SAT_dict[value]["p1"] or SAT_dict[value]["p2"] or SAT_dict[value]["p3"]

			# 2. If a card is in one place, it cannot be in another place
			for i in range(len(locations)):
				only_one_place *= not SAT_dict[value][locations[i%4]] or (not (SAT_dict[value][locations[(i+1)%4]] or SAT_dict[value][locations[(i+2)%4]] or SAT_dict[value][locations[(i+3)%4]]))

			# 3. There is at least one card in each category in the Case FIle
			for i in range(len(locations)):
				if value in ROOMS:
					room_category +=  SAT_dict[value][locations[i]]
				elif value in WEAPONS:
					weapon_category +=  SAT_dict[value][locations[i]]
				elif value in SUSPECTS:
					suspect_category +=  SAT_dict[value][locations[i]]
		one_in_each_category = room_category and weapon_category and suspect_category

		# 4. No two cards in each category can both be in the case file
		no_two_cards_in_cf = 1
		room_len = len(ROOMS)
		weapons_len = len(WEAPONS)
		suspects_len = len(SUSPECTS)
		for i in range(len(ROOMS)):
			no_two_cards_in_cf *= not SAT_dict[ROOMS[i%room_len]]["CF"] or not \
			(SAT_dict[ROOMS[(i+1)%room_len]]["CF"] \
			or SAT_dict[ROOMS[(i+2)%room_len]]["CF"] \
			or SAT_dict[ROOMS[(i+3)%room_len]]["CF"] \
			or SAT_dict[ROOMS[(i+4)%room_len]]["CF"]\
			 or SAT_dict[ROOMS[(i+5)%room_len]]["CF"] or \
			 SAT_dict[ROOMS[(i+6)%room_len]]["CF"] or \
			 SAT_dict[ROOMS[(i+7)%room_len]]["CF"] or \
			 SAT_dict[ROOMS[(i+8)%room_len]]["CF"] )
		for i in range(len(WEAPONS)):
			no_two_cards_in_cf *= not SAT_dict[WEAPONS[i%room_len]]["CF"] or not \
			(SAT_dict[WEAPONS[(i+1)%weapons_len]]["CF"] \
			or SAT_dict[WEAPONS[(i+2)%weapons_len]]["CF"] \
			or SAT_dict[WEAPONS[(i+3)%weapons_len]]["CF"] \
			or SAT_dict[WEAPONS[(i+4)%weapons_len]]["CF"]\
			 or SAT_dict[WEAPONS[(i+5)%weapons_len]]["CF"])
		for i in range(len(SUSPECTS)):
			no_two_cards_in_cf *= not SAT_dict[SUSPECTS[i%room_len]]["CF"] or not \
			(SAT_dict[SUSPECTS[(i+1)%suspects_len]]["CF"] \
			or SAT_dict[SUSPECTS[(i+2)%suspects_len]]["CF"] \
			or SAT_dict[SUSPECTS[(i+3)%suspects_len]]["CF"] \
			or SAT_dict[SUSPECTS[(i+4)%suspects_len]]["CF"]\
			 or SAT_dict[SUSPECTS[(i+5)%suspects_len]]["CF"])

		# Now, if the rules of the game are satisfied, this clause will
		# be evaluated to True.

		return one_place and only_one_place and one_in_each_category and no_two_cards_in_cf
