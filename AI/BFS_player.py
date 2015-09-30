import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import *
from Move import Move
from GameState import *
from Location import *
from Inventory import *
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
		super(AIPlayer,self).__init__(inputPlayerId, "Jet Drones Can't Melt Steel Queens")

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
	def getMove(self, currentState):
		moves = listAllLegalMoves(currentState)

		bestMove = moves[0]
		bestMoveValue = self.evaluate(self.genState(currentState, bestMove))
		#evaluate each move and pick the best one
		for move in moves:
			nextState = self.genState(currentState, move)
			value = self.evaluate(nextState)
			if (value > bestMoveValue):
				bestMove = move
				bestMoveValue = value
		return bestMove

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
						simpleState.inventories[opponentId].ants.remove(ant)
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
			if simpleState.inventories[self.playerId].foodCount < 0:
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

		#get a list of tuple coordinates of my constructs
		buildings = getConstrList(gameState, self.playerId, (ANTHILL, TUNNEL))
		buildingCoords = []
		buildingCoords.append(buildings[0].coords)
		buildingCoords.append(buildings[1].coords)

		#get a list of tuple coordinates of all food on board
		food = getConstrList(gameState, None, (FOOD, ))
		foodCoords = []
		for foodObj in food:
			foodCoords.append(foodObj.coords)

		#base-case: if we win, return 1.
		if myInv.foodCount == 11 or opponentInv.getQueen() == None:
			return 1.0 #WIN

		#base-case: if the opponent wins, return 0.
		if opponentInv.foodCount == 11 or myInv.getQueen() == None:
			return 0.0 #LOSE

		#find and store coordinates of enemy queen
		enemyQueenCoords = opponentInv.getQueen().coords

		#compare food counts
		foodResult = (float(myInv.foodCount))/(float(FOOD_GOAL))

		#compare the ant counts
		allAnts = getAntList(gameState, pid=None)
		sumMyAnts = float(len(myInv.ants))
		sumOppAnts = float(len(opponentInv.ants))
		sumAllAnts = float(len(allAnts))
		antResult = (sumMyAnts - sumOppAnts)/(2*sumAllAnts) + 0.5

		#define a value for each ant type (sum of stats minus build cost)
		workerValue = 4.0
		droneValue = 6.0
		soldierValue = 6.0
		rangeValue = 5.0
		queenValue = 1.0

		#calculate stength of my army
		myAntSum = 0.0
		for myAnt in myInv.ants:
			if myAnt.type == WORKER:
				myAntSum = myAntSum + workerValue
			elif myAnt.type == DRONE:
				myAntSum = myAntSum + droneValue
			elif myAnt.type == SOLDIER:
				myAntSum = myAntSum + soldierValue
			elif myAnt.type == R_SOLDIER:
				myAntSum = myAntSum + rangeValue
			elif myAnt.type == QUEEN:
				myAntSum = myAntSum + queenValue
		#calculate strength of opponent's army
		oppAntSum = 0.0
		for oppAnt in opponentInv.ants:
			if oppAnt.type == WORKER:
				oppAntSum = oppAntSum + workerValue
			elif oppAnt.type == DRONE:
				oppAntSum = oppAntSum + droneValue
			elif oppAnt.type == SOLDIER:
				oppAntSum = oppAntSum + soldierValue
			elif oppAnt.type == R_SOLDIER:
				oppAntSum = oppAntSum + rangeValue
			elif oppAnt.type == QUEEN:
				oppAntSum = oppAntSum + queenValue
		armyStrength = (myAntSum - oppAntSum)/(2*(myAntSum + oppAntSum)) + 0.5

		#compare how many hit points enemy has vs total possible
		currentHealth = 0.0
		totalHealth = 0.0
		for ant in opponentInv.ants:
			currentHealth = currentHealth + ant.health
			totalHealth = totalHealth + UNIT_STATS[ant.type][HEALTH]
		hpPercent = 1.0 - currentHealth/totalHealth

		#evaulate an ant's distance from it's goal
		distanceSum = 0.0
		workers = 0.0
		carryingWorkers = 0.0
		for ant in myInv.ants:
			if ant.type == WORKER:
				workers = workers + 1.0	#keep count of how many workers we have
				#calculate distance ants are from food/building and keep a sum of the steps
				if ant.carrying:
					carryingWorkers = carryingWorkers + 1.0
					closestBuilding = self.findClosestCoord(gameState, ant.coords, buildingCoords)
					buildingDistance = stepsToReach(gameState, ant.coords, closestBuilding)
					distanceSum = distanceSum + buildingDistance/2.0
				else:
					closestFood = self.findClosestCoord(gameState, ant.coords, foodCoords)
					foodDistance = stepsToReach(gameState, ant.coords, closestFood)
					distanceSum = distanceSum + foodDistance
			#all ants except worker and queen should pursue the enemy queen
			elif ant.type == DRONE or ant.type == R_SOLDIER or ant.type == SOLDIER:
				distanceSum = distanceSum + stepsToReach(gameState, ant.coords, enemyQueenCoords)

		#compare how many of our workers are carrying vs not carrying
		workerRatio = 0.0
		if workers > 0:
			distanceResult = 1.0 - distanceSum/(40*workers)
			if distanceResult < 0.0:
				distanceResult = 0.0
			workerRatio = carryingWorkers/workers
		else:
			distanceResult = 0.0

		#weight all considerations - higher multipliers = higher weight
		result = (foodResult*10.0 + antResult + armyStrength*8.0 + hpPercent + distanceResult + workerRatio/2.0)/22.5

		return result

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

#Unit Test #1: Tests whether an ant correctly moves to a space
#create a worker ant on the board
ant = Ant((0,0), WORKER, 0)

#initialize the parameters needed to create a gamestate
board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
p1Inventory = Inventory(PLAYER_ONE, [ant], [], 0)
p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
neutralInventory = Inventory(NEUTRAL, [], [], 0)
state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], MENU_PHASE, PLAYER_ONE)

#ant will move two spaces down
move = Move(MOVE_ANT, [(0,0),(0,1),(0,2)], None)

#create new AI instance and use next move algorithm
player = AIPlayer(0)
nextState = player.genState(state, move)

#check if ant made it to that destination
antDest = getAntAt(nextState,(0,2))
if(antDest.type == WORKER):
	print "Jet Drones Can't Melt Steel Queens: Unit Test #1 Passed"
else:
	print "Error has occurred in Unit Test"