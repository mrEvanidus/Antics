__author__ = 'Max Robinson, Triton Pitassi'
import random
from Ant import *
from Building import *
from Player import *
from AIPlayerUtils import *
from math import *

# #
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#    playerId - The id of the player.
# #
class AIPlayer(Player):

    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #    inputPlayerId - The id to give the new player (int)
    # #
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "DFS-Informed")
        self.MAX_DEPTH = 2

    # #
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #    must be placed by the player.  These items are: 1 Anthill on
    #    the player's side; 1 tunnel on player's side; 9 grass on the
    #    player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #    construction - the Construction to be placed.
    #    currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    # #
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    # #
    # getMove
    # Description: Chooses the next best move to make by first expanding all legal moves and then scoring
    #   each expanded state. It then decides which move to make based on the highest score.
    #   If multiple moves share the same score, a random move is picked from the list of moves that all
    #   received that score.
    #
    # Parameters:
    #    currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    # #
    def getMove(self, currentState):
        # currentState.fastclone()
        # moves = listAllLegalMoves(currentState)
        # score = -1
        # moveToMake = None
        # moveDict = {}
        # for move in moves:
        #     newGameState = self.expandNode(currentState, move)
        #     tempScore = self.evaluateState(newGameState)
        #     if tempScore not in moveDict:
        #         moveDict[tempScore] = list()
        #     moveDict[tempScore].append(move)
        #
        # maxKey = 0
        # for key in moveDict:
        #     if key > maxKey:
        #         maxKey = key
        #
        #
        # # Choose random move that has a key value of maxKey Value
        # if moveDict.get(maxKey) is not None:
        #     moveToMake = moveDict[maxKey][random.randint(0, len(moveDict[maxKey])-1)]
        #
        # if moveToMake is None:
        #     return Move(END, None, None)
        #
        # return moveToMake

        gameState = currentState.fastclone()
        node = Node(None, gameState, None, None)

        bestNode = self.search(node, self.playerId, 0)
        return bestNode.move

    # #
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #    currentState - A clone of the current state (GameState)
    #    attackingAnt - The ant currently making the attack (Ant)
    #    enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    # #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    # #
    # expandNode
    # Description: This method takes a game state, and a move, and applies the move
    #   to the game State to depict what the game state would look like after the move is made
    #
    # Parameters:
    #    currentState - A clone of the current state (GameState)
    #    move - a game move to be executed to expand the state
    # #
    def expandNode(self, currentState, move):
        gameState = currentState.fastclone()
        ourInventory = gameState.inventories[self.playerId]
        if(move.moveType == MOVE_ANT):
            antToMove = None
            for ant in ourInventory.ants:
                if ant.coords == move.coordList[0]:
                    antToMove = ant
            if antToMove is not None:
                antToMove.coords = move.coordList[-1]
                antToMove.hasMoved = True

                # check if other ants near by for attack
                opponentId = self.getOpponentId()
                enemyInv = gameState.inventories[opponentId]
                ## Checks if can attack.
                self.attackSequence(enemyInv, antToMove)

        elif(move.moveType == BUILD):
            # just worried about building Ants and Tunnel
            if(move.buildType == WORKER):
                # add ant
                ourInventory.ants.append(Ant(move.coordList[-1], WORKER, self.playerId))
                # subtract food
                ourInventory.foodCount -= 1
            elif(move.buildType == DRONE):
                ourInventory.ants.append(Ant(move.coordList[-1], DRONE, self.playerId))
                ourInventory.foodCount -= 1
            elif(move.buildType == SOLDIER):
                ourInventory.ants.append(Ant(move.coordList[-1], SOLDIER, self.playerId))
                ourInventory.foodCount -= 2
            elif(move.buildType == R_SOLDIER):
                ourInventory.ants.append(Ant(move.coordList[-1], R_SOLDIER, self.playerId))
                ourInventory.foodCount -= 2
            elif(move.buildType == TUNNEL):
                ourInventory.constrs.append(Building(move.coordList[-1], TUNNEL, self.playerId))
                ourInventory.foodCount -= 3
        else:
            self.pickUpFood(gameState, ourInventory)
            self.dropOffFood(gameState, ourInventory)
            return gameState

        return gameState

    # #
    # getOpponentId
    # Description: Helper method to get the opponent's ID
    #
    # Parameters:
    #    None
    #
    # Return: The opponent's ID
    # #
    def getOpponentId(self):
        opponentId = -1
        if self.playerId == 0:
            opponentId = 1
        else:
            opponentId = 0
        return opponentId


    # #
    # isValidAttack
    # Description: Determines if an attack is valid.
    #   This method was taken from the Game.py file, and slightly modified by current authors.
    #
    # Parameters:
    #    attackingAnt - The ant that will be attacking
    #    attackCoord - The Coords of where the ant is attacking
    #
    # Return: A boolean: True for Valid attack, False otherwise.
    def isValidAttack(self, attackingAnt, attackCoord):
        if attackCoord == None:
            return None
        # we know we have an enemy ant
        range = UNIT_STATS[attackingAnt.type][RANGE]
        diffX = abs(attackingAnt.coords[0] - attackCoord[0])
        diffY = abs(attackingAnt.coords[1] - attackCoord[1])

        # pythagoras would be proud
        if range ** 2 >= diffX ** 2 + diffY ** 2:
            # return True if within range
            return True
        else:
            return False

    # #
    # attackSequence
    # Description: This method determines if there are any valid attacks for ourAI, and if so,
    #   to evaluate the attack by picking a random enemy to attack.
    #
    # Parameters:
    #    enemyInv - The opponents Inventory
    #    antToMove - The ant that is moving into attack range.
    #
    # Return: Nothing
    # #
    def attackSequence(self, enemyInv, antToMove ):
        attackedAntList = []
        for ant in enemyInv.ants:
            if self.isValidAttack(antToMove, ant.coords):
                # keep track of valid ants to attack
                attackedAntList.append(ant)

        if len(attackedAntList) > 0:
            antToAttack = attackedAntList[random.randint(0, len(attackedAntList)-1)]
            # subtract health
            if antToMove == SOLDIER or antToMove == QUEEN:
                antToAttack.health -= 2
            else:
                antToAttack.health -= 1
            #if ant dies, remove it from list
            if antToAttack.health <= 0:
                enemyInv.ants.remove(antToAttack)

    # #
    # pickUpFood
    # Description: This method edits the game state to pickUP food if a worker ant that can carry is standing
    #   on food.
    #
    # Parameters:
    #    gameState - The state being edited.
    #    ourInventory - our Inventory
    #
    # Return: Nothing
    # #
    def pickUpFood(self, gameState, ourInventory):
        # check if food there
        for ant in ourInventory.ants:
            if getConstrAt(gameState, ant.coords) is not None:
                if getConstrAt(gameState, ant.coords).type == FOOD and (not ant.carrying):
                    ant.carrying = True

    # #
    # dropOffFood
    # Description: This method edits the game state to drop off food if a worker ant with food is standing
    #   on a tunnel or anthill.
    #
    # Parameters:
    #    gameState - The state being edited.
    #    ourInventory - our Inventory
    #
    # Return: Nothing
    # #
    def dropOffFood(self, gameState, ourInventory):
        # check if landded on tunnel or anthill
        for ant in ourInventory.ants:
            if getConstrAt(gameState, ant.coords) is not None:
                if getConstrAt(gameState, ant.coords).type == TUNNEL or \
                        getConstrAt(gameState, ant.coords).type == ANTHILL\
                        and ant.carrying:
                    ant.carrying = False
                    ourInventory.foodCount += 1

    # #
    # evaluateState
    # Description:
    #
    # Parameters:
    #    gameState - The state being edited.
    #
    # Return: Score - a number between 0 and 1 that depicts how good a game state is for our AI
    # #
    def evaluateState(self, gameState):
        opponentId = self.getOpponentId()
        enemyInv = gameState.inventories[opponentId]
        ourInv = gameState.inventories[self.playerId]
        if self.checkIfWon(ourInv, enemyInv):
            return 1.0
        elif self.checkIfLose(ourInv, enemyInv):
            return 0.0

        sumScore = 0
        sumScore += self.evalNumAnts(ourInv, enemyInv)
        sumScore += self.evalType(ourInv)
        sumScore += self.evalAntsHealth(ourInv, enemyInv)
        sumScore += self.evalFood(ourInv, enemyInv)
        sumScore += self.evalQueenThreat(gameState, ourInv, enemyInv)
        sumScore += self.evalWorkerCarrying(gameState, ourInv)
        sumScore += self.evalWorkerNotCarrying(gameState, ourInv)
        sumScore += self.evalQueenPosition(ourInv)

        score = sumScore/8  # divide by number of catagories to
        # print score
        return score

    # #
    # CheckIfWon
    # Description: Checks if the gamestate is a win condition
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Boolean: True if win condition, False if not.
    # #
    def checkIfWon(self, ourInv, enemyInv):
        if enemyInv.getQueen() is None or ourInv.foodCount == 11:
            return True
        return False

    # #
    # CheckIfLose
    # Description: Checks if the game state is a lose condition
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Boolean: True if win condition, False if not.
    # #
    def checkIfLose(self, ourInv, enemyInv):
        # bit more complicated....
        if ourInv.getQueen() is None:
            return True
        return False
    # #
    # evalNumAnts
    # Description: Evaluates the number of ants we have based on the number of ants the opponent has
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Score - score based on the difference between the number of ants we have and our opponent has
    # #
    def evalNumAnts(self, ourInv, enemyInv):
        ourNum = len(ourInv.ants)
        enNum = len(enemyInv.ants)

        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        return self.diff(ourNum, enNum, 5)

    # #
    # evalAntsHealth
    # Description: evals ants Health. checks the collective difference between our ants health verses our opponents
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Score - based on difference of overall ant health between AI's ants and Enemies Ant's
    # #
    def evalAntsHealth(self, ourInv, enemyInv):
        ourHealth=-1
        enHealth=-1
        for oAnt in ourInv.ants:
            ourHealth += oAnt.health
        for eAnt in enemyInv.ants:
            enHealth += eAnt.health

        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        return self.diff(ourHealth, enHealth, 5)

    # #
    # evalFood
    # Description: Evals the differnece in food based on diff between our Ai's food and Enemies Food
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Score - based on difference of food between AI and Enemy's
    # #
    def evalFood(self, ourInv, enemyInv):
        return self.diff(ourInv.foodCount, enemyInv.foodCount, 10)

    # #
    # evalQueenThreat
    # Description: Evals the threat our AI's ants are posing to the enemy queen. Based on distance from queen.
    #   Uses mostly drones and drone distance.
    #
    # Parameters:
    #   gameState - the state of the game.
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's inventory
    #
    # Return: Score - based on difference of overall drone distance of a drone to the enemy queen.
    # #
    def evalQueenThreat(self, gameState, ourInv, enemyInv):
        droneList = []
        for ant in ourInv.ants:
            if ant.type == DRONE:
                droneList.append(ant)

        totalScore = 0
        for drone in droneList:
            dist = self.dist(gameState, drone, enemyInv.getQueen().coords)
            totalScore += self.scoreDist(dist, 14)

        score = 0
        if len(droneList) > 0:
            score = totalScore / float(len(droneList))

        return score

    # #
    # evalWorkerNotCarrying
    # Description: Evals the placement of worker ants not carrying food. Based on distance from food a worker.
    #   The closer to the food the better the score. Does this for all ants, and does a collective score, and then
    #   normalizes the score.
    #
    # Parameters:
    #   gameState - the state of the game.
    #   ourInv - the AI's inventory
    #
    # Return: Score - distance of all available workers from food.
    # #
    def evalWorkerNotCarrying(self, gameState, ourInv):
        # Find worker ants not carrying
        notCarryingWorkers = []
        for ant in ourInv.ants:
            if (not ant.carrying) and ant.type == WORKER:
                notCarryingWorkers.append(ant)

        antDistScore = 0
        for ant in notCarryingWorkers:
            minDist = 1000
            foodList = []
            for constr in gameState.inventories[2].constrs:
                if constr.type == FOOD:
                    foodList.append(constr)

            for food in foodList:
                dist = self.dist(gameState, ant, food.coords)
                if dist < minDist:
                    minDist = dist

            antDistScore += self.scoreDist(minDist, 14)

        if len(notCarryingWorkers) > 0:
            score = antDistScore / float(len(notCarryingWorkers))
        else:
            return 0

        return score

    # #
    # evalWorkerCarrying
    # Description: Evals the placement of worker ants carrying food. Based on distance from anthill or tunnel.
    #   The closer to the building the better the score. Does this for all ants, and does a collective score, and then
    #   normalizes the score.
    #
    # Parameters:
    #   gameState - the state of the game.
    #   ourInv - the AI's inventory
    #
    # Return: Score - based on all carrying ants from a building to drop food at.
    # #
    def evalWorkerCarrying(self, gameState, ourInv):
        # Find worker ants not carrying
        CarryingWorkers = []
        for ant in ourInv.ants:
            if ant.carrying and ant.type == WORKER:
                CarryingWorkers.append(ant)

        antDistScore = 0
        for ant in CarryingWorkers:
            minDist = None
            tunnelDist = 10000
            for tunnel in ourInv.getTunnels():
                dist = self.dist(gameState, ant, tunnel.coords)
                if dist < tunnelDist:
                    tunnelDist = dist
            antHillDist = self.dist(gameState, ant, ourInv.getAnthill().coords)
            if tunnelDist < antHillDist:
                minDist = tunnelDist
            else:
                minDist = antHillDist
            antDistScore += self.scoreDist(minDist, 14)
        if len(CarryingWorkers) > 0:
            score = antDistScore / float(len(CarryingWorkers))
        else:
            return 0

        return score

    # #
    # evalType
    # Description: Evals the type of ants that we have and awards score based on the ration of worker ants to
    #   drone ants.
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #
    # Return: Score - based on the ration of drone ants to worker ants.
    # #
    def evalType(self, ourInv):
        workerCount = 0
        droneCount = 0
        for ant in ourInv.ants:
            if ant.type == SOLDIER:
                return 0.0
            if ant.type == R_SOLDIER:
                return 0.0
            if ant.type == WORKER:
                workerCount += 1
            if ant.type == DRONE:
                droneCount += 1

        if workerCount <= 1:
            return 0.0
        elif workerCount >= 2:
            return 0.0

        # return droneCount in proportion to workers
        ratio = droneCount / float(workerCount * 2)
        if ratio > 2:
            ratio = 2
        score = (1/2)*ratio

        return score

    # #
    # evalQueenPosition
    # Description: Ensures that the queen does not sit or move onto the food and block our worker ants.
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #
    # Return: Score - based on if the queen is on food or not.
    # #
    def evalQueenPosition(self, ourInv):
        queen = ourInv.getQueen()
        for constr in ourInv.constrs:
            if constr.type in [ANTHILL, TUNNEL, FOOD]:
                if queen.coords == constr.coords:
                    return 0
        return 1

    # #
    # diff
    # Description: Helper method to calculate the difference between two values, given a bound to bound our equation
    #   and return a score, based on difference and bound
    #
    # Parameters:
    #   ours - AI's value
    #   theirs - opponent's value
    #   bound - an upper bound on the equation. Max difference.
    #
    # Return: Score - based on difference and the upper bound to provide a score between 0 and 1.
    # #
    def diff(self, ours, theirs, bound):
        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        diff = ours - theirs
        if diff >= bound:
            diff = bound
        elif diff <= bound:
            diff = -bound

        #return score
        return diff/(bound*2) + 0.5

    # #
    # scoreDist
    # Description: Helper method to provide a score for distance based scores. Given a distance and an upper bound,
    #   retur
    #
    # Parameters:
    #   dist - distance between two things
    #   bound - an upper bound on max possible distance.
    #
    # Return: Score - based on the distance and uses the bound to normalize the number to be between 0 and 1.
    # #
    def scoreDist(self, dist, bound):
        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        if dist == 0:
            return 1.0
        if dist > bound:
            dist = bound
        return (-dist + bound)/float(bound)

    # #
    # dist
    # Description: calculates the distance between an ant and coordinate
    #
    # Parameters:
    #   gameState - the state of the game.
    #   ant - the source ant
    #   dest - the destination COORDINATE
    #
    # Return: Score - based on difference of overall ant health between AI's ants and Enemies Ant's
    # #
    def dist(self, gameState, ant, dest):
        return sqrt((dest[0] - ant.coords[0])**2 + (dest[1] - ant.coords[1])**2)
        # return stepsToReach(gameState, ant.coords, dest)

