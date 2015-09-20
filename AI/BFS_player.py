import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import *
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
		super(AIPlayer,self).__init__(inputPlayerId, "Reward/Punishment AI")

	##
	#getPlacement
	#
	#Description: called during setup phase for each Construction that
	#   must be placed by the player.  These items are: 1 Anthill on
	#   the player's side; 1 tunnel on player's side; 9 grass on the
	#   player's side; and 2 food on the enemy's side.
	#
	#Parameters:
	#   construction - the Construction to be placed.
	#   currentState - the state of the game at this point in time.
	#
	#Return: The coordinates of where the construction is to be placed
	##
	def getPlacement(self, currentState):
		numToPlace = 0
		#implemented by students to return their next move
		if currentState.phase == SETUP_PHASE_1:    #stuff on my side
			numToPlace = 11
			moves = []
			for i in range(0, numToPlace):
				move = None
				while move == None:
					#Choose any x location
					x = random.randint(0, 9)
					#Choose any y location on your side of the board
					y = random.randint(0, 3)
					#Set the move if this space is empty
					if currentState.board[x][y].constr == None and (x, y) not in moves:
						move = (x, y)
						#Just need to make the space non-empty. So I threw whatever I felt like in there.
						currentState.board[x][y].constr == True
				moves.append(move)
			return moves
		elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
			numToPlace = 2
			moves = []
			for i in range(0, numToPlace):
				move = None
				while move == None:
					#Choose any x location
					x = random.randint(0, 9)
					#Choose any y location on enemy side of the board
					y = random.randint(6, 9)
					#Set the move if this space is empty
					if currentState.board[x][y].constr == None and (x, y) not in moves:
						move = (x, y)
						#Just need to make the space non-empty. So I threw whatever I felt like in there.
						currentState.board[x][y].constr == True
				moves.append(move)
			return moves
		else:
			return [(0, 0)]

	##
	#getMove
	#Description: Gets the next move from the Player.
	#
	#Parameters:
	#   currentState - The state of the current game waiting for the player's move (GameState)
	#
	#Return: The Move to be made
	##
	#TODO: AI should make moves according to BFS & board evaluation
	def getMove(self, currentState):
		#self.evaluate(currentState)
		moves = listAllLegalMoves(currentState)

		for move in moves:
			nextState = self.genState(currentState, move)

		return moves[random.randint(0,len(moves) - 1)]

	##
	#getAttack
	#Description: Gets the attack to be made from the Player
	#
	#Parameters:
	#   currentState - A clone of the current state (GameState)
	#   attackingAnt - The ant currently making the attack (Ant)
	#   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
	##
	def getAttack(self, currentState, attackingAnt, enemyLocations):
		#Attack a random enemy.
		return enemyLocations[random.randint(0, len(enemyLocations) - 1)]


	#================================================================================
	#   BOARD EVALUATION FUNCTIONS FOR HOMEWORK 2
	#================================================================================

	##
	#genState
	#Description: determines what the agent's state would look like after a given move
	#
	#Parameters:
	#   currentState - the state of the game before the move
	#   moveAction - the move to be made on the current state
	#                  (we assume these are always legal moves)
	#
	#Returns: the state of the game after the move,
	# or None if the move seems invalid (limited checks for this)
	##
	def genState(self, currentState, moveAction):
		simpleState = currentState.fastclone()

		opponentId = 0
		if self.playerId == 0:
			opponentId = 1

		if moveAction.moveType == MOVE_ANT:
			#move the ant.
			movingAnt = getAntAt(simpleState, moveAction.coordList[0])
			if movingAnt == None:
				return None

			movingAnt.coords = moveAction.coordList[len(moveAction.coordList)-1]

			#assume we attack an ant nearby
			# (in the case of multiple targets this may be inaccurate)
			for coord in listAdjacent(movingAnt.coords):
				ant = getAntAt(simpleState, coord)
				if ant != None and ant.player != self.playerId:
					ant.health -= UNIT_STATS[movingAnt.type][ATTACK]
					#an ant has died
					if ant.health <= 0:
						simpleState.inventories[opponentId].remove(ant)
					break

			#worker ants pick up food if they end turn on a food
			foods = getConstrList(simpleState, None, [(FOOD)])
			for food in foods:
				if movingAnt.type == WORKER and food.coords == movingAnt.coords:
					movingAnt.carrying = True

			#worker ants drop food if they end turn on the goals
			goals = getConstrList(simpleState, None, types=(ANTHILL,TUNNEL))
			for goal in goals:
				if movingAnt.type == WORKER and goal.coords == movingAnt.coords and movingAnt.carrying:
					movingAnt.carrying = False
					simpleState.inventories[self.playerId].foodCount += 1


		elif moveAction.moveType == BUILD:
			# decrease the food amount for the player
			simpleState.inventories[self.playerId].foodCount -= UNIT_STATS[moveAction.buildType][COST]
			if simpleState.inventories[self.playerId].foodCount > 0:
				return None

			#add the appropriate ant to the player's inventory
			newAnt = Ant(moveAction.coordList[0], moveAction.buildType, self.playerId)
			simpleState.inventories[self.playerId].ants.append(newAnt)

		# elif moveAction.moveType == END:
			# we made no change

		return simpleState

	##
	#evaluate
	#Description:  examines a GameState and returns a double
	#              between 0.0 and 1.0 that indicates how "good" that state is
	#
	#Parameters:
	#   gameState - the state to evaluate
	#
	#Returns: a double indicating the desirability of the state
	#         (from the current player's perspective)
	##
	def evaluate(self, gameState):
		#get the player inventories
		myInv = gameState.inventories[self.playerId]

		opponentId = 0
		if self.playerId == 0:
			opponentId = 1
		opponentInv = gameState.inventories[opponentId]

		#base-case: if we win, return 1.
		if myInv.foodCount == 11 or opponentInv.getQueen() == None:
			return 1.0 #WIN

		#base-case: if the opponent wins, return 0.
		if opponentInv.foodCount == 11 or myInv.getQueen() == None:
			return 0.0 #LOSE

		#compare food counts
		foodResult = (myInv.foodCount - opponentInv.foodCount)/FOOD_GOAL + 0.5

		#compare the ant counts
		allAnts = getAntList(gameState, pid=None)
		antResult = (len(myInv.ants) - len(opponentInv.ants))/len(allAnts) + 0.5

		#ant values (sum of stats minus build cost)
		workerValue = 4
		droneValue = 6
		soldierValue = 6
		rangeValue = 5

		myAntSum = 0
		for myAnt in myInv.ants:
			if myAnt.type == WORKER:
				myAntSum = myAntSum + workerValue
			elif myAnt.type == DRONE:
				myAntSum = myAntSum + droneValue
			elif myAnt.type == SOLDIER:
				myAntSum = myAntSum + soldierValue
			elif myAnt.type == R_SOLDIER:
				myAntSum = myAntSum + rangeValue

		oppAntSum = 0
		for oppAnt in myInv.ants:
			if oppAnt.type == WORKER:
				oppAntSum = oppAntSum + workerValue
			elif oppAnt.type == DRONE:
				oppAntSum = oppAntSum + droneValue
			elif oppAnt.type == SOLDIER:
				oppAntSum = oppAntSum + soldierValue
			elif oppAnt.type == R_SOLDIER:
				oppAntSum = oppAntSum + rangeValue

		armyStrength = (myAntSum - oppAntSum)/(myAntSum + oppAntSum) + 0.5

		#weight all considerations - higher multipliers = higher weight
		#food - 2
		#number of ants - 1
		result = (foodResult*2 + antResult + armyStrength)/4

		return result
