import time
import functools
import numpy as np
import game

'''
TO DO: 
- Constraint class
- other requried functions for CSP
'''

class CSP:
	'''
	Class for packing up a set of variables into a CSP problem.
	Contains various utility routines for accessing the problem.
	The variables of the CSP can be added later or on initialization.
	The constraints must be added later

	Class will be initalized for each ghost hand (2 per player) and 1 for the case file
	'''
	def __init__(self, player, name, vars=[]):
		'''create a CSP object. Specify a name (a string - player and hand) and 
	   	optionally a set of variables'''
		self.player = player	#Player name
		self.name = name	#Name of hand for player
		self.vars = []	#Cards
		self.cons = []	#Constraints for cards
		self.vars_to_cons = dict()
		for v in vars:
			self.add_var(v)
	
	def add_var(self,v):
		'''Add variable object to CSP while setting up an index
		to obtain the constraints over this variable'''
		if not type(v) is Variable:
		    print("Trying to add non variable ", v, " to CSP object")
		elif v in self.vars_to_cons:
		    print("Trying to add variable ", v, " to CSP object that already has it")
		else:
		    self.vars.append(v)
		    self.vars_to_cons[v] = []

	def add_constraint(self,c):
		'''Add constraint to CSP. Note that all variables in the 
        constraints scope must already have been added to the CSP'''
		if not type(c) is Constraint:
		    print("Trying to add non constraint ", c, " to CSP object")
		else:
		    for v in c.scope:
		        if not v in self.vars_to_cons:
		            print("Trying to add constraint ", c, " with unknown variables to CSP object")
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
	    '''return list of variables in the CSP'''
	    return list(self.vars)

	def print_all(self):
	    print("CSP {} {}".format(self.player, self.name))
	    print("   Variables = ", self.vars)
	    print("   Constraints = ", self.cons)

	def print_soln(self):
		print("CSP", self.name, " Assignments = ")
		for v in self.vars:
		    print(v, " = ", v.get_assigned_value(), "    ", end='')
		print("")