##################### HW #3 ##########################

    # #
    # TODO: Write this comment for method
    # Description: returns the evaluated score of a list of nodes, based on best score in list.
    #
    # Parameters:
    #   listOfNodes - a list of Node objects.
    #
    # Return: MaxEval - the best evaluation rating for a node in the list.
    # #
    def setStateToMoveDeeper(self, gameState, playerId):
        antList = gameState.inventories[playerId].ants
        for ant in antList:
            ant.hasMoved = False
        gameState.whoseTurn = playerId

    def evaluateNodeList(self, nodeList):
        averageScore = 0.0
        for node in nodeList:
            averageScore += node.eval
        return averageScore/float(len(nodeList))

    # #
    # search
    # Description: searches to a depth of MAX_DEPTH to determine the best branch to go down.
    #
    # Parameters:
    #   TODO: add parameters
    #
    # Return: A node
    #       - breaks if Max_depth is 0
    # #
    def search(self, currentNode, playerId, currentDepth):
        moveList = listAllLegalMoves(currentNode.state)
        nodeList = []

        nodeDict = {}
        for move in moveList:
            # expand node
            gameState = self.expandNode(currentNode.state, move)
            eval = self.evaluateState(gameState)
            self.setStateToMoveDeeper(gameState, playerId)
            node = Node(move, gameState, currentNode.state, eval)
            nodeList.append(node)

            #if we can win, don't look further
            if node.eval == 1.0:
                return node

            if eval not in nodeDict:
                nodeDict[eval] = list()
            nodeDict[eval].append(node)

        # BASE CASE: if MAX_DEPTH - Skip recursion, and find best node of those evaluated
        # if not max dept recurs
        if currentDepth != self.MAX_DEPTH:
            # recurse here
            maxKey = max(nodeDict.keys())

            for node in nodeDict[maxKey]:
                # self.search(node, playerId, currentDepth+1)
                node.eval = self.search(node, playerId, currentDepth+1).eval
            return self.findBestNode(nodeDict[maxKey])

        # return best node of nodes that haven't been recursively expanded
        return self.findBestNode(nodeList)



    # recursive
    # Return a node
    # def search(self, currentNode, playerId, currentDepth):
    #     # Base Case
    #     if currentDepth == self.MAX_DEPTH:
    #         # for node in nodeList:
    #         #     node.eval = self.evaluateState(node.state)
    #         return currentNode
    #     # expand and create Nodes
    #     nodeList = []
    #     for move in listAllLegalMoves(currentNode.state):
    #         tempState = self.expandNode(currentNode.state, move)
    #         tempEval = self.evaluateState(currentNode.state)
    #         self.setStateToMoveDeeper(tempState, playerId)
    #         nodeList.append(Node(move, tempState, currentNode, tempEval))
    #
    #     # recursive case
    #     # recursiveList
    #
    #     # for node in nodeList:
    #         # node.eval = self.search(node, playerId, currentDepth + 1).eval
    #     for node in nodeList:
    #         self.search(node, playerId, currentDepth + 1)
    #
    #
    #     # regardless return
    #     return self.findBestNode(nodeList)


    # #
    # findBestNode
    # Description: returns the best node, in a list of nodes.
    #
    # Parameters:
    #   listOfNodes - a list of Node objects.
    #
    # Return: A NODE!!!!!!
    # #
    def findBestNode(self, nodeList):
        if len(nodeList) < 1:
            return None

        bestNode = nodeList[0]
        for node in nodeList:
            if node.eval > bestNode.eval:
                bestNode = node
        return bestNode


