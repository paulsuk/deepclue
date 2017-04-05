from game import *

class SimpleRandom(Agent):

	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card
		'''
		weapon_dom = self.caseFileWeapon.cur_domain()
		room_dom = self.caseFileRoom.cur_domain()
		suspect_dom = self.caseFileSuspect.cur_domain()

		np.random.shuffle(weapon_dom)
		np.random.shuffle(room_dom)
		np.random.shuffle(suspect_dom)

		if (len(weapon_dom) == 1 and len(room_dom) == 1 and len(suspect_dom) == 1):
			room_value = self.caseFileRoom.cur_domain()[0]
			weapon_value = self.caseFileWeapon.cur_domain()[0]
			suspect_value = self.caseFileSuspect.cur_domain()[0]

			self.caseFileRoom.assign(room_value)
			self.caseFileWeapon.assign(weapon_value)
			self.caseFileSuspect.assign(suspect_value)

			accusation = {}
			accusation['Room'] = Card(typ="Room", name='Hall')
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
			if card.assignedValue == suggestion.weapon:
				return card
			elif card.assignedValue == suggestion.room:
				return card
			elif card.assignedValue == suggestion.suspect:
				return card
		return None

	def observe_suggestion(self, suggestion, did_respond):
		'''
		used for observation
		observe a suggestion, and see the response
		suggestion - of type SUGGESTION
		did_respond - boolean to see if the responder sent a card back or not
		'''
		return

	def update_from_response(self, suggestion, response):
		'''
		after making a suggestion, this method will be called to respond to a response

		'''
		if response is not None:
			if response.typ == 'Weapon':
				self.caseFileWeapon.prune_value(response.assignedValue)
			elif response.typ == 'Room':
				self.caseFileRoom.prune_value(response.assignedValue)
			else:
				self.caseFileSuspect.prune_value(response.assignedValue)	
		return

	def observe_accusation(self, accuser_name, was_correct):
		'''
		made to respond to an accusation
		was_accuser is true if the accusation was made by self, False otherwise
		was_correct is true if the accusation was correct (and the game ends)
		'''
		return



