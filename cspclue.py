import abc
import time
import functools
import pdb

ROOMS = ['Conservatory', 'Hall', 'Lounge', 'Dining Room', 'Kitchen', 'Ballroom', 'Billiard Room', 'Library', 'Study']
WEAPONS = ['Candlestick', 'Revolver', 'Wrench', 'Rope', 'Lead Pipe', 'Knife']
SUSPECTS = ['Miss Scarlett', 'Mrs White', 'Mr Green', 'Mrs Peacock', 'Colonel Mustard', 'Professor Plum']


'''Constraint Satisfaction Routines
   A) class Card

	  This class allows one to define CSP Cards.

	  On initialization the Card object can be given a name, and
	  an original domain of values. This list of domain values can be
	  added but NOT deleted from.

	  To support constraint propagation, the class also maintains a
	  set of flags to indicate if a value is still in its current domain.
	  So one can remove values, add them back, and query if they are
	  still current.

	B) class constraint

	  This class allows one to define constraints specified by tables
	  of satisfying assignments.

	  On initialization the Cards the constraint is over is
	  specified (i.e. the scope of the constraint). This must be an
	  ORDERED list of Cards. This list of Cards cannot be
	  changed once the constraint object is created.

	  Once initialized the constraint can be incrementally initialized
	  with a list of satisfying tuples. Each tuple specifies a value
	  for each Card in the constraint (in the same ORDER as the
	  Cards of the constraint were specified).

	C) Backtracking routine---takes propagator and CSP as arguments
	   so that basic backtracking, forward-checking or GAC can be
	   executed depending on the propagator used.

'''

class Card:

	'''Class for defining CSP Cards.  On initialization the
	   Card object should be given a name, and optionally a list of
	   domain values. Later on more domain values an be added...but
	   domain values can never be removed.

	   The Card object offers two types of functionality to support
	   search.
	   (a) It has a current domain, implimented as a set of flags
		   determining which domain values are "current", i.e., unpruned.
		   - you can prune a value, and restore it.
		   - you can obtain a list of values in the current domain, or count
			 how many are still there

	   (b) You can assign and unassign a value to the Card.
		   The assigned value must be from the Card domain, and
		   you cannot assign to an already assigned Card.

		   You can get the assigned value e.g., to find the solution after
		   search.

		   Assignments and current domain interact at the external interface
		   level. Assignments do not affect the internal state of the current domain
		   so as not to interact with value pruning and restoring during search.

		   But conceptually when a Card is assigned it only has
		   the assigned value in its current domain (viewing it this
		   way makes implementing the propagators easier). Hence, when
		   the Card is assigned, the 'cur_domain' returns the
		   assigned value as the sole member of the current domain,
		   and 'in_cur_domain' returns True only for the assigned
		   value. However, the internal state of the current domain
		   flags are not changed so that pruning and unpruning can
		   work independently of assignment and unassignment.
		   '''
	#
	#set up and info methods
	#
	def __init__(self, typ, name=None, domain=[]):
		'''Create a Card object, specifying its name (a
		string). Optionally specify the initial domain.
		'''
		self.typ = typ
		self.dom = list(domain)		 #Make a copy of passed domain
		self.curdom = [True] * len(domain)	  #using list
		self.name = name
		self.assignedValue = name

	def __str__(self):
		return 'Var-{}'.format(self.assignedValue)

	def update_type(self):
		if self.assignedValue != None and self.typ == None:
			if self.assignedValue in WEAPONS:
				self.typ = 'Weapon'
			elif self.assignedValue in ROOMS:
				self.typ = 'Room'
			else:
				self.typ = 'Suspect'

	def add_domain_values(self, values):
		'''Add additional domain values to the domain
		   Removals not supported removals'''
		for val in values:
			self.dom.append(val)
			self.curdom.append(True)

	def domain_size(self):
		'''Return the size of the (permanent) domain'''
		return(len(self.dom))

	def domain(self):
		'''return the Card's (permanent) domain'''
		return(list(self.dom))

	#
	#methods for current domain (pruning and unpruning)
	#

	def prune_value(self, value):
		'''Remove value from CURRENT domain'''
		self.curdom[self.value_index(value)] = False

	def unprune_value(self, value):
		'''Restore value to CURRENT domain'''
		self.curdom[self.value_index(value)] = True

	def cur_domain(self):
		'''return list of values in CURRENT domain (if assigned
		   only assigned value is viewed as being in current domain)'''
		vals = []
		if self.is_assigned():
			vals.append(self.get_assigned_value())
		else:
			for i, val in enumerate(self.dom):
				if self.curdom[i]:
					vals.append(val)
		return vals

	def in_cur_domain(self, value):
		'''check if value is in CURRENT domain (without constructing list)
		   if assigned only assigned value is viewed as being in current
		   domain'''
		if not value in self.dom:
			return False
		if self.is_assigned():
			return value == self.get_assigned_value()
		else:
			return self.curdom[self.value_index(value)]

	def cur_domain_size(self):
		'''Return the size of the Cards domain (without construcing list)'''
		if self.is_assigned():
			return 1
		else:
			return(sum(1 for v in self.curdom if v))

	def restore_curdom(self):
		'''return all values back into CURRENT domain'''
		for i in range(len(self.curdom)):
			self.curdom[i] = True

	#
	#methods for assigning and unassigning
	#

	def is_assigned(self):
		return self.assignedValue != None

	def assign(self, value):
		'''Used by bt_search. When we assign we remove all other values
		   values from curdom. We save this information so that we can
		   reverse it on unassign'''

		if self.is_assigned() or not self.in_cur_domain(value):
			print("ERROR: trying to assign Card", self,
				  "that is already assigned or illegal value (not in curdom)")
			return

		self.assignedValue = value

	def unassign(self):
		'''Used by bt_search. Unassign and restore old curdom'''
		if not self.is_assigned():
			print("ERROR: trying to unassign Card", self, " not yet assigned")
			return
		self.assignedValue = None

	def get_assigned_value(self):
		'''return assigned value...returns None if is unassigned'''
		return self.assignedValue

	#
	#internal methods
	#

	def value_index(self, value):
		'''Domain values need not be numbers, so return the index
		   in the domain list of a Card value'''
		return self.dom.index(value)

	def __repr__(self):
		return("Var-{}".format(self.assignedValue))

	def print_all(self):
		'''Also print the Card domain and current domain'''
		print("Var--\"{}\": Dom = {}, CurDom = {}".format(self.name,
															 self.dom,
															 self.curdom))