class Node:
    def __init__(self, move, state, parent,  eval):
        self.move = move
        self.state = state
        self.parent = parent
        self.eval = eval



## Unit Tests
from GameState import *
from Location import *
from Inventory import *
from Construction import *

# #
# putFood
# Description: places the Food for our set up for our gameState for the Unit Test
#
# Parameters:
#   neutralInventory - the inventory where grass and food is placed
#
# Return: Nothing
# #
def putFood(neutralInventory):
    for i in range(0,9):
        ourGrass = Construction((i, 0), GRASS)
        otherGrass = Construction((i,9), GRASS)
        neutralInventory.constrs.append(ourGrass)
        neutralInventory.constrs.append(otherGrass)
    for i in range(0,2):
        ourFood = Construction((i,1), FOOD)
        otherFood = Construction((i,8), FOOD)
        neutralInventory.constrs.append(ourFood)
        neutralInventory.constrs.append(otherFood)


# #
# putOurInventory
# Description: places the ants and anthill for our set up for our AI's inventory for the gameState for the Unit Test
#
# Parameters:
#   inventory - the inventory for our AI.
#
# Return: Nothing
# #
def putOurInventory(inventory):
    inventory.constrs.append(Construction((0,3), ANTHILL))
    inventory.constrs.append(Construction((1,3), TUNNEL))
    inventory.ants.append(Ant((0,3), QUEEN, PLAYER_ONE)) # Queen
    inventory.ants.append(Ant((0,6), DRONE, PLAYER_ONE)) # Queen


