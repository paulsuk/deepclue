# deepclue
Project for CSC384 Winter 2017

To run the code: go to the main of game.py.

To compare 3 Agents, initialize 3 agents, and call compare(), with the 3 agents as well as the name of the test, and optionally the number of games to run the test on. 

There is an option to print every single step of the game to have an understanding of what's going on in each step, you can set 'verbose' to be true.

Note that all agents must be subclasses of the Agent class fond in cspclue.py


Our rules of clue are:
Modified Rules:
-21 cards total (9 locations, 6 suspects, 6 weapons)
-3 cards (1 of each category) are selected as the case file which describes the circumstances of the murder. The goal of the game is to be able to figure out what are the cards in the case file.
-Each player gets 6 random cards that are not already in the middle (3 PLAYERS)
-During a player’s turn they can either
	-Make a suggestion
		-The player to the left must now disprove the suggestion by revealing 1 card in their hand that matches the suggestion, showing the card to the suggester. If the player to the left does not have any cards that match, then the next player can try to disprove the suggestion.
	-Make an accusation (you can only make 1 accusation per game)
		-If a player makes an accusation, the case file is revealed to that player
		-If the accusation was correct then the player who made the accusation wins
		-Otherwise, player stays in the game but do not ask any more suggestions. The player can no longer win the game