class Constraint:
	'''Class for defining constraints Card objects specifes an
	   ordering over Cards.  This ordering is used when calling
	   the satisfied function which tests if an assignment to the
	   Cards in the constraint's scope satisfies the constraint'''

	def __init__(self, name, scope):
		'''create a constraint object, specify the constraint name (a
		string) and its scope (an ORDERED list of Card objects).
		The order of the Cards in the scope is critical to the
		functioning of the constraint.

		Consraints are implemented as storing a set of satisfying
		tuples (i.e., each tuple specifies a value for each Card
		in the scope such that this sequence of values satisfies the
		constraints).

		NOTE: This is a very space expensive representation...a proper
		constraint object would allow for representing the constraint
		with a function.
		'''

		self.scope = list(scope)
		self.name = name
		self.sat_tuples = dict()

		#The next object data item 'sup_tuples' will be used to help
		#support GAC propgation. It allows access to a list of
		#satisfying tuples that contain a particular Card/value
		#pair.
		self.sup_tuples = dict()

	def add_satisfying_tuples(self, tuples):
		'''We specify the constraint by adding its complete list of satisfying tuples.'''
		for x in tuples:
			t = tuple(x)  #ensure we have an immutable tuple
			if not t in self.sat_tuples:
				self.sat_tuples[t] = True

			#now put t in as a support for all of the Card values in it
			for i, val in enumerate(t):
				var = self.scope[i]
				if not (var,val) in self.sup_tuples:
					self.sup_tuples[(var,val)] = []
				self.sup_tuples[(var,val)].append(t)

	def get_scope(self):
		'''get list of Cards the constraint is over'''
		return list(self.scope)

	def check(self, vals):
		'''Given list of values, one for each Card in the
		   constraints scope, return true if and only if these value
		   assignments satisfy the constraint by applying the
		   constraints "satisfies" function.  Note the list of values
		   are must be ordered in the same order as the list of
		   Cards in the constraints scope'''
		return tuple(vals) in self.sat_tuples

	def get_n_unasgn(self):
		'''return the number of unassigned Cards in the constraint's scope'''
		n = 0
		for v in self.scope:
			if not v.is_assigned():
				n = n + 1
		return n

	def get_unasgn_vars(self):
		'''return list of unassigned Cards in constraint's scope. Note
		   more expensive to get the list than to then number'''
		vs = []
		for v in self.scope:
			if not v.is_assigned():
				vs.append(v)
		return vs

	def has_support(self, var, val):
		'''Test if a Card value pair has a supporting tuple (a set
		   of assignments satisfying the constraint where each value is
		   still in the corresponding Cards current domain
		'''
		if (var, val) in self.sup_tuples:
			for t in self.sup_tuples[(var, val)]:
				if self.tuple_is_valid(t):
					return True
		return False

	def tuple_is_valid(self, t):
		'''Internal routine. Check if every value in tuple is still in
		   corresponding Card domains'''
		for i, var in enumerate(self.scope):
			if not var.in_cur_domain(t[i]):
				return False
		return True

	def __str__(self):
		return("{}({})".format(self.name,[var.name for var in self.scope]))