# #
# putTheirInventory
# Description: places the ants and anthill for our set up for our opponent's inventory
# for the gameState for the Unit Test
#
# Parameters:
#   inventory - the inventory for our opponent.
#
# Return: Nothing
# #
def putTheirInventory(inventory):
    inventory.constrs.append(Construction((0, 7), ANTHILL))
    inventory.constrs.append(Construction((1, 7), TUNNEL))
    queen = Ant((0, 7), QUEEN, PLAYER_TWO)
    queen.health = 1
    inventory.ants.append(queen) # Queen

# #
# equalStates
# Description: Checks if two game states are equal
#
# Parameters:
#   state1 - a game state
#   state2 - a game state to check against.
#
# Return: Boolean: True if equal, False if Not
# #
def equalStates(state1, state2):
    if state1.phase != state2.phase or state1.whoseTurn != state2.whoseTurn:
        return False
    for i in range(0,3):
        state1Inv = state1.inventories[i]
        state2Inv = state1.inventories[i]
        if len(state1Inv.constrs) != len(state2Inv.constrs):
            return False
        for j in range(0, len(state1Inv.constrs)):
            if state1Inv.constrs[i] != state1Inv.constrs[i]:
                return False
        if i < 2:
            if len(state1Inv.ants) != len(state2Inv.ants):
                return False
            for k in range(0, len(state1Inv.ants)):
                if state1Inv.ants[i] != state1Inv.ants[i]:
                    return False
            if state1Inv.foodCount != state2Inv.foodCount:
                return False
    return True



# #
# Unit Test
# Description: Test's that given a game state, that it expands accordingly, and evaluates that state correctly.
# #
board = [[Location((col, row)) for row in xrange(0, BOARD_LENGTH)] for col in xrange(0, BOARD_LENGTH)]
p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
neutralInventory = Inventory(NEUTRAL, [], [], 0)

putFood(neutralInventory)
putOurInventory(p1Inventory)
putTheirInventory(p2Inventory)

state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], PLAY_PHASE, PLAYER_ONE)
expectedState = state.fastclone()
expectedState.inventories[PLAYER_TWO].ants = []


ourAI = AIPlayer(PLAYER_ONE)

move = Move(MOVE_ANT,[(0,6)], None)
retrievedState = ourAI.expandNode(state, move)

if equalStates(retrievedState, expectedState):
    score = ourAI.evaluateState(retrievedState)
    if score == 1.0:
        print "Unit Test #1 Passed"
    else:
        print "UNIT TEST #1 FAILED"
else:
    print "UNIT TEST #1 FAILED: STATES NOT THE SAME."








