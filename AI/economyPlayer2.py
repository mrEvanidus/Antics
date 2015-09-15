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
		super(AIPlayer,self).__init__(inputPlayerId, "Economy AI 2")



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

			#var to keep track of how many foods we've placed
			placedFood = False
			x = -1
			y = -1
			#find 2 open locations to place food
			for i in range(0,BOARD_LENGTH):
				for j in range(6,BOARD_LENGTH):
					if currentState.board[i][j].constr == None:
						if placedFood:
							return [(x,y),(i,j)]
						else:
							x = i
							y = j
							placedFood = True

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

		#ECONOMY Strategy (WIP):
		#   -begin the game by moving the queen off the hill, and building a worker
		#
		# WORKERS:
		#   -make sure to move towards closer destination (Food or tunnel/hill)
		#   -make sure to move as far as possible (not 1 when we can do)
		#   -have workers avoid grass (we've placed grass out of the way for most cases)
		#   -if we can't move closer (i.e. we are blocked) move to a different spot
		#		   (and hope we aren't blocked there)
		#   -if there is another ant on the food we are trying to get to, go towards a different food
		#
		#QUEEN:
		#   -try to move AWAY from the nearest food, so as not to block the workers
		#   -after the first turn, do nothing. the queen's job is to stay out
		#		   of the way in this strategy
		#
		#ANTHILL:
		#   -if we have less than (2) workers, build a worker
		#   -if the enemy is building an army, match the army (drones should do)
		#
		#DRONE:
		#   -if not threatened, move to the edge of our territory
		#   -if any enemy units enter the neutral zone, attack them

		#coordinates of our starting ants (hard-coded in the 'setup' phase
		hillCoord = (2,1) # the queen starts here, as do any built ants
		tunnelCoord = (7,1)

		#gather information we will need throughout this function
		# list of food (list of Construction objects)
		foods = getConstrList(currentState,None,[(FOOD)])
		#list of food coordinates (list of Tuples)
		foodCoords = []
		for f in foods:
			foodCoords.append(f.coords)
		#list of possible movements (list of Move objects)
		antMoves = listAllMovementMoves(currentState)
		#list of my ants (list of Ant objects)
		myWorkers = getAntList(currentState, currentState.whoseTurn, [(WORKER)])

#========================================QUEEN AI=========================================
		#first, if the queen is on the hill, move her off
		#try to move her away from food
		#this should happen first turn only
		queenAnt = getCurrPlayerQueen(currentState)
		hillAnt = getAntAt(currentState, hillCoord)
		if queenAnt.coords == hillCoord:
			queenMoves = listReachableAdjacent(currentState, hillCoord, UNIT_STATS[QUEEN][MOVEMENT])
			closestFoodToQueen = self.findClosestCoord(currentState, hillCoord, foodCoords)
			bestQueenMove = self.findFurthestCoord(currentState, closestFoodToQueen, queenMoves)
			return Move(MOVE_ANT, [hillCoord, bestQueenMove], None)

		#if we have not moved the queen, tell her to make a move.
		# this ensures that if she is being attacked, she will hit back
		if not (queenAnt.hasMoved):
			return Move(MOVE_ANT, [queenAnt.coords], None)

#=======================================ANTHILL AI========================================
		#the anthill should attempt to build an army to match any oncoming forces
		enemyArmy = self.getEnemyAntList(currentState, types=(DRONE, SOLDIER, R_SOLDIER))
		friendArmy = getAntList(currentState, currentState.whoseTurn, types=(DRONE, SOLDIER, R_SOLDIER))
		if len(enemyArmy) > len (friendArmy) and self.canBuild(currentState, hillCoord):
			return Move(BUILD, [hillCoord], DRONE)

		#Then, also first turn, build a worker (up to 2)
		#this method also means that if a worker is destroyed we will build a new one
		if len(myWorkers) < 2 and self.canBuild(currentState, hillCoord):
			return Move(BUILD, [hillCoord], WORKER)

#========================================WORKER AI========================================
		#Next, move any workers that we can.
		#workers without food move towards food
		# workers with food move towards goals (hill or tunnel
		workerMove = None
		for move in antMoves:
			ant = getAntAt(currentState, move.coordList[0])

			#only deal with worker-type ants
			if ant.type != WORKER:
				continue

			#calculate and pick the closest destinations
			closerFood = self.findClosestCoord(currentState, ant.coords, foodCoords)
			closerGoal = self.findClosestCoord(currentState, ant.coords, [tunnelCoord, hillCoord])

			if ant.carrying:
				if getAntAt(currentState, closerGoal) == None:
					dest = closerGoal
				else:
					continue #wait for other moves to be done (drones may move from destination)

			elif getAntAt(currentState, closerFood) == None:
				dest = closerFood

			else:
				fc = foodCoords
				fc.remove(closerFood)
				dest = self.findClosestCoord(currentState, ant.coords, fc)


			#make sure we move as far as possible UNLESS the food is only 1 space away
			if stepsToReach(currentState, ant.coords, dest) != 1 and UNIT_STATS[WORKER][MOVEMENT] > len(move.coordList):
				continue

			#find an appropriate move
			currentDist = stepsToReach(currentState, move.coordList[0], dest)
			nextDist = stepsToReach(currentState, move.coordList[len(move.coordList) - 1], dest)
			if workerMove != None and workerMove.moveType == MOVE_ANT:
				workerMoveDist = stepsToReach(currentState, workerMove.coordList[len(workerMove.coordList) - 1], dest)

			else:
				workerMoveDist = 100 #nasty hard-coded way to ensure that we always move the right direction

			#ask: is this the best move?
			if nextDist <= currentDist and nextDist < workerMoveDist:
				workerMove = move

		#return drone move
		if workerMove != None:
			return workerMove

