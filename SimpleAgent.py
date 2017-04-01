from game import *
	'''
	SimpleAgent:
	- Makes random guess from current domain of the casefile cards
	- Makes accusation only when 100 percent certain
	- Does not consider oponents guesses/responses
	- Prunes based on answers as the suggestor and response from the responder
	'''
class SimpleAgent(Agent):

	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card
		'''
		weapon_dom = np.shuffle(self.caseFileWeapon.cur_dom())
		room_dom = np.shuffle(self.caseFileRoom.cur_dom())
		suspect_dom = np.shuffle(self.caseFileSuspect.cur_dom())

		if (self.caseFileWeapon.cur_domain_size() == 1 and self.caseFileRoom.cur_domain_size() == 1 and self.caseFileSuspect.cur_domain_size() == 1):
			accusation = {}
			accusation['Room'] = self.caseFileRoom
			accusation['Weapon'] = self.caseFileWeapon
			accusation['Suspect'] = self.caseFileSuspect
			return accusation
		else:
			suggestion = Suggestion(self.name, weapon_dom[0], room_dom[0], suspect_dom[0])
			return suggestion

	def respond_to_suggestion(self, suggestion):
		'''
		update knowledge base with whatever from game

		Update CSPs

		give a response of a card if you have a card in suggestion, or None otherwise
		'''

		for card in self.Hand:
			if card.assignedValue == suggestion.weapon:
				return card
			else if card.assignedValue == suggestion.room:
				return card
			else if card.assignedValue == suggestion.suspect:
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
			else if response.typ == 'Room':
				self.caseFileRoom.prune_value(response.assignedValue)
			else:
				self.caseFileSuspect.prune_value(response.assignedValue)	
		return

	def observe_accusation(self, was_accuser, was_correct):
		'''
		made to respond to an accusation
		accuser_name is name of accuser
		was_correct is true if the accusation was correct (and the game ends)
		'''
		return

if __name__ == '__main__':
	agent = SimpleAgent('Player1')