class CSP:
	'''Class for packing up a set of Cards into a CSP problem.
	   Contains various utility routines for accessing the problem.
	   The Cards of the CSP can be added later or on initialization.
	   The constraints must be added later'''

	def __init__(self, name, vars=[]):
		'''create a CSP object. Specify a name (a string) and
		   optionally a set of Cards'''

		self.name = name
		self.vars = []
		self.cons = []
		self.vars_to_cons = dict()
		for v in vars:
			self.add_var(v)

	def add_var(self,v):
		'''Add Card object to CSP while setting up an index
		   to obtain the constraints over this Card'''
		if not type(v) is Card:
			print("Trying to add non Card ", v, " to CSP object")
		elif v in self.vars_to_cons:
			print("Trying to add Card ", v, " to CSP object that already has it")
		else:
			self.vars.append(v)
			self.vars_to_cons[v] = []

	def add_constraint(self,c):
		'''Add constraint to CSP. Note that all Cards in the
		   constraints scope must already have been added to the CSP'''
		if not type(c) is Constraint:
			print("Trying to add non constraint ", c, " to CSP object")
		else:
			for v in c.scope:
				if not v in self.vars_to_cons:
					print("Trying to add constraint ", c, " with unknown Cards to CSP object")
					return
				self.vars_to_cons[v].append(c)
			self.cons.append(c)

	def get_all_cons(self):
		'''return list of all constraints in the CSP'''
		return self.cons

	def get_cons_with_var(self, var):
		'''return list of constraints that include var in their scope'''
		return list(self.vars_to_cons[var])

	def get_all_vars(self):
		'''return list of Cards in the CSP'''
		return list(self.vars)

	def print_all(self):
		print("CSP", self.name)
		print("   Cards = ", self.vars)
		print("   Constraints = ", self.cons)


	def print_soln(self):
		print("CSP", self.name, " Assignments = ")
		for v in self.vars:
			print(v, " = ", v.get_assigned_value(), "	", end='')
		print("")

########################################################
# Backtracking Routine								 #
########################################################

