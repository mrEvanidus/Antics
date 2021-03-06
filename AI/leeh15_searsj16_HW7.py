__author__ = "Sunny Lee & Jaimiey Sears"
import random
import math
from Ant import *
from Building import *
from Player import *
from AIPlayerUtils import *
from GameState import *
from Location import *
from Inventory import *
from Construction import *


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
        super(AIPlayer,self).__init__(inputPlayerId, "Thinker")
        self.ALPHA = 0.3
        self.limit = 5
        self.NUM_NODES = 9 #8 hidden nodes, NUM_NODES[8] is the output
        print "Learning coefficient: ", self.ALPHA

        # with 8 nodes, there should be 81 weights in this array.
        # x = 8*8 (inputs->nodes) + 1*8 (node bias) +
        #       8*1 (nodes->output) + 1*1 (output bias) = 81 weights

        # EDIT: Hardcoded network weights have been learned
        self.networkWeights = [ 3.352, -0.707, -3.247, 0.248, 3.973, 3.365, -1.675,
                                4.941, 2.807, 0.525, 0.728, 2.263, -1.098, 0.250, -4.413,
                                1.075, -3.934, -3.184, -4.498, -0.064, 0.370, -0.238,
                                -0.919, 0.359, -4.999, 1.082, -1.066, -1.437, -0.591,
                                -2.070, 1.356, 3.074, 1.331, 0.004, 2.910, 1.280, -5.164,
                                4.539, 0.804, 1.409, 2.629, -0.789, 4.244, -2.369, -1.420,
                                1.156, 0.241, 1.134, -3.899, 5.029, 3.854, 0.364, 4.625,
                                -2.643, 0.873, 2.125, -1.749, -2.482, 3.252, -2.211, 0.220,
                                2.590, -2.063, 1.309, -3.439, -1.537, -3.249, 2.111, 0.020,
                                1.834, 1.981, 3.312, -1.423, -0.614, -0.272, 3.534, -2.042,
                                -2.032, -2.572, 4.473, -2.932 ]
        # self.generateRandomNetworkWeights()


    # createNode
    # Description: Creates a new node in the form of a dictionary
    #
    # Parameters:
    #	dictMove - the move that brings us to this node
    #	dictState - the state after executing move
    #	evalScore - evaluation of the state
    #	dictParent - the node that takes us to this node
    #
    #	Returns:
    #		The node
    def createNode(self, dictMove, dictState, evalScore, dictParent):
        return dict(move=dictMove, state=dictState, score=evalScore, parent=dictParent)

    #maxNode
    #Description: Takes in a list of nodes and returns the node with the
    #		highest eval Score.
    #
    #Parameters:
    #	nodeList - list of nodes to evaluate
    #
    #Returns:
    #	node with the highest score
    def maxNode(self, nodeList):
        maxNode = nodeList[0]
        for node in nodeList:
            if node['score'] > maxNode['score']:
                maxNode = node

        return maxNode

    #minNode
    #Description: Takes in a list of nodes and returns the node with the
    #		lowest eval Score.
    #
    #Parameters:
    #	nodeList - list of nodes to evaluate
    #
    #Returns:
    #	node with the lowest score
    def minNode(self, nodeList):
        minNode = nodeList[0]
        for node in nodeList:
            if node['score'] > minNode['score']:
                minNode = node

        return minNode

    #recursiveSearch
    #Description: Given a state and current depth, recursively search tree
    #				of nodes that can be reached from this state
    #
    #Parameters:
    #	currentState: the state currently being searched from
    #	playerID: id of the player whose turn is currently being played
    #	currentDepth: the depth of the tree being searched
    #
    #Returns:
    #	the best move to make, along with an evaluation score for that move
    def recursiveSearch(self, parentNode, currentDepth, alpha, beta):

        #Sanity check
        if parentNode is None:
            return 0

        #Determining the playerId of this state to allow for both players to make moves
        playerID = parentNode['state'].whoseTurn

        #all moves from current state
        moves = listAllLegalMoves(parentNode['state'])

        # initialize variables
        result = None
        nodeList = []
        numNodes = 0

        #evaluate all nodes in tree
        for move in moves:
            #perform evaluation of node after move
            nextState = self.expandNode(parentNode['state'], move)
            evalScore = self.evaluateState(nextState)

            #update alpha/beta values for first time through recursion
            if playerID == self.playerId:
                if evalScore > beta:
                    beta = evalScore
            else:
                if evalScore < alpha:
                    alpha = evalScore

            #create a node with the calculated values
            node = self.createNode(move, nextState, evalScore, parentNode)
            nodeList.append(node)

        #recurse here: replace the node's score with it's branch score
        if currentDepth != self.limit:
            for node in nodeList:

                if playerID == self.playerId and node['score'] <= beta:
                    #skip ahead if this move isn't better
                    continue
                elif node['score'] >= alpha:
                    #skip ahead if this move isn't better
                    continue

                #Recurse down to get a score for the total branch
                branch = self.recursiveSearch(node, currentDepth+1, alpha, beta)

                #update this nodes score to reflect the whole branch
                node['score'] = branch[1]

                #update alpha and beta scores if necessary
                if playerID == self.playerId and node['score'] > branch[3]:
                    beta = branch[3]
                elif node['score'] < branch[2]:
                    alpha = branch[2]

        #find the move that would be selected, no matter whose turn it is
        if playerID == self.playerId:
            result = self.maxNode(nodeList)
        else:
            result = self.minNode(nodeList)

        #Return the winning move, the winning score, and alpha and beta values
        return [result['move'], result['score'], alpha, beta]






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
                # creates a node of the current state
        currentNode = self.createNode(None, currentState, 0, None)

        # calls recursive search function to find the best move
        # for this state
        moveScoreTuple = self.recursiveSearch(currentNode, 0, 999, -999)

        # return the move
        return moveScoreTuple[0]

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
        #gameState.whoseTurn = self.playerId
        ourInventory = gameState.inventories[currentState.whoseTurn]
        opponentId = self.getOpponentId(currentState)

        if(move.moveType == MOVE_ANT):
            antToMove = None
            for ant in ourInventory.ants:
                if ant.coords == move.coordList[0]:
                    antToMove = ant
            if antToMove is not None:
                antToMove.coords = move.coordList[-1]
                #antToMove.hasMoved = True

                # check if other ants near by for attack
                #opponentId = self.getOpponentId(currentState)
                enemyInv = gameState.inventories[opponentId]
                ## Checks if can attack.
                self.attackSequence(enemyInv, antToMove)

        elif(move.moveType == BUILD):
            # just worried about building Ants and Tunnel
            if(move.buildType == WORKER):
                # add ant
                ourInventory.ants.append(Ant(move.coordList[-1], WORKER, currentState.whoseTurn))
                # subtract food
                ourInventory.foodCount -= 1
            elif(move.buildType == DRONE):
                ourInventory.ants.append(Ant(move.coordList[-1], DRONE, currentState.whoseTurn))
                ourInventory.foodCount -= 1
            elif(move.buildType == SOLDIER):
                ourInventory.ants.append(Ant(move.coordList[-1], SOLDIER, currentState.whoseTurn))
                ourInventory.foodCount -= 2
            elif(move.buildType == R_SOLDIER):
                ourInventory.ants.append(Ant(move.coordList[-1], R_SOLDIER, currentState.whoseTurn))
                ourInventory.foodCount -= 2
            elif(move.buildType == TUNNEL):
                ourInventory.constrs.append(Building(move.coordList[-1], TUNNEL, currentState.whoseTurn))
                ourInventory.foodCount -= 3
        else:
            self.pickUpFood(gameState, ourInventory)
            self.dropOffFood(gameState, ourInventory)
            gameState.whoseTurn = opponentId
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
    def getOpponentId(self, currentState):
        opponentId = -1
        if currentState.whoseTurn == 0:
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
        opponentId = self.getOpponentId(gameState)
        if opponentId == self.playerId:
            opponentId = (opponentId + 1)%2

        enemyInv = gameState.inventories[opponentId]
        ourInv = gameState.inventories[self.playerId]
        if self.checkIfWon(ourInv, enemyInv):
            return 1.0
        elif self.checkIfLose(ourInv, enemyInv):
            return 0.0

        scores = []
        scores.append(self.evalNumAnts(ourInv, enemyInv))
        scores.append(self.evalType(ourInv))
        scores.append(self.evalAntsHealth(ourInv, enemyInv))
        scores.append(self.evalFood(ourInv, enemyInv))
        scores.append(self.evalQueenThreat(gameState, ourInv, enemyInv))
        scores.append(self.evalWorkerCarrying(gameState, ourInv))
        scores.append(self.evalWorkerNotCarrying(gameState, ourInv))
        scores.append(self.evalQueenPosition(ourInv))

        # scoreSum = 0.0
        # for score in scores:
        #     scoreSum += score
        #
        # target = scoreSum/8.0
        #
        # outputs = self.propagateNeuralNetwork(scores)
        # self.backPropagateNeuralNetwork(target, outputs, scores)
        # error = outputs[self.NUM_NODES -1] - target
        #
        # print "Error = ", abs(error)
        # if abs(error) < 0.03:
        #     string = "["
        #     for w in self.networkWeights:
        #         string += " {0:.3f},".format(w)
        #     print string, "]"

        outputs = self.propagateNeuralNetwork(scores)
        return outputs[self.NUM_NODES -1]

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
                if dist <= minDist:
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
                if dist <= tunnelDist:
                    tunnelDist = dist
            antHillDist = self.dist(gameState, ant, ourInv.getAnthill().coords)
            if tunnelDist <= antHillDist:
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
                return 0
            if ant.type == R_SOLDIER:
                return 0
            if ant.type == WORKER:
                workerCount += 1
            if ant.type == DRONE:
                droneCount += 1

        if workerCount <= 1:
            return 0
        elif workerCount >= 2:
            return 0

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
        for food in ourInv.constrs:
            if queen.coords == food.coords:
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
        diffX = abs(ant.coords[0] - dest[0])
        diffY = abs(ant.coords[1] - dest[1])
        return diffX + diffY
        #return math.sqrt((dest[0] - ant.coords[0])**2 + (dest[1] - ant.coords[1])**2)
        #return stepsToReach(gameState, ant.coords, dest)

    # #
    # propagateNeuralNetwork
    # Description: gets the output of a network given a set of inputs
    #
    # Parameters:
    #   inputs - a list of inputs between 0..1
    #
    # Return: nodeVals[8] is the sole output of the network
    # #
    def propagateNeuralNetwork(self, inputs):
        nodeVals = [0] * self.NUM_NODES
        counter = 0


        # weights 0-8 are biases for 8 inner nodes [0:7] and 1 output node [8]
        while counter < self.NUM_NODES:
            nodeVals[counter] = self.networkWeights[counter]
            counter += 1

        # weights 9-73 are weights applied to inputs
        for i in range(len(inputs)):
            for j in range(self.NUM_NODES -1):
                nodeVals[j] += inputs[i]*self.networkWeights[counter]
                counter += 1

        for m in range(self.NUM_NODES -1):
            nodeVals[m] = self.g(nodeVals[m])

        # weights 74-81 are weights applied to middle nodes
        for k in  range(self.NUM_NODES -1):
            nodeVals[self.NUM_NODES-1] += nodeVals[k]*self.networkWeights[counter]
            counter += 1

        nodeVals[self.NUM_NODES -1] = self.g(nodeVals[self.NUM_NODES -1])

        return nodeVals

    # #
    # g
    # Description: applies the 'g' function used by our neural network
    #
    # Parameters:
    #   x - the variable to apply g to
    #
    # Return: g(x)
    # #
    def g(self, x):
        return 1/(1+math.exp(-x))

    # #
    # generateRandomNetworkWeights
    # Description: populates the weights list with random numbers
    #
    # Parameters: none
    #
    # Return: none
    # #
    def generateRandomNetworkWeights(self):
        weightCounts = self.NUM_NODES**2
        for i in range(weightCounts):
            # random float between -5 and 5
            self.networkWeights.append(random.random()*10.0-5.0)

    # #
    # backPropagateNeuralNetwork
    # Description: edit the weights of the network based on a target output
    #
    # Parameters:
    #   target - the expected output, for generating an error term
    #   outputs - a list of outputs from our nodes. The last element is our network output.
    #   inputs - a list of the inputs to our neural network, as they were applied to the network
    #
    # Return: nodeVals[8] is the sole output of the network
    # #
    def backPropagateNeuralNetwork(self, target, outputs, inputs ):

        # calculate error for the output node
        err = target - outputs[self.NUM_NODES-1]
        delta = outputs[self.NUM_NODES-1]*(1-outputs[self.NUM_NODES-1])*err
        counter = self.NUM_NODES-1 + (self.NUM_NODES-1)*len(inputs)

        hiddenErrs = [0] * (self.NUM_NODES-1)
        hiddenDeltas = [0] * (self.NUM_NODES-1)
        for i in range(self.NUM_NODES -2):
            hiddenErrs[i] = self.networkWeights[counter+1 + i]*delta
            hiddenDeltas[i] = outputs[i]*(1-outputs[i])*hiddenErrs[i]

        hiddenDeltas.append(delta)

        for w in range(len(self.networkWeights) -1):
            if w < self.NUM_NODES:
                nodeIdx = w %self.NUM_NODES
                input = 1
            elif w > len(self.networkWeights) - self.NUM_NODES:
                nodeIdx = self.NUM_NODES-1
                inputIdx = w - (len(self.networkWeights) - self.NUM_NODES)
                input = outputs[inputIdx]
            else:
                nodeIdx = (w-1) %(self.NUM_NODES-1)
                inputIdx = (w-self.NUM_NODES)/(self.NUM_NODES -1)
                input = inputs[inputIdx]

            self.networkWeights[w] += self.ALPHA*hiddenDeltas[nodeIdx]*input

## Unit Tests

#unit test 1##
p = AIPlayer(0)
p.NUM_NODES = 4
p.ALPHA = 0.8
p.networkWeights = [0.5, 0.3, -0.3, 0.0, 0.9, 0.2, 0.0, 0.0, -0.4, -0.8, -0.4, 0.1, -0.1]
testInputs =  [0,1]
output = 0.444
out = p.propagateNeuralNetwork(testInputs)
diff =  out[p.NUM_NODES-1] - output
if diff < 0.01 and diff > -0.01:
    print "propagate test passed."
else: print "propagate test failed."

p.backPropagateNeuralNetwork(1.0, out, testInputs)
string = "["
for w in p.networkWeights:
    string += " {0:.3f} ".format(w)
print string, "]"