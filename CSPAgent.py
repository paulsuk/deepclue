from game import *

	'''
	CSPAgent focuses on 'observe_suggestion()' function.
	- It observes the exchange as first opponent is the suggester
	'''

class CSPAgent(Agent):
	def __init__(self, name):
		super(Agent, self).__init__(name)

		self.first_opponent_hand = pruneHand(Hand())
		self.second_opponent_hand = pruneHand(Hand())

		#self.CSP_first_opponent = CSP(self.firstOppName, self.first_opponent_hand.getCards())
		#self.CSP_second_opponent = CSP(self.secondOppName, self.second_opponent_hand.getCards())

		self.first_opponent_sets = []
		self.second_opponent_sets = []

	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card
		'''
		_update(self)

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

		CSPAgent: Return room last (becomes more rooms - harder to figure out)
		'''

		for card in self.Hand:
			if card.assignedValue == suggestion.weapon:
				return card
			else if card.assignedValue == suggestion.suspect:
				return card
			else if card.assignedValue == suggestion.room:
				return card
		return None

	def observe_suggestion(self, suggestion, did_respond):
		'''
		used for observation
		observe a suggestion, and see the response
		suggestion - of type SUGGESTION
		did_respond - boolean to see if the responder sent a card back or not

		CSPAgent: Add constraints to set
		'''
		#Add constraints to one card
		if did_respond:
			if suggestion.responder == self.firstOppName:
				_update_set(suggestion, self.first_opponent_hand, self.first_opponent_sets)
			else:
				_update_set(suggestion, self.second_opponent_hand, self.second_opponent_sets)
			
		#If opponent did not respond, they do not have the suggested
		#Weapon, room or suspect. Prune these from their cards.
		#Also, prune values from domains in sets
		else:
			if suggestion.responder == self.firstOppName:
				_prune_sug(suggestion, self.first_opponent_hand, self.first_opponent_sets)
			else:
				_prune_sug(suggestion, self.second_opponent_hand, self.second_opponent_sets)
	
	def _update_case(self, hand):
		for card in hand.get_cards():
			

	def _update_player(self, hand, sets):
		'''
		Update player's set and hand by pruning cards with domain of length 1
		and the entire domain if a value in it is already assigned to a card
		'''
		assigned = set(hand.get_assigned_card_values())
		copy = sets
		for domain in sets:
			#Remove domains of size 1
			if len(domain) == 1 and domain[0] not in assigned:
				_assign(hand, domain[0])
		for domain in copy:
			#Prune if already assigned
			overlap = assigned.intersect(domain)
			if len(overlap) > 0:
				sets.remove(domain)

			
	def _assign(self, hand, value):
		'''
		Assign value to a non assigned card in hand
		'''
		for card in hand.get_cards():
			if card.assignedValue == None and domain[0] in card.cur_domain():
				card.assign(domain[0])
				card.update_type()
				break

	def _prune_sug(self, suggestion, hand, sets):
		'''
		Prune all elements of suggestion from all cards in hand
		'''
		#Remove from curdom
		for card in hand.get_cards():
			if card.assignedValue == None:
				card.prune_value(suggestion.weapon)
				card.prune_value(suggestion.room)
				card.prune_value(suggestion.suspect)
		#Remove from sets
		for domain, i in enumerate(sets):
			domain = [x for x in domain if (x != suggestion.suspect or x!= suggestion.room or x!=suggestion.weapon)]
			sets[i] = domain

	def _update_set(self, suggestion, hand, sets):
		'''
		Helper fn for observe_suggestion:
		- add constraints to represent potential values for a card
		'''
		domain = []
		#Populate domain
		for card in hand.get_cards():
			#Do not add constraint if already know what card (or a card that) was shown
			if (card.get_assigned_value() == suggestion.weapon or card.get_assigned_value() == suggestion.room 
				or card.get_assigned_value() == suggestion.suspect):
				return

			if suggestion.weapon in card.cur_domain() and suggestion.weapon not in domain:
				domain.append(suggestion.weapon)
			if suggestion.room in card.cur_domain() and suggestion.room not in domain:
				domain.append(suggestion.room)
			if suggestion.suspect in card.cur_domain() and suggestion.suspect not in domain:
				domain.append(suggestion.suspect)
			
		#If only one value - assign value to an unassigned card 
		if len(domain) == 1:
			_assign(hand, domain[0])
		else:
			sets.append(domain)


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
	agent = CSPAgent('player1')