class BT:
	'''use a class to encapsulate things like statistics
	   and bookeeping for pruning/unpruning variabel domains
	   To use backtracking routine make one of these objects
	   passing the CSP as a parameter. Then you can invoke
	   that objects's bt_search routine with the right
	   kind or propagator function to obtain plain backtracking
	   forward-checking or gac'''

	def __init__(self, csp):
		'''csp == CSP object specifying the CSP to be solved'''

		self.csp = csp
		self.nDecisions = 0 #nDecisions is the number of Card
							#assignments made during search
		self.nPrunings  = 0 #nPrunings is the number of value prunings during search
		unasgn_vars = list() #used to track unassigned Cards
		self.TRACE = False
		self.runtime = 0

	def trace_on(self):
		'''Turn search trace on'''
		self.TRACE = True

	def trace_off(self):
		'''Turn search trace off'''
		self.TRACE = False


	def clear_stats(self):
		'''Initialize counters'''
		self.nDecisions = 0
		self.nPrunings = 0
		self.runtime = 0

	def print_stats(self):
		print("Search made {} Card assignments and pruned {} Card values".format(
			self.nDecisions, self.nPrunings))

	def restoreValues(self,prunings):
		'''Restore list of values to Card domains
		   each item in prunings is a pair (var, val)'''
		for var, val in prunings:
			var.unprune_value(val)

	def restore_all_Card_domains(self):
		'''Reinitialize all Card domains'''
		for var in self.csp.vars:
			if var.is_assigned():
				var.unassign()
			var.restore_curdom()

	def extractMRVvar(self):
		'''Remove Card with minimum sized cur domain from list of
		   unassigned vars. Would be faster to use heap...but this is
		   not production code.
		'''

		md = -1
		mv = None
		for v in self.unasgn_vars:
			if md < 0:
				md = v.cur_domain_size()
				mv = v
			elif v.cur_domain_size() < md:
				md = v.cur_domain_size()
				mv = v
		self.unasgn_vars.remove(mv)
		return mv

	def restoreUnasgnVar(self, var):
		'''Add Card back to list of unassigned vars'''
		self.unasgn_vars.append(var)

	def bt_search(self,propagator):
		'''Try to solve the CSP using specified propagator routine

		   propagator == a function with the following template
		   propagator(csp, newly_instantiated_Card=None)
		   ==> returns (True/False, [(Card, Value), (Card, Value) ...]

		   csp is a CSP object---the propagator can use this to get access
		   to the Cards and constraints of the problem.

		   newly_instaniated_Card is an optional argument.
		   if newly_instantiated_Card is not None:
			   then newly_instantiated_Card is the most
			   recently assigned Card of the search.
		   else:
			   progator is called before any assignments are made
			   in which case it must decide what processing to do
			   prior to any Cards being assigned.

		   The propagator returns True/False and a list of (Card, Value) pairs.
		   Return is False if a deadend has been detected by the propagator.
			 in this case bt_search will backtrack
		   return is true if we can continue.

		   The list of Card values pairs are all of the values
		   the propagator pruned (using the Card's prune_value method).
		   bt_search NEEDS to know this in order to correctly restore these
		   values when it undoes a Card assignment.

		   NOTE propagator SHOULD NOT prune a value that has already been
		   pruned! Nor should it prune a value twice'''

		self.clear_stats()
		stime = time.process_time()

		self.restore_all_Card_domains()

		self.unasgn_vars = []
		for v in self.csp.vars:
			if not v.is_assigned():
				self.unasgn_vars.append(v)

		status, prunings = propagator(self.csp) #initial propagate no assigned Cards.
		self.nPrunings = self.nPrunings + len(prunings)

		if self.TRACE:
			print(len(self.unasgn_vars), " unassigned Cards at start of search")
			print("Root Prunings: ", prunings)

		if status == False:
			print("CSP{} detected contradiction at root".format(
				self.csp.name))
		else:
			status = self.bt_recurse(propagator, 1)   #now do recursive search


		self.restoreValues(prunings)
		if status == False:
			print("CSP{} unsolved. Has no solutions".format(self.csp.name))
		if status == True:
			print("CSP {} solved. CPU Time used = {}".format(self.csp.name,
															 time.process_time() - stime))
			self.csp.print_soln()

		print("bt_search finished")
		self.print_stats()

	def bt_recurse(self, propagator, level):
		'''Return true if found solution. False if still need to search.
		   If top level returns false--> no solution'''

		if self.TRACE:
			print('  ' * level, "bt_recurse level ", level)

		if not self.unasgn_vars:
			#all Cards assigned
			return True
		else:
			var = self.extractMRVvar()
			if self.TRACE:
				print('  ' * level, "bt_recurse var = ", var)

			for val in var.cur_domain():

				if self.TRACE:
					print('  ' * level, "bt_recurse trying", var, "=", val)

				var.assign(val)
				self.nDecisions = self.nDecisions+1

				status, prunings = propagator(self.csp, var)
				self.nPrunings = self.nPrunings + len(prunings)

				if self.TRACE:
					print('  ' * level, "bt_recurse prop status = ", status)
					print('  ' * level, "bt_recurse prop pruned = ", prunings)

				if status:
					if self.bt_recurse(propagator, level+1):
						return True

				if self.TRACE:
					print('  ' * level, "bt_recurse restoring ", prunings)
				self.restoreValues(prunings)
				var.unassign()

			self.restoreUnasgnVar(var)
			return False

class Hand(object):
	'''
	6 cards
	'''
	def __init__(self):
		'''
		Initialize 6 empty card objects into hand
		'''
		self.cards = [Card(None, domain=WEAPONS+ROOMS+SUSPECTS)]*6

	def add_card(self, card):
		'''
		Initialize an empty card as card if empty cards exist

		NOTE: MIGHT NEED TO MAKE THIS MORE SPECIFIC TO ENSURE TO TARGETS
		THE RIGHT CARD, for now:
		'''
		for i, c in enumerate(self.cards):
			if c.get_assigned_value() == None:
				c = card
				self.cards[i] = card
				break

	def isInHand(self, name):
		'''
		Returns true if a card in the hand is assigned name
		'''
		for c in self.cards:
			if c.name == name:
				return True
		return False

	def get_cards(self):
		return (list(self.cards))

	def pruneHand(self, know_hand):
		'''
		Prunes opponent_hand of card values in self.hand
		'''
		for op_card in self.cards:
		  for card in know_hand.get_cards():
		   op_card.prune_value(card.assignedValue)

	def get_assigned_card_values(self):
		'''
		Returns list of assigned values of cards
		in hand
		'''
		assigned = []
		for c in self.cards:
			assigned.append(c.get_assigned_value())
		return assigned


