from game import *
	
	#GameTreeProbAgent has the same logic
	#Same as CSPAgent except for make_move()
	#If probability of guessing a type is < 50% - remove
	#sets' values from that type's current domain since
	#there is atleast a 50 or 33 percent chance that a player
	#has one of the cards 

	#ALSO - Shows card that will yield lowest probability in response to
	#a suggestion
	#ALSO - Guess if think opponent will guess on next turn
	
class GameTreeProbAgent(Agent):
	def __init__(self, name):
		super().__init__(name)

		#Make opponent hands
		self.first_opponent_hand = Hand()
		self.second_opponent_hand = Hand()

		#Sets to keep track of potential domains for each hand
		self.first_opponent_sets = []
		self.second_opponent_sets = []

		#Keep track of what each hand (might) know, dict: key is card and percentage
		self.first_opponent_know = {}
		self.second_opponent_know = {}

		self.first_caseFileWeapon = Card(typ="Weapon", domain=WEAPONS)
		self.first_caseFileSuspect = Card(typ="Suspect", domain=SUSPECTS)
		self.first_caseFileRoom = Card(typ="Room", domain=ROOMS)

		self.first_total_cur_dom = 15
		self.second_total_cur_dom = 15

		self.second_caseFileWeapon = Card(typ="Weapon", domain=WEAPONS)
		self.second_caseFileSuspect = Card(typ="Suspect", domain=SUSPECTS)
		self.second_caseFileRoom = Card(typ="Room", domain=ROOMS)

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

			#Initialize the probability for each value for both hands
			#self._init_dict(self.first_opponent_know)
			#self._init_dict(self.second_opponent_know)

			np.random.shuffle(weapon_dom)
			np.random.shuffle(room_dom)
			np.random.shuffle(suspect_dom)

			self.past_suggestion[0] = weapon_dom[0]
			self.past_suggestion[1] = room_dom[0]
			self.past_suggestion[2] = suspect_dom[0]

			suggestion = Suggestion(self.name, self.firstOppName, weapon_dom[0], room_dom[0], suspect_dom[0])
			return suggestion

		#Update the player's hands and sets
		self._update_player(self.first_opponent_hand, self.first_opponent_sets, self.first_opponent_know)
		self._update_player(self.second_opponent_hand, self.second_opponent_sets, self.second_opponent_know)
		
		#Prune assigned values in one hand from the other
		self._update_each_other()

		#Prune assigned values from the hands from the cur dom of the casefile
		self._update_case(self.first_opponent_hand)
		self._update_case(self.second_opponent_hand)

		#Prune opponents assigned cards from the cur dom of the casefile
		self._update_opp_case(self.firstOppName, self.first_opponent_hand)
		self._update_opp_case(self.secondOppName, self.second_opponent_hand)

		#Update dictionaries
		#self._update_dict(self.first_opponent_hand, self.first_opponent_sets, self.first_opponent_know, 
		#	self.first_caseFileWeapon, self.first_caseFileSuspect, self.first_caseFileRoom)
		#self._update_dict(self.second_opponent_hand, self.second_opponent_sets, self.second_opponent_know,
		#	self.second_caseFileWeapon, self.second_caseFileSuspect, self.second_caseFileRoom)

		print("Player {}'s cards: {}".format(self.firstOppName, self.first_opponent_hand.get_cards()))
		print("Player {}'s cards: {}".format(self.secondOppName, self.second_opponent_hand.get_cards()))

		print("Player {}'s set: {}".format(self.firstOppName, self.first_opponent_sets))
		print("Player {}'s set: {}".format(self.secondOppName, self.second_opponent_sets))

		#for key, value in self.first_opponent_know.items():
		#	print("OP1: CARD: {} PROBABILITY: {}".format(key, value))
		#for key, value in self.second_opponent_know.items():
		#	print("OP2: CARD: {} PROBABILITY: {}".format(key, value))

		print("CF: W{}: R:{} S:{}".format(self.caseFileWeapon.cur_domain(), self.caseFileRoom.cur_domain(), self.caseFileSuspect.cur_domain()))
		print("CF {} : W{}: R:{} S:{}".format(self.firstOppName, self.first_caseFileWeapon.cur_domain(), self.first_caseFileRoom.cur_domain(), self.first_caseFileSuspect.cur_domain()))
		print("CF {} : W{}: R:{} S:{}".format(self.secondOppName, self.second_caseFileWeapon.cur_domain(), self.second_caseFileRoom.cur_domain(), self.second_caseFileSuspect.cur_domain()))

		prob = self._find_probability()

		print("CUR DOM PROBABILITY {}: {}".format(self.firstOppName, self.first_total_cur_dom))
		print("CUR DOM PROBABILITY {}: {}".format(self.secondOppName, self.second_total_cur_dom))

		#print("PROBABILITY of correctly guessing based on hands: {}%".format(prob))
		#print("PROBABILITY of correctly guessing weapon: {}%".format(self._find_probability_weapon()))
		#print("PROBABILITY of correctly guessing suspect: {}%".format(self._find_probability_suspect()))
		#print("PROBABILITY of correctly guessing room: {}%".format(self._find_probability_room()))

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
		
		#Make accusation if others are close - at least one section figured out
			'''if (self.first_total_cur_dom < 9 or self.second_total_cur_dom < 9):
			small_room = self._smaller_dom(room_dom, ROOMS)
			small_weapon = self._smaller_dom(weapon_dom, WEAPONS)
			small_suspect = self._smaller_dom(suspect_dom, SUSPECTS)

			np.random.shuffle(small_room)
			np.random.shuffle(small_weapon)
			np.random.shuffle(small_suspect)

			self.caseFileRoom.assign(small_room[0])
			self.caseFileSuspect.assign(small_suspect[0])
			self.caseFileWeapon.assign(small_weapon[0])

			print("******************* GUESSED BC SOMEONE WAS CLOSE ******************")
			print("FROM {} {} {}. GUESSED {} {} {}".format(small_room, small_weapon, small_suspect, small_room[0],
				small_weapon[0], small_suspect[0]))

			accusation = {}
			accusation['Room'] = self.caseFileRoom
			accusation['Weapon'] = self.caseFileWeapon
			accusation['Suspect'] = self.caseFileSuspect
			return accusation'''

		#Make suggestion - keep as close to prev suggestion as possible
		else:
			if self._find_probability_weapon() < 50:
				new_dom = self._smaller_dom(weapon_dom, WEAPONS)
				np.random.shuffle(new_dom)
				self.past_suggestion[0] = weapon_dom[0]
				#print("Guess Weapon from: {}".format(new_dom))
			else:
				np.random.shuffle(weapon_dom)
				self.past_suggestion[0] = weapon_dom[0]

			if self._find_probability_room() < 50:
				new_dom = self._smaller_dom(room_dom, ROOMS)
				np.random.shuffle(new_dom)
				self.past_suggestion[1] = room_dom[0]
				#print("Guess Room from: {}".format(new_dom))
			else:
				np.random.shuffle(room_dom)
				self.past_suggestion[1] = room_dom[0]

			if self._find_probability_suspect() < 50:
				new_dom = self._smaller_dom(suspect_dom, SUSPECTS)
				np.random.shuffle(new_dom)
				self.past_suggestion[2] = suspect_dom[0]
				#print("Guess Suspect from: {}".format(new_dom))
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
		#print('CUR DOM1: {}'.format(dom1))
		for domain in self.second_opponent_sets:
			for card in domain:
				if card in typ:
					dom2.append(card)
		#print('CUR DOM2: {}'.format(dom2))

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
		if suggestion.suggester == self.firstOppName:
			p = [None]*3
			p[1] = self._post_probability_weapon_player(self.firstOppName)
			p[2] = self._post_probability_suspect_player(self.firstOppName)			
			p[0] = self._post_probability_room_player(self.firstOppName)

			answer = self._find_lowest_response(suggestion, p)
			if answer != None:
				print('Reduce {} cur domain'.format(self.firstOppName))
				self._update_cur_dom(self.firstOppName)
				self._prune_opp_case(self.firstOppName, answer)
			return answer
		else:
			p = [None]*3
			p[0] = self._post_probability_room_player(self.secondOppName)
			p[1] = self._post_probability_weapon_player(self.secondOppName)			
			p[2] = self._post_probability_suspect_player(self.secondOppName)

			answer = self._find_lowest_response(suggestion, p)
			if answer != None:
				print('Reduce {} cur domain'.format(self.secondOppName))
				self._update_cur_dom(self.secondOppName)
				self._prune_opp_case(self.secondOppName, answer)
			return answer


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
				print('Reduce {} cur domain'.format(suggestion.suggester))
				self._update_cur_dom(suggestion.suggester)
			elif suggestion.responder == self.secondOppName:
				self._update_cur_dom(suggestion.suggester)
				print('Reduce {} cur domain'.format(suggestion.suggester))
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

	def _update_player(self, hand, sets, d):
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
				self._remove_dict(d, domain)
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


	def _update_opp_case(self, name, hand):
		'''
		Removed opp player's cards from opp player's casefile
		'''
		if name == self.firstOppName:
			for card in hand.get_cards():
				if card.is_assigned():
					if card.typ == 'Weapon' and self.first_caseFileWeapon.in_cur_domain(card.assignedValue):
						self.first_caseFileWeapon.prune_value(card.assignedValue)
					elif card.typ == 'Room' and self.first_caseFileRoom.in_cur_domain(card.assignedValue):
						self.first_caseFileRoom.prune_value(card.assignedValue)
					elif card.typ == 'Suspect' and self.first_caseFileSuspect.in_cur_domain(card.assignedValue):
						self.first_caseFileSuspect.prune_value(card.assignedValue)
					else:
						continue
		else:
			for card in hand.get_cards():
				if card.is_assigned():
					if card.typ == 'Weapon' and self.second_caseFileWeapon.in_cur_domain(card.assignedValue):
						self.second_caseFileWeapon.prune_value(card.assignedValue)
					elif card.typ == 'Room' and self.second_caseFileRoom.in_cur_domain(card.assignedValue):
						self.second_caseFileRoom.prune_value(card.assignedValue)
					elif card.typ == 'Suspect' and self.second_caseFileSuspect.in_cur_domain(card.assignedValue):
						self.second_caseFileSuspect.prune_value(card.assignedValue)
					else:
						continue
	
	def _prune_opp_case(self, name, card):
		'''
		Prune cards that agent has shown opponents from opponents caseFile
		'''
		if name == self.firstOppName:
			if card.typ == 'Weapon' and self.first_caseFileWeapon.in_cur_domain(card.assignedValue):
				self.first_caseFileWeapon.prune_value(card.assignedValue)
			elif card.typ == 'Room' and self.first_caseFileRoom.in_cur_domain(card.assignedValue):
				self.first_caseFileRoom.prune_value(card.assignedValue)
			elif card.typ == 'Suspect' and self.first_caseFileSuspect.in_cur_domain(card.assignedValue):
				self.first_caseFileSuspect.prune_value(card.assignedValue)
		if name == self.secondOppName:
			if card.typ == 'Weapon' and self.second_caseFileWeapon.in_cur_domain(card.assignedValue):
				self.second_caseFileWeapon.prune_value(card.assignedValue)
			elif card.typ == 'Room' and self.second_caseFileRoom.in_cur_domain(card.assignedValue):
				self.second_caseFileRoom.prune_value(card.assignedValue)
			elif card.typ == 'Suspect' and self.second_caseFileSuspect.in_cur_domain(card.assignedValue):
				self.second_caseFileSuspect.prune_value(card.assignedValue)


	def _update_cur_dom(self, name):
		if name == self.firstOppName:
			self.first_total_cur_dom -= 1
		else:
			self.second_total_cur_dom -= 1	

	def _remove_dict(self, d, domain):
		'''
		Set keys' values in domain to None (no longer know anything about)
		unless 100p
		'''
		for value in domain:
			if d.get(value) == None or d.get(value) < 100:
				d[value] = None
				

	def _update_dict(self, hand, sets, d, cfw, cfs, cfr):
		'''
		Update dictionary where key is value of card
		and value is the probability of it in an opponent's hand
		'''
		#Prune values from cf for opponent
		for card in hand.get_cards():
			if card.is_assigned():
				if card.typ == 'WEAPONS' and card.in_cur_domain(card.assignedValue):
					cfw.prune_value(card.assignedValue)
				elif card.typ == 'SUSPECTS' and card.in_cur_domain(card.assignedValue):
					cfs.prune_value(card.assignedValue)
				elif card.typ == 'ROOMS' and card.in_cur_domain(card.assignedValue):
					cfr.prune_value(card.assignedValue)
		
		#Update sets
		#Remove empty lists from sets
		'''simple_set = [x for x in sets if x]
		sets = simple_set

		#Update mid-range probabilities 33/50/100
		for domain in sets:
			if len(domain) == 3:
				for value in domain:
					if d.get(value) == None or d.get(value) < 33:
						d[value] = 33
			elif len(domain) == 2:
				for value in domain:
					if d.get(value) == None or d.get(value) < 50:
						d[value] = 50
			elif len(domain) == 1:
				if d.get(domain[0]) == None or d.get(domain[0]) < 100:
					if domain[0] in WEAPONS:
						cfw.prune_value(card.assignedValue)
					elif domain[0] in SUSPECTS:
						cfs.prune_value(card.assignedValue)
					else:
						cfr.prune_value(card.assignedValue)
		'''
		'''#Update 0 probabilities
		does_not_have = []
		for card in hand.get_cards():
			if not card.is_assigned():
				for value in card.cur_domain():
					if value not in SUSPECTS+ROOMS+WEAPONS:
						does_not_have.append(value)
		for value in does_not_have:
			d[value] = 0
		'''

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

	def _init_dict(self, d):
		assigned = self.hand.get_assigned_card_values()
		for value in WEAPONS+SUSPECTS+ROOMS:
			d[value] = None
	
	def _post_probability_room_player(self, name):
		if name == self.firstOppName:
			return 100/(self.first_caseFileRoom.cur_domain_size()-1)
		else:
			return 100/(self.second_caseFileRoom.cur_domain_size()-1)

	def _post_probability_weapon_player(self, name):
		if name == self.firstOppName:
			return 100/(self.first_caseFileWeapon.cur_domain_size()-1)
		else:
			return 100/(self.second_caseFileWeapon.cur_domain_size()-1)

	def _post_probability_suspect_player(self, name):
		if name == self.firstOppName:
			return 100/(self.first_caseFileSuspect.cur_domain_size()-1)
		else:
			return 100/(self.second_caseFileSuspect.cur_domain_size()-1)
	
	def _find_total_probability(self, name):
		if name == self.firstOppName:
			return 100/(self.first_total_cur_dom)
		else:
			return 100/(self.second_total_cur_dom)

	def _find_lowest_response(self, suggestion, p):
		'''
		Returns the card with that keeps the probability as low as possible
		for the opponent
		'''
		has = [None]*3

		weapon = None
		suspect = None
		room = None

		print('P: {}'.format(p))

		for card in self.hand.get_cards():
			if card.assignedValue == suggestion.weapon:
				has[1] = 1
				weapon = card
			elif card.assignedValue == suggestion.suspect:
				has[2] = 1
				suspect = card
			elif card.assignedValue == suggestion.room:
				has[0] = 1
				room = card

		print('HAS: {}'.format(has))
		
		#Do not have any:
		if has.count(1) == 0:
			return None

		#If have all 3:
		if has.count(1) == 3:
			print('HAS ALL THREE')
			min_value = min(p)
			index = p.index(min_value)
			if index == 1:
				print('Showed {} bc lowest prob of: {}'.format(suggestion.weapon, p[1]))
				return weapon
			elif index == 2:
				print('Showed {} bc lowest prob of: {}'.format(suggestion.suspect, p[2]))
				return suspect
			elif index == 0:
				print('Showed {} bc lowest prob of: {}'.format(suggestion.room, p[0]))
				return room
		
		#Only 1
		if has.count(True) == 1:
			if has[1]:
				print('Showed {} bc only have 1: {}'.format(suggestion.weapon, p[1]))
				return weapon
			elif has[2]:
				print('Showed {} bc only have 1: {}'.format(suggestion.suspect, p[2]))
				return suspect
			else:					
				print('Showed {} bc only have 1: {}'.format(suggestion.room, p[0]))
				return room

		#Has a combo of 2
		if has.count(True) == 2:
			if has[0] and has[1]:
				if p[0] < p[1]:
					print('Showed {} bc lowest out of 2: {}'.format(suggestion.room, p[0]))
					return room
				else:
					return weapon
					print('Showed {} bc lowest out of 2: {}'.format(suggestion.weapon, p[1]))

			elif has[0] and has[2]:
				if p[0] < p[2]:
					print('Showed {} bc lowest out of 2: {}'.format(suggestion.room, p[0]))
					return room
				else:
					print('Showed {} bc lowest out of 2: {}'.format(suggestion.suspect, p[2]))
					return suspect
			else:
				if p[1] < p[2]:
					print('Showed {} bc lowest out of 2: {}'.format(suggestion.weapon, p[1]))
					return weapon
				else:
					print('Showed {} bc lowest out of 2: {}'.format(suggestion.suspect, p[2]))
					return suspect
