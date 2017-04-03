''' This Agent assumes that all suggestions made by other Agents indicate that the respective agent does not
possess those cards, and after all enemy agent hands are pruned, the casefile cards are pruned.
Shows cards randomly. '''

from game import *
from cspclue import *

class PruneEnemiesAgent(Agent):

	def __init__(self, name):
		#super(Agent, self).__init__()
		super().__init__(name)

		self.pruned_hand_from_casefile = False

		# Initialize CSPs for other Agents
		# Begin by initializing the opposing agent's possible cards (and removing my cards)
		domain = WEAPONS + ROOMS + SUSPECTS
		self.p1cards = [Card(typ = None, domain=domain)]*6
		self.p2cards = [Card(typ = None, domain=domain)]*6

		# Create the constraints for the player cards
		self.p1constraint = Constraint(name = 'p1_constraint', scope = self.p1cards)
		self.p2constraint = Constraint(name = 'p2_constraint', scope = self.p2cards)

	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card
		'''

		# INITIAL CHECK ROUTINES
		if not self.pruned_hand_from_casefile:
			print("****Gabe's Cards:****")
			for my_card in self.hand.get_cards():
				print(my_card.get_assigned_value())
				# Prune values in my hand from enemies hands
				for cards_list in [self.p1cards, self.p2cards]:
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


		weapon_dom = self.caseFileWeapon.cur_domain()
		room_dom = self.caseFileRoom.cur_domain()
		suspect_dom = self.caseFileSuspect.cur_domain()
		np.random.shuffle(weapon_dom)
		np.random.shuffle(room_dom)
		np.random.shuffle(suspect_dom)

		if (len(weapon_dom) == 1 and len(room_dom) == 1 and len(suspect_dom) == 1):
			accusation = {}
			self.caseFileWeapon.assign(weapon_dom[0])
			self.caseFileRoom.assign(room_dom[0])
			self.caseFileSuspect.assign(suspect_dom[0])
			accusation['Room'] = self.caseFileRoom
			accusation['Weapon'] = self.caseFileWeapon
			accusation['Suspect'] = self.caseFileSuspect

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
			for card in self.p1cards:
				card.prune_value(suggestion.weapon)
				card.prune_value(suggestion.room)
				card.prune_value(suggestion.suspect)

		elif suggestion.suggester == self.secondOppName:
			for card in self.p2cards:
				card.prune_value(suggestion.weapon)
				card.prune_value(suggestion.room)
				card.prune_value(suggestion.suspect)

		# If all enemy player cards are known, can prune from the casefile
		# Since all cards are pruned at once every time an information is received, only have to check one card

		# If Know one enemy's cards for certain, prune the casefile.
		for cards_list in [self.p1cards, self.p2cards]:
			if (cards_list[0].cur_domain_size() == 6):
				#Get the domain of all cards (the same for all cards)
				dom = cards_list[0].cur_domain()
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
		self.p1cards = [Card(typ = None, domain=domain)]*6
		self.p2cards = [Card(typ = None, domain=domain)]*6

		# Create the constraints for the player cards
		self.p1constraint = Constraint(name = 'p1_constraint', scope = self.p1cards)
		self.p2constraint = Constraint(name = 'p2_constraint', scope = self.p2cards)

		return