class Suggestion(object):

	def __init__(self, suggester, responder, weapon, room, suspect):
		self.suggester = suggester
		self.responder = responder
		self.weapon = weapon
		self.room = room
		self.suspect = suspect

	def get_cards(self):
		return [self.room, self.weapon, self.suspect]

class Agent(metaclass=abc.ABCMeta):
	'''
	Hand

	create blank instance of Hand for each other player

	instance of csp or something
	gabes a bitch
	'''
	def __init__(self, name):
		'''
		init hand
		opponents

		- DONE Initialize their own hand (given from game class)
		- Initialize ghost hands for 2 oponents (csp*2)
		- DONE Initialize ghost cards for case file (csp)
		'''
		self.name = name
		self._init_csp()

	def _init_csp(self):
		self.caseFileWeapon = Card(typ="Weapon", domain=WEAPONS)
		self.caseFileSuspect = Card(typ="Suspect", domain=SUSPECTS)
		self.caseFileRoom = Card(typ="Room", domain=ROOMS)

		self.CSP = CSP(self.name, [self.caseFileRoom, self.caseFileSuspect, self.caseFileWeapon])
		roomConstraint = Constraint('Room', scope=[self.caseFileRoom])
		suspectConstraint = Constraint('Suspect', scope=[self.caseFileSuspect])
		weaponConstraint = Constraint('Weapon', scope=[self.caseFileWeapon])

		roomSatisfyingTuples = [[x] for x in ROOMS]
		suspectSatisfyingTuples = [[x] for x in SUSPECTS]
		weaponSatisfyingTuples = [[x] for x in WEAPONS]

		roomConstraint.add_satisfying_tuples(roomSatisfyingTuples)
		suspectConstraint.add_satisfying_tuples(suspectSatisfyingTuples)
		weaponConstraint.add_satisfying_tuples(weaponSatisfyingTuples)

		self.CSP.add_constraint(roomConstraint)
		self.CSP.add_constraint(suspectConstraint)
		self.CSP.add_constraint(weaponConstraint)

	def init_player_orders(self, order_dict):
		'''
		order_dict is a dictionary that maps player numbers to their names
		'''

		for key in order_dict:
			if order_dict[key] == self.name:
				self.playerNum = key
				break

		self.firstOppName = order_dict[(self.playerNum + 1) % 3]
		self.secondOppName = order_dict[(self.playerNum + 2) % 3]

	def give_hand(self, hand):
		'''
		Initalize hand
		Prune cards in hand from the casefile domain
		'''
		self.hand = hand
		for card in self.hand.get_cards():
			if card.typ == 'Weapon':
				self.caseFileWeapon.prune_value(card.assignedValue)
			elif card.typ == 'Room':
				self.caseFileRoom.prune_value(card.assignedValue)
			else:
				self.caseFileSuspect.prune_value(card.assignedValue)

	@abc.abstractmethod
	def reset(self):
		self._init_csp()

	@abc.abstractmethod
	def make_move(self):
		'''
		decide when to make a suggestion or accusation
		suggestion is of type Suggestion
		accusation is a dict where key is the type, and the value is the card
		'''
		return

	@abc.abstractmethod
	def respond_to_suggestion(self, suggestion):
		'''
		update knowledge base with whatever from game

		Update CSPs

		give a response of a card if you have a card in suggestion, or None otherwise
		'''
		return

	@abc.abstractmethod
	def observe_suggestion(self, suggestion, did_respond):
		'''
		used for observation
		observe a suggestion, and see the response
		suggestion - of type SUGGESTION
		did_respond - boolean to see if the responder sent a card back or not
		'''
		return

	@abc.abstractmethod
	def update_from_response(self, suggestion, response):
		'''
		after making a suggestion, this method will be called to respond to a response

		'''
		return

	@abc.abstractmethod
	def observe_accusation(self, accuser_name, was_correct):
		'''
		made to respond to an accusation
		was_accuser is true if the accusation was made by self, False otherwise
		was_correct is true if the accusation was correct (and the game ends)
		'''
		return