#===================================DRONE AI==========================================
		#when workers have moved, the drones move.
		#drones try to get to the center line (row 3)
		#if any enemy units invade the neutral zone, they should be attacked
		droneMove = None
		for move in antMoves:
			ant = getAntAt(currentState, move.coordList[0])

			#only deal with drone-type ants
			if ant.type != DRONE:
				continue

			#first, see if there are enemies on the center line
			#if so, target the closest one
			enemyCoords = []
			for enemyAnt in enemyArmy:
				if enemyAnt.coords[1] <= 5:
					enemyCoords.append(enemyAnt.coords)

			#if there is no one to attack, go to center line
			if len(enemyCoords) == 0:
				dest = (ant.coords[0], 3)

			else:
				dest = self.findClosestCoord(currentState, ant.coords, enemyCoords)

			#find an appropriate move
			currentDist = stepsToReach(currentState, move.coordList[0], dest)
			nextDist = stepsToReach(currentState, move.coordList[len(move.coordList) - 1], dest)
			if droneMove != None and droneMove.moveType == MOVE_ANT:
				droneMoveDist = stepsToReach(currentState, droneMove.coordList[len(droneMove.coordList) - 1], dest)

			else:
				droneMoveDist = 100 #nasty hard-coded way to ensure that we always move the right direction

			#ask: is this the best move?
			if nextDist <= currentDist and nextDist < droneMoveDist:
				droneMove = move

		if droneMove != None:
			return droneMove


		#if we have nothing else to do, end turn
		return Move(END, None, None)



	##
	#findClosestCoord
	#Description: returns the closest in a list of coords from a specified
	#
	#Parameters:
	#   currentState - the current game state, as a GameState object
	#   src - the starting coordinate, as a tuple
	#   destList - a list of destination tuples
	#
	#Return: The closest coordinate from the list
	##
	def findClosestCoord(self, currentState, src, destList):
		result = destList[0]
		lastDist = stepsToReach(currentState, src, result)

		#loop through to find the closest coordinates
		for coords in destList:
			currentDist = stepsToReach(currentState, src, coords)
			if currentDist < lastDist:
				result = coords
				lastDist = currentDist

		return result

	##
	#findFurthestCoord
	#Description: returns the furthest in a list of coords from a specified
	#
	#Parameters:
	#   currentState - the current game state, as a GameState object
	#   src - the starting coordinate, as a tuple
	#   destList - a list of destination tuples
	#
	#Return: The furthest coordinate from the list
	##
	def findFurthestCoord(self, currentState, src, destList):
		result = destList[0]
		lastDist = stepsToReach(currentState, src, result)

		#loop through to find the closest coordinates
		for coords in destList:
			currentDist = stepsToReach(currentState, src, coords)
			if currentDist > lastDist:
				result = coords
				lastDist = currentDist

		return result

	##
	#containsNoGrass
	#Description: detects any grass on a given path
	#
	#Parameters:
	#   currentState - the current game state, as a GameState object
	#   coordList - list of coordinates to check
	#
	#Return: True if there is grass blocking that path
	##
	def containsNoGrass(self, currentState, coordList):
		for c in coordList:
			if currentState.board[c[0]][c[1]].constr != None and currentState.board[c[0]][c[1]].constr.type == GRASS:
				return False

		return True

	##
	# getEnemyAntList()
	#
	# builds a list of all enemy ants that meet a given specification
	#
	# Parameters:
	#     currentState - a GameState or Node
	#     types - a tuple of all the ant types wanted (see Constants.py)
	#
	#Returns:
	#   -a list of enemy ants of the specified types
	##
	def getEnemyAntList(self, currentState, types = (QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER)):
		result = getAntList(currentState, None, types)
		for ant in result:
			if ant.player == currentState.whoseTurn:
				result.remove(ant)

		return result

	##
	#canBuild
	#Description:
	#   checks if the current player can build a (1-cost) unit. It does this by ensuring
	#   there is no ant already on the hill, and that the player has enough food for construction
	#Params:
	#   currentState - the current game state, as a GameState object
	#   hillCoord - the coordinate at which the anthill resides
	#
	#REturns:
	#   True if building right now is a legal move
	##
	def canBuild(self, currentState, hillCoord):
		return getAntAt(currentState, hillCoord) == None and getCurrPlayerInventory(currentState).foodCount > 0

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
	#method template, not implemented
		pass
