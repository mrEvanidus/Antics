# -*- coding: latin-1 -*-
import random
import math
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
		super(AIPlayer,self).__init__(inputPlayerId, "Version5_test")
		self.foodA = None
		self.foodB = None
		self.theirAnthill = None

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
	#       requesting a placement from the player.(GameState)
	#
	#Return: If setup phase 1: list of ten 2-tuples of ints -> [(x1,y1), (x2,y2),,(x10,y10)]
	#       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
	##
	def getPlacement(self, currentState):
		numToPlace = 0
		if currentState.phase == SETUP_PHASE_1:    #stuff on my side
			return [(2,1),(7,1),(0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3)]
		elif currentState.phase == SETUP_PHASE_2:
			moves = []
			#place left corner
			x = 0
			y = 9
			while currentState.board[x][y].constr != None:
				x = x+1
				if x > 9:
					x = 0
					y = y-1
			moves.append((x,y))
			#place right corner
			x = 9
			y = 9
			while currentState.board[x][y].constr != None:
				x = x-1
				if x < 0:
					x = 9
					y = y-1
			moves.append((x,y))
			return moves
		else:
			return [(0, 0)]

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
	#       requesting a move from the player.(GameState)
	#
	#Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
	##
	def getMove(self, currentState):


		

		buildMoves = listAllBuildMoves(currentState)

		
		
		fighterTypeAnts = getAntList(currentState,self.playerId,[DRONE,SOLDIER,R_SOLDIER])
		countOfFighters = len(fighterTypeAnts)


		

		if countOfFighters < 2:
			for bMove in buildMoves:
				if bMove.buildType == DRONE:
					return bMove

		
			
			

		workerAnts = getAntList(currentState,self.playerId,[WORKER])
		countOfWorkers = len(workerAnts)

		if countOfFighters < 1:
			if countOfWorkers > 0 and getCurrPlayerInventory(currentState).foodCount >= 2 and workerAnts[0].coords == (2,1):
				paths = listAllMovementPaths(currentState,workerAnts[0].coords,UNIT_STATS[workerAnts[0].type][0])
				for path in paths:
					if path[-1] != workerAnts[0].coords:
						return Move(MOVE_ANT,path,0)

		if countOfWorkers < 1:
			for bMove in buildMoves:
				if bMove.buildType == WORKER:
					return bMove

		

		if(self.theirAnthill is None):
			for x in range(10):
				for y in range(6,10):
					coord = (x,y)
					construct = getConstrAt(currentState,coord)
					if construct and construct.type == ANTHILL:
						self.theirAnthill = construct.coords
						break



		for fAnt in fighterTypeAnts:
			if fAnt.hasMoved:
				continue
			r = UNIT_STATS[fAnt.type][0]
			paths = listAllMovementPaths(currentState,fAnt.coords,r)


			queenLocation = None
			for xt in range(10):
				for yt in range(6,10):
					coord = (xt,yt)
					construct = getAntAt(currentState,coord)
					if construct and construct.type == QUEEN:
						queenLocation = construct.coords
						break
			

			
			maxChange = None
			steps = -1
			adja = listAdjacent(queenLocation)
			if fAnt.coords in adja:
				return Move(MOVE_ANT,[fAnt.coords],0)
			if fAnt.coords == self.theirAnthill:
				continue
			

			for path in paths:
				target = path[-1]
				if(target in adja):
					return Move(MOVE_ANT,path,0)
				if(target == self.theirAnthill):
					return Move(MOVE_ANT,path,0)
					
				tarSteps = self.stepsToReachWithDrone(currentState,target,self.theirAnthill)
				if(not maxChange):
					maxChange = path
					steps = tarSteps
				elif steps > tarSteps:
						maxChange = path
						steps = tarSteps
			return Move(MOVE_ANT,maxChange,0)


		if getCurrPlayerInventory(currentState).foodCount < 2:
			if(self.foodA is None and self.foodB is None):
				foodLocations = []
				for x in range(10):
					for y in range(4):
						coord = (x,y)
						construct = getConstrAt(currentState,coord)
						if construct and construct.type == FOOD:
							foodLocations.append(construct.coords)
							if(len(foodLocations) >= 2):
								break
				self.foodA = foodLocations[0]
				self.foodB = foodLocations[1]

			for wAnt in workerAnts:
				if wAnt.hasMoved:
					continue
				r = UNIT_STATS[wAnt.type][0]
				paths = listAllMovementPaths(currentState,wAnt.coords,r)
				if wAnt.carrying:
					stepsAnthill = stepsToReach(currentState,wAnt.coords,(2,1))
					stepsToTunnel = stepsToReach(currentState,wAnt.coords,(7,1))
					if stepsAnthill > r and stepsToTunnel > r:
						for path in paths:
							if stepsToReach(currentState,path[-1],(2,1)) <= r or stepsToReach(currentState,path[-1],(7,1)) <= r:
								return Move(MOVE_ANT,path,0)
						stepsToCenter = stepsToReach(currentState,wAnt.coords,(4,1))
						if(stepsToCenter <= r):
							for path in paths:
								if path[-1] == (4,1):
									return Move(MOVE_ANT,path,0)
					elif stepsToTunnel <= stepsAnthill:
						for path in paths:
							if path[-1] == (7,1):
								return Move(MOVE_ANT,path,0)
					else:
						for path in paths:
							if path[-1] == (2,1):
								return Move(MOVE_ANT,path,0)
				else:
				
					stepsFoodA = stepsToReach(currentState,wAnt.coords,self.foodA)
					stepsFoodB = stepsToReach(currentState,wAnt.coords,self.foodB)
					if stepsFoodA > r and stepsFoodB > r:
						for path in paths:
							if stepsToReach(currentState,path[-1],self.foodA) <= r or stepsToReach(currentState,path[-1],self.foodB) <= r:
								return Move(MOVE_ANT,path,0)
						stepsToCenter = stepsToReach(currentState,wAnt.coords,(4,1))
						if(stepsToCenter <= r):
							for path in paths:
								if path[-1] == (4,1):
									return Move(MOVE_ANT,path,0)
						return Move(MOVE_ANT,paths[random.randint(0,len(paths) - 1)],0)
					elif stepsFoodB <= stepsFoodA:
						for path in paths:
							if path[-1] == self.foodB:
								return Move(MOVE_ANT,path,0)
						return Move(MOVE_ANT,paths[random.randint(0,len(paths) - 1)],0)
					else:
						for path in paths:
							if path[-1] == self.foodA:
								return Move(MOVE_ANT,path,0)
						return Move(MOVE_ANT,paths[random.randint(0,len(paths) - 1)],0)

		
			
			#return Move(MOVE_ANT,paths[random.randint(0,len(paths) - 1)],0)
		
		queenList = getAntList(currentState,self.playerId,[QUEEN])

		queen = queenList[0]
		
		con = getConstrAt(currentState,queen.coords)

		if con and not queen.hasMoved:
			paths = listAllMovementPaths(currentState,queen.coords,UNIT_STATS[queen.type][0])
			for path in paths:
				if path[-1] != queen.coords and path[-1][1] == 0 and path[-1][1] > 2:
					return Move(MOVE_ANT,path,0)
			return Move(MOVE_ANT,paths[random.randint(0,len(paths) - 1)],0)


		return Move(END,None,0)
		#legalMoves = listAllMovementMoves(currentState)
		#legalMoves.append(Move(END,None,0))
		##if no movement has been accepted, choose one randomly from filtered list
		#return legalMoves[random.randint(0,len(legalMoves) - 1)]

	##
	# stepsToReach
	#
	# estimates the shortest distance between two cells taking
	# movement costs into account.
	#
	#Parameters:
	#   currentState   - The state of the game (GameState)
	#   src            - starting position (an x,y coord)
	#   dst            - destination position (an x,y coord)
	#
	# Return: the costs in steps (an integer) or -1 on invalid input
	def stepsToReachWithDrone(self,currentState, src, dst):
		#check for invalid input
		if (not legalCoord(src)): return -1
		if (not legalCoord(dst)): return -1

		xChange = src[0] - dst[0]
		yChange = src[1] - dst[1]

		distance = math.sqrt(xChange**2 + yChange**2)

		return distance


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
	#       a move from the player. (GameState)
	#   attackingAnt - A clone of the ant currently making the attack. (Ant)
	#   enemyLocation - A list of coordinate locations for valid attacks (i.e.
	#       enemies within range) ([list of 2-tuples of ints])
	#
	#Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
	##
	def getAttack(self, currentState, attackingAnt, enemyLocations):
		#Attack a random enemy.
		return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

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
