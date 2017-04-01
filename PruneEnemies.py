''' This Agent assumes that all suggestions made by other Agents indicate that the respective agent does not
possess those cards, and after all enemy agent hands are pruned, the casefile cards are pruned.
Shows cards randomly. '''
from game import *
import itertools

class PruneEnemiesAgent(Agent):

    def __init__(self, name):
        super(Agent, self).__init__(name)

        # Initialize CSPs for other Agents
        # Begin by initializing the opposing agent's possible cards (and removing my cards)
        domain = [x for x in WEAPONS + ROOMS + SUSPECTS if x not in self.hand.get_cards()]
        p1cards = [Card(typ = None, domain=domain)]*6
        p2cards = [Card(typ = None, domain=domain)]*6

        # Create the constraints for the player cards
        p1constraint = Constraint(name = 'p1_constraint', p1cards)
        p2constraint = Constraint(name = 'p2_constraint', p2cards)

        #Add the satisfying tuples to the constraint
        sat_tuples = list(itertools.permutations(domain, 6))
        p1constraint.add_satisfying_tuples(sat_tuples)
        p2constraint.add_satisfying_tuples(sat_tuples)

	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card
		'''
        weapon_dom = self.caseFileWeapon.cur_dom()
		room_dom = self.caseFileRoom.cur_dom()
		suspect_dom = self.caseFileRoom.cur_dom()
        np.shuffle(weapon_dom)
        np.shuffle(room_dom)
        np.shuffle(suspect_dom)

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
			suggestion = Suggestion(self.name, weapon_dom[0], room_dom[0], suspect_dom[0])
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
			else if card.get_assigned_value() == suggestion.room:
				return card
			else if card.get_assigned_value() == suggestion.suspect:
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
            for card in p1cards:
                card.prune_value(suggestion.weapon)
                card.prune_value(suggestion.room)
                card.prune_value(suggestion.suspect)
        elif suggestion.suggester == self.secondOppName:
            for card in p2cards:
                card.prune_value(suggestion.weapon)
                card.prune_value(suggestion.room)
                card.prune_value(suggestion.suspect)

        # If all enemy player cards are known, can prune from the casefile
        # Since all cards are pruned at once every time an information is received, only have to check one card
        if p1cards[0].cur_domain_size() == 1 and p2cards[0].cur_domain_size() == 1:
            for card_list in [p1cards, p2cards]:
                for card in card_list:
                    card.assign(card.cur_domain()[0])
                    if card.get_assigned_value() in ROOMS:
                        self.caseFileRoom.prune_value(card.get_assigned_value())
                    elif card.get_assigned_value() in WEAPONS:
                        self.caseFileWeapon.prune_value(card.get_assigned_value())
                    elif card.get_assigned_value() in SUSPECTS:
                        self.caseFileSuspect.prune_value(card.get_assigned_value())

            # Also prune the values that I hold in my hand
            for card in self.hand.cards:
                    card.assign(card.cur_domain()[0])
                    if card.get_assigned_value() in ROOMS:
                        self.caseFileRoom.prune_value(card.get_assigned_value())
                    elif card.get_assigned_value() in WEAPONS:
                        self.caseFileWeapon.prune_value(card.get_assigned_value())
                    elif card.get_assigned_value() in SUSPECTS:
                        self.caseFileSuspect.prune_value(card.get_assigned_value())

            # Case file domain sizes should now be 1.

		return

	def update_from_response(self, suggestion, response):
		'''
		after making a suggestion, this method will be called to respond to a response

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

if __name__ == '__main__':
	agent = PruneEnemiesAgent('Player1')
