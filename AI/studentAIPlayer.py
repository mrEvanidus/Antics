  # -*- coding: latin-1 -*-
import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

	#__init__
	#Description: Creates a new Player
	#
	#Parameters:
	#   inputPlayerId - The id to give the new player (int)
	##
	def __init__(self, inputPlayerId):
		super(AIPlayer,self).__init__(inputPlayerId, "'smart' AI (implemented)")
	

	
	##
	#getPlacement
	#Description: The getPlacement method corresponds to the 
	#action taken on setup phase 1 and setup phase 2 of the game. 
	#In setup phase 1, the AI player will be passed a copy of the 
	#state as currentState which contains the board, accessed via 
	#currentState.board. The player will then return a list of 10 tuple 
	#coordinates (from their side of the board) that represent Locations 
	#to place the anthill and 9 grass pieces. In setup phase 2, the player 
	#will again be passed the state and needs to return a list of 2 tuple
	#coordinates (on their opponent’s side of the board) which represent
	#Locations to place the food sources. This is all that is necessary to 
	#complete the setup phases.
	#
	#Parameters:
	#   currentState - The current state of the game at the time the Game is 
	#	   requesting a placement from the player.(GameState)
	#
	#Return: If setup phase 1: list of ten 2-tuples of ints -> [(x1,y1), (x2,y2),…,(x10,y10)]
	#	   If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
	##
	def getPlacement(self, currentState):

		grass = getConstrList(currentState,None,[(GRASS)])
	
		#placement for setup phase 1: hard-coded values for now
		if currentState.phase == SETUP_PHASE_1:
			return [(2,1),(7,1),(0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3)]

		#placement for setup phase 2: find first two empty squares
		elif currentState.phase == SETUP_PHASE_2:

			#keep track of how many foods we've placed
			placedFood = False
			for i in range(0,BOARD_LENGTH):
				for j in range(6,BOARD_LENGTH):
					if currentState.board[i][j].constr == None:
						if placedFood:
							return [(x,y),(i,j)]
						else:
							x = i
							y = j
							placedFood = True
						break
							
		else:
			return None
	
	##
	#getMove
	#Description: The getMove method corresponds to the play phase of the game 
	#and requests from the player a Move object. All types are symbolic 
	#constants which can be referred to in Constants.py. The move object has a 
	#field for type (moveType) as well as field for relevant coordinate 
	#information (coordList). If for instance the player wishes to move an ant, 
	#they simply return a Move object where the type field is the MOVE_ANT constant 
	#and the coordList contains a listing of valid locations starting with an Ant 
	#and containing only unoccupied spaces thereafter. A build is similar to a move 
	#except the type is set as BUILD, a buildType is given, and a single coordinate 
	#is in the list representing the build location. For an end turn, no coordinates 
	#are necessary, just set the type as END and return.
	#
	#Parameters:
	#   currentState - The current state of the game at the time the Game is 
	#	   requesting a move from the player.(GameState)   
	#
	#Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
	##
	def getMove(self, currentState):
	
		#coordinates of our starting ants
		hillCoord = (2,1) # the queen starts here, as do any built ants
		tunnelCoord = (7,1)
		
		#find the foods coords
		foods = getConstrList(currentState,None,[(FOOD)])
		antMoves = listAllMovementMoves(currentState)
		
		# for m in antMoves:
			# if getAntAt(currentState, m.coordList[0]).type == WORKER:
				
		#if stepsToReach(currentState, m.coordList[0], foods[0]) < stepsToReach(currentState, m.coordList[0], foods[1]):
		
		# if state
			# myQueen = getCurrPlayerQueen(currentState)
		#find which ant is closer to each food
		# for c in [hillCoord, tunnelCoord]:
			# if stepsToReach(currentState, hillCoord, foods[0]) <  stepsToReach(currentState, hillCoord, foods[1]):
				# hillFoodCoord = foods[0]
			# else:
				# hillFoodCoord = foods[1]
			# if stepsToReach(currentState, tunnelCoord, foods[0]) <  stepsToReach(currentState, tunnelCoord, foods[1]):
				# tunnelFoodCoord = foods[0]
			# else:
				# tunnelFoodCoord = foods[1]
		
		return Move(END, None, None, )
		
		myWorkers = getAntList(currentState, 2, [(WORKER)])
		for ant in myWorkers:
			if ant.hasMoved:
				continue
			else:
				wMoves = listAllMovementPaths(currentState, ant.coords, UNIT_STATS[WORKER][MOVEMENT])
				
				#check all the moves to see if they are closer to food
				for path in wMoves:
					if stepsToReach(currentState, ant.coords, foods[0].coords) > stepsToReach(currentState, move.coordList[len(move.coordList) - 1], foods[0].coords):
						move = Move(MOVE_ANT, path, None)
						return move
		return None
	
	##
	#getAttack
	#Description: The getAttack method is called on the player whenever an ant completes 
	#a move and has a valid attack. It is assumed that an attack will always be made 
	#because there is no strategic advantage from withholding an attack. The AIPlayer 
	#is passed a copy of the state which again contains the board and also a clone of 
	#the attacking ant. The player is also passed a list of coordinate tuples which 
	#represent valid locations for attack. Hint: a random AI can simply return one of 
	#these coordinates for a valid attack. 
	#
	#Parameters:
	#   currentState - The current state of the game at the time the Game is requesting 
	#	   a move from the player. (GameState)
	#   attackingAnt - A clone of the ant currently making the attack. (Ant)
	#   enemyLocation - A list of coordinate locations for valid attacks (i.e. 
	#	   enemies within range) ([list of 2-tuples of ints])
	#
	#Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
	##
	def getAttack(self, currentState, attackingAnt, enemyLocations):
		return enemyLocations[0]
		
  
		
		
	 ##
	#registerWin
	#Description: The last method, registerWin, is called when the game ends and simply 
	#indicates to the AI whether it has won or lost the game. This is to help with 
	#learning algorithms to develop more successful strategies.
	#
	#Parameters:
	#   hasWon - True if the player has won the game, False if the player lost. (Boolean)
	#
	def registerWin(self, hasWon):
		#method templaste, not implemented
		pass