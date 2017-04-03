from game import *
	
	#ProbAgent has the same logic
	#Make guess is based on probabilities
	

class ProbAgent(Agent):
	def __init__(self, name):
		super().__init__(name)

		#Make opponent hands
		self.first_opponent_hand = Hand()
		self.second_opponent_hand = Hand()

		#Sets to keep track of potential domains for each hand
		self.first_opponent_sets = []
		self.second_opponent_sets = []

		#Keep track of prev suggestion
		self.past_suggestion = [None]*3

	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card

		Update player
		Update casefile
		Make guess based on values not in sets
		'''
		weapon_dom = self.caseFileWeapon.cur_domain()
		room_dom = self.caseFileRoom.cur_domain()
		suspect_dom = self.caseFileSuspect.cur_domain()

		#For the first tern - randomly make a suggestion
		if None in self.past_suggestion:
			#Prune agents cards from opponents' hands
			self.first_opponent_hand.pruneHand(self.hand)
			self.second_opponent_hand.pruneHand(self.hand)

			np.random.shuffle(weapon_dom)
			np.random.shuffle(room_dom)
			np.random.shuffle(suspect_dom)

			self.past_suggestion[0] = weapon_dom[0]
			self.past_suggestion[1] = room_dom[0]
			self.past_suggestion[2] = suspect_dom[0]

			suggestion = Suggestion(self.name, self.firstOppName, weapon_dom[0], room_dom[0], suspect_dom[0])
			return suggestion

		#Update the player's hands and sets
		self._update_player(self.first_opponent_hand, self.first_opponent_sets)
		self._update_player(self.second_opponent_hand, self.second_opponent_sets)
		
		#Prune assigned values in one hand from the other
		self._update_each_other()

		#Prune assigned values from the hands from the cur dom of the casefile
		self._update_case(self.first_opponent_hand)
		self._update_case(self.second_opponent_hand)

		print("Player {}'s set: {}".format(self.firstOppName, self.first_opponent_sets))
		print("Player {}'s set: {}".format(self.secondOppName, self.second_opponent_sets))

		print("CF: W{}: R:{} S:{}".format(self.caseFileWeapon.cur_domain(), self.caseFileRoom.cur_domain(), self.caseFileSuspect.cur_domain()))

		prob = self._find_probability()

		print("PROBABILITY of correctly guessing based on hands: {}%".format(prob))
		print("PROBABILITY of correctly guessing weapon: {}%".format(self._find_probability_weapon()))
		print("PROBABILITY of correctly guessing suspect: {}%".format(self._find_probability_suspect()))
		print("PROBABILITY of correctly guessing room: {}%".format(self._find_probability_room()))

		#Make accusation
		if (self.caseFileWeapon.cur_domain_size() == 1 and self.caseFileRoom.cur_domain_size() == 1 and self.caseFileSuspect.cur_domain_size() == 1):
			room_value = self.caseFileRoom.cur_domain()[0]
			weapon_value = self.caseFileWeapon.cur_domain()[0]
			suspect_value = self.caseFileSuspect.cur_domain()[0]

			self.caseFileRoom.assign(room_value)
			self.caseFileWeapon.assign(weapon_value)
			self.caseFileSuspect.assign(suspect_value)

			accusation = {}
			accusation['Room'] = self.caseFileRoom
			accusation['Weapon'] = self.caseFileWeapon
			accusation['Suspect'] = self.caseFileSuspect
			return accusation
		
		#Make suggestion - keep as close to prev suggestion as possible
		else:
			if self._find_probability_weapon() < 50:
				new_dom = self._smaller_dom(weapon_dom, WEAPONS)
				np.random.shuffle(new_dom)
				self.past_suggestion[0] = weapon_dom[0]
				print("Guess Weapon from: {}".format(new_dom))
			else:
				np.random.shuffle(weapon_dom)
				self.past_suggestion[0] = weapon_dom[0]

			if self._find_probability_room() < 50:
				new_dom = self._smaller_dom(room_dom, ROOMS)
				np.random.shuffle(new_dom)
				self.past_suggestion[1] = room_dom[0]
				print("Guess Room from: {}".format(new_dom))
			else:
				np.random.shuffle(room_dom)
				self.past_suggestion[1] = room_dom[0]

			if self._find_probability_suspect() < 50:
				new_dom = self._smaller_dom(suspect_dom, SUSPECTS)
				np.random.shuffle(new_dom)
				self.past_suggestion[2] = suspect_dom[0]
				print("Guess Suspect from: {}".format(new_dom))
			else:
				np.random.shuffle(suspect_dom)
				self.past_suggestion[2] = suspect_dom[0]

			suggestion = Suggestion(self.name, self.firstOppName, self.past_suggestion[0], self.past_suggestion[1], self.past_suggestion[2])
			return suggestion

	def _smaller_dom(self, cur_dom, typ):
		'''
		Return new current domain where the elements from the domain
		are removed
		'''
		#Remove empty lists from sets
		set1 = [x for x in self.first_opponent_sets if x]
		self.first_opponent_sets = set1
		set2 = [x for x in self.second_opponent_sets if x]
		self.second_opponent_sets = set2
		
		dom1 = []
		dom2 = []

		for domain in self.first_opponent_sets:
			for card in domain:
				if card in typ:
					dom1.append(card)
		print('CUR DOM1: {}'.format(dom1))
		for domain in self.second_opponent_sets:
			for card in domain:
				if card in typ:
					dom2.append(card)
		print('CUR DOM2: {}'.format(dom2))

		dom = list(set(dom1+dom2))
		dom = dom+cur_dom

		new_dom = [card for card in dom if (dom.count(card) == 1 and card in cur_dom)]

		return new_dom


	def respond_to_suggestion(self, suggestion):
		'''
		update knowledge base with whatever from game

		Update CSPs

		give a response of a card if you have a card in suggestion, or None otherwise

		CSPAgent: Return room last (becomes more rooms - harder to figure out)
		'''

		for card in self.hand.get_cards():
			if card.assignedValue == suggestion.weapon:
				return card
			elif card.assignedValue == suggestion.suspect:
				return card
			elif card.assignedValue == suggestion.room:
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
				self._add_domain(suggestion, self.first_opponent_hand, self.first_opponent_sets)
			elif suggestion.responder == self.secondOppName:
				self._add_domain(suggestion, self.second_opponent_hand, self.second_opponent_sets)
			
		#If opponent did not respond, they do not have the suggested
		#Weapon, room or suspect. Prune these from their cards.
		#Also, prune values from domains in sets
		#NOTE: Self is second responder
		else:
			if suggestion.responder == self.firstOppName:
				self._prune_sug(suggestion, self.first_opponent_hand, self.first_opponent_sets)

	def update_from_response(self, suggestion, response):
		'''
		after making a suggestion, this method will be called to respond to a response

		- Doesnt have 
			- prune from domain of sets
			- prune from paul's hand
		- Does have 
			- prune domain from sets
			- prune from casefile
			- add response to non assigned value
		'''
		if response is not None:
			#Update casefile - can't have the response
			if response.typ == 'Weapon':
				self.caseFileWeapon.prune_value(response.assignedValue)
			elif response.typ == 'Room':
				self.caseFileRoom.prune_value(response.assignedValue)
			else:
				self.caseFileSuspect.prune_value(response.assignedValue)


			if suggestion.responder == self.firstOppName:

				#Add value to responder's hand
				assigned = self.first_opponent_hand.get_assigned_card_values()
				if response.assignedValue in assigned:
					return
				else:
					if None in assigned:
						card = Card(response.typ, response.assignedValue, response.cur_domain())
						self.first_opponent_hand.add_card(card)

			else:

				#Add value to responder's hand
				assigned = self.second_opponent_hand.get_assigned_card_values()

				if response.assignedValue in assigned:
					return
				else:
					if None in assigned:
						card = Card(response.typ, response.assignedValue, response.cur_domain())
						self.second_opponent_hand.add_card(card)

		#If did not respond
		else:
			#If first responder says no - prune suggestion from cards and domain
			self._prune_sug(suggestion, self.first_opponent_hand, self.first_opponent_sets)

			#If second responder says no - response must be in casefile!
			if suggestion.responder == self.secondOppName:
				if self.caseFileWeapon.cur_domain_size() != 1:
					if self.caseFileWeapon.in_cur_domain(suggestion.weapon):
						print('**************FOUND WEAPON BC LUCKY GUESS****************')
						self._prune_all(self.caseFileWeapon, suggestion.weapon)
				if self.caseFileSuspect.cur_domain_size() != 1:
					if self.caseFileSuspect.in_cur_domain(suggestion.suspect):
						self._prune_all(self.caseFileSuspect, suggestion.suspect)
						print('*************FOUND SUSPECT BC LUCKY GUESS****************')
				if self.caseFileRoom.cur_domain_size() != 1:
					if self.caseFileRoom.in_cur_domain(suggestion.room):
						self._prune_all(self.caseFileRoom, suggestion.room)
						print('*************FOUND ROOM BC LUCKY GUESS*******************')

				print('Case file W:{} R:{} S:{}'.format(self.caseFileWeapon.cur_domain(), self.caseFileRoom.cur_domain(), self.caseFileSuspect.cur_domain()))

	def observe_accusation(self, was_accuser, was_correct):
		'''
		made to respond to an accusation
		accuser_name is name of accuser
		was_correct is true if the accusation was correct (and the game ends)
		'''
		return
	
	def reset(self):
		'''
		to reset for a new game!
		'''
		self.first_opponent_hand = Hand()
		self.second_opponent_hand = Hand()
		
		self.first_opponent_sets = []
		self.second_opponent_sets = []

		self.past_suggestion = [None]*3

	def _update_case(self, hand):
		'''
		Prune assigned values of cards in hand from casefile
		'''
		for card in hand.get_cards():
			if card.is_assigned():
				if card.typ == 'Weapon' and self.caseFileWeapon.in_cur_domain(card.assignedValue):
					self.caseFileWeapon.prune_value(card.assignedValue)
				elif card.typ == 'Room' and self.caseFileRoom.in_cur_domain(card.assignedValue):
					self.caseFileRoom.prune_value(card.assignedValue)
				elif card.typ == 'Suspect' and self.caseFileSuspect.in_cur_domain(card.assignedValue):
					self.caseFileSuspect.prune_value(card.assignedValue)
				else:
					continue

	def _update_player(self, hand, sets):
		'''
		Update player's set and hand by pruning cards with domain of length 1
		and the entire domain if a value in it is already assigned to a card

		If casefile value is known, remove value from domain
		'''
		assigned = set(hand.get_assigned_card_values())
		#print("Assigned: {}".format(hand.get_assigned_card_values()))
		copy = sets
		for i, domain in enumerate(sets):
			#Remove domains of size 1
			if len(domain) == 1 and domain[0] not in hand.get_assigned_card_values() and None in hand.get_assigned_card_values():
				print('********************** ASSIGNED BECAUSE SIZE 1: UPDATE PLAYERS {} *************************'.format(domain[0]))
				card = Card(typ=None, name=domain[0], domain=domain)
				card.update_type()
				hand.add_card(card)
				#print("ADDED {} so now {}".format(domain, hand.get_cards()))
			if self.caseFileWeapon.cur_domain_size() == 1:
				if self.caseFileWeapon.cur_domain()[0] in domain:
					new_dom = [x for x in domain if (x != self.caseFileWeapon.cur_domain()[0])]
					sets[i] = new_dom
					print('********************** CHANGED BC CF WEAPON KNOWN *************************')
			if self.caseFileSuspect.cur_domain_size() == 1:
				if self.caseFileSuspect.cur_domain()[0] in domain:
					new_dom = [x for x in domain if (x != self.caseFileSuspect.cur_domain()[0])]
					sets[i] = new_dom
					print('********************** CHANGED BC CF SUSPECT KNOWN *************************')
			if self.caseFileRoom.cur_domain_size() == 1:
				if self.caseFileRoom.cur_domain()[0] in domain:
					new_dom = [x for x in domain if (x != self.caseFileRoom.cur_domain()[0])]
					sets[i] = new_dom
					print('********************** CHANGED BC CF ROOM KNOWN *************************')

		for domain in copy:
			#Prune if already assigned
			overlap = assigned.intersection(domain)
			if len(overlap) > 0:
				sets.remove(domain)
			#remove empty domains and already considered domains
			elif len(domain) == 1:
				sets.remove(domain)

	def _update_each_other(self):
		'''
		Prune assigned values of cards in one hand from the other
		Vice versa
		'''
		assigned_1 = set(self.first_opponent_hand.get_assigned_card_values())
		assigned_2 = set(self.second_opponent_hand.get_assigned_card_values())
			
		for value in assigned_1:
			if value != None:
				for card in self.second_opponent_hand.get_cards():
					if card.in_cur_domain(value):
						card.prune_value(value)
		for value in assigned_2:
			if value != None:
				for card in self.first_opponent_hand.get_cards():
					if card.in_cur_domain(value):
						card.prune_value(value)

	def _prune_all(self, card, name):
		'''
		Prune all values from card except name
		'''
		for c in card.cur_domain():
			if c != name:
				card.prune_value(c)


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
		copy = sets
		#Remove from sets
		if len(sets) != 0:
			for i, domain in enumerate(sets):
				new_dom = [x for x in domain if (x != suggestion.suspect or x!= suggestion.room or x!=suggestion.weapon)]
				if new_dom != domain:
					print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXX CHANGE MADE TO SETS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
				sets[i] = new_dom


	def _add_domain(self, suggestion, hand, sets):
		'''
		Helper fn for observe_suggestion:
		- add constraints to represent potential values for a card
		'''
		domain = []
		my_cards = self.hand.get_assigned_card_values()
		#Populate domain
		for card in hand.get_cards():
			#Do not add constraint if already know what card (or a card that) was shown
			if (card.get_assigned_value() == suggestion.weapon or card.get_assigned_value() == suggestion.room 
				or card.get_assigned_value() == suggestion.suspect):
				return

			if card.in_cur_domain(suggestion.weapon) and suggestion.weapon not in domain and suggestion.weapon not in my_cards:
				domain.append(suggestion.weapon)
			if card.in_cur_domain(suggestion.room) and suggestion.room not in domain and suggestion.weapon not in my_cards:
				domain.append(suggestion.room)
			if card.in_cur_domain(suggestion.suspect) and suggestion.suspect not in domain and suggestion.weapon not in my_cards:
				domain.append(suggestion.suspect)
			
		#If only one value - assign value to an unassigned card 
		if len(domain) == 1 and domain[0] not in hand.get_assigned_card_values() and None in hand.get_assigned_card_values():
			#print("Domain: {}".format(domain))
			print("************************ ASSIGNED BC SIZE 1: ADD DOMAIN {} **************************".format(domain[0]))
			card = Card(typ=None, name=domain[0], domain=domain)
			card.update_type()
			hand.add_card(card)
			#print("ADDED {} so now {}".format(domain, hand.get_cards()))

		else:
			sets.append(domain)

	def _find_probability(self):
		num_weapons = 0
		num_rooms = 0
		num_suspects = 0
		for card in self.hand.get_cards():
			if card.typ == 'Weapon':
				num_weapons +=1 
			elif card.typ == 'Room':
				num_rooms+=1
			else:
				num_suspects+=1
		for card in self.first_opponent_hand.get_cards():
			if card.assignedValue != None:
				if card.typ == 'Weapon':
					num_weapons +=1 
				elif card.typ == 'Room':
					num_rooms+=1
				else:
					num_suspects+=1
		for card in self.second_opponent_hand.get_cards():
			if card.assignedValue != None:
				if card.typ == 'Weapon':
					num_weapons +=1 
				elif card.typ == 'Room':
					num_rooms+=1
				else:
					num_suspects+=1	
		return (1/(6-num_weapons))*(1/(6-num_suspects))*(1/(9-num_rooms))*100

	def _find_probability_room(self):
		return 100/self.caseFileRoom.cur_domain_size()
	
	def _find_probability_weapon(self):
		return 100/self.caseFileWeapon.cur_domain_size()

	def _find_probability_suspect(self):
		return 100/self.caseFileSuspect.cur_domain_size()
		