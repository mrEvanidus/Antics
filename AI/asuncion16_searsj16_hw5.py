__authors__ = "Chandler Underwood, Jaimiey Sears, Ryan Asuncion"
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
import difflib


# #
# AIPlayer
# Description: The responsibility of this class is to interact with the game by
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
        super(AIPlayer, self).__init__(inputPlayerId, "Genetic Player")
        self.limit = 5
        self.firstMove = True

        # vars to support genetic algorithms
        self.POPULATION_SIZE = 32
        self.GENERATION_CAP = 20 #currently unused
        self.NUM_GAMES = 10
        self.RANDOM_NUMBER_CAP = 1000
        self.gamesPlayed = 0
        self.population = []
        self.nextGeneIdx = 0
        self.fitness = []
        self.geneInit(self.population, self.fitness)

    ##
    # geneInit
    # Description: Initializes a random population
    #
    # Parameters:
    #     pop - the population to populate
    #     fit - array of ints to populate with fitness's
    ##
    def geneInit(self, pop, fit):
        for i in range(self.POPULATION_SIZE):
            gene = self.generateRandomGene()
            pop.append(gene)
            fit.append(0)

    ##
    # generateRandomGene
    # Description: generates a gene filled with random numbers between 0 and RANDOM_NUMBER_CAP
    #
    # Returns: an array of integers between 0 and RANDOM_NUMBER_CAP
    ##
    def generateRandomGene(self):
        sequence = []
        for i in range(40):
            sequence.append(random.randint(0, self.RANDOM_NUMBER_CAP))

        return sequence

    ##
    # mate
    # Description: mates two genes together to produce two children
    #
    # Parameters:
    #     parent1, parent2 - parent genes to mate, as arrays of integers
    #     debug - if True, the method will print the mating process
    #
    # Returns:
    #     child1, child2 - the two children which are the result of splicing.
    ##
    def mate(self, parent1, parent2, debug=False):
        # slice randomly in the middle part of the gene
        split = random.randint(9, 30)
        child1 = parent1[:split] + parent2[split:]
        child2 = parent2[:split] + parent1[split:]



        #implement a 2% mutation rate for each child
        if random.randint(0, 100) >= 99:
            if debug: print "Mutating child 1"
            self.mutate(child1)
        if random.randint(0, 100) >= 99:
            if debug: print "Mutating child 2"
            self.mutate(child2)

         # print a debug message if prompted
        if debug:
            print "Parent 1:", parent1[:split], "\n+\n", parent1[split:]
            print "------------------------------------------------------------------------------------"
            print "Parent 2:", parent2[:split], "\n+\n", parent2[split:]
            print "===================================================================================="
            print "Child 1:", child1[:split], "\n+\n", child1[split:]
            print "------------------------------------------------------------------------------------"
            print "Child 2:", child2[:split], "\n+\n", child2[split:]

        return child1, child2

    ##
    # mutate
    # Description: mutates a random element in a gene sequence
    #
    # Parameters: gene - the gene to mutate
    ##
    def mutate(self, gene):
        gene[random.randint(0, 39)] = random.randint(0, self.RANDOM_NUMBER_CAP)

    ##
    # newGeneration
    # Description: creates a new generation from the current one
    ##
    def newGeneration(self):
        # copy fitness list so we don't write over it
        fitnessCopy = self.fitness[:]

        #get the top half of the population (elite parents)
        maxIndices = []
        for i in range(self.POPULATION_SIZE/2):
            maxIdx = 0
            for j in range(len(fitnessCopy)):
                if fitnessCopy[maxIdx] < fitnessCopy[j]:
                    maxIdx = j
            maxIndices.append(maxIdx)
            fitnessCopy[maxIdx] = float("-inf")

        # randomly select parents to mate
        children = []
        for i in range(self.POPULATION_SIZE/4):
            randIdx1 = random.randint(0, len(maxIndices)-1)
            randIdx2 = random.randint(0, len(maxIndices)-1)

            # avoid cloning
            while randIdx1 == randIdx2:
                randIdx2 = random.randint(0, len(maxIndices)-1)

            # mate the selected parents
            child1, child2 = self.mate(self.population[randIdx1], self.population[randIdx2])
            children.append(child1)
            children.append(child2)

        # create the next generation using the children and the elite parents
        newPopulation = children[:]
        for idx in maxIndices:
            newPopulation.append(self.population[idx])

        # reset the fitness array
        for i in range(len(self.fitness)):
            self.fitness[i] = 0

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

    # maxNode
    # Description: Takes in a list of nodes and returns the node with the
    #		highest eval Score.
    #
    # Parameters:
    #	nodeList - list of nodes to evaluate
    #
    # Returns:
    #	node with the highest score
    def maxNode(self, nodeList):
        maxNode = nodeList[0]
        for node in nodeList:
            if node['score'] > maxNode['score']:
                maxNode = node

        return maxNode

    # minNode
    # Description: Takes in a list of nodes and returns the node with the
    #		lowest eval Score.
    #
    # Parameters:
    #	nodeList - list of nodes to evaluate
    #
    # Returns:
    #	node with the lowest score
    def minNode(self, nodeList):
        minNode = nodeList[0]
        for node in nodeList:
            if node['score'] > minNode['score']:
                minNode = node

        return minNode

    # recursiveSearch
    # Description: Given a state and current depth, recursively search tree
    #				of nodes that can be reached from this state
    #
    # Parameters:
    #	currentState: the state currently being searched from
    #	playerID: id of the player whose turn is currently being played
    #	currentDepth: the depth of the tree being searched
    #
    # Returns:
    #	the best move to make, along with an evaluation score for that move
    def recursiveSearch(self, parentNode, currentDepth, alpha, beta):

        # Sanity check
        if parentNode is None:
            return 0

        # Determining the playerId of this state to allow for both players to make moves
        playerID = parentNode['state'].whoseTurn

        # all moves from current state
        moves = listAllLegalMoves(parentNode['state'])

        # initialize variables
        result = None
        nodeList = []
        numNodes = 0

        # evaluate all nodes in tree
        for move in moves:
            # perform evaluation of node after move
            nextState = self.expandNode(parentNode['state'], move)
            evalScore = self.evaluateState(nextState)

            # update alpha/beta values for first time through recursion
            if playerID == self.playerId:
                if evalScore > beta:
                    beta = evalScore
            else:
                if evalScore < alpha:
                    alpha = evalScore

            # create a node with the calculated values
            node = self.createNode(move, nextState, evalScore, parentNode)
            nodeList.append(node)

        # recurse here: replace the node's score with it's branch score
        if currentDepth != self.limit:
            for node in nodeList:

                if playerID == self.playerId and node['score'] <= beta:
                    # skip ahead if this move isn't better
                    continue
                elif node['score'] >= alpha:
                    # skip ahead if this move isn't better
                    continue

                # Recurse down to get a score for the total branch
                branch = self.recursiveSearch(node, currentDepth + 1, alpha, beta)

                # update this nodes score to reflect the whole branch
                node['score'] = branch[1]

                # update alpha and beta scores if necessary
                if playerID == self.playerId and node['score'] > branch[3]:
                    beta = branch[3]
                elif node['score'] < branch[2]:
                    alpha = branch[2]

        # find the move that would be selected, no matter whose turn it is
        if playerID == self.playerId:
            result = self.maxNode(nodeList)
        else:
            result = self.minNode(nodeList)

        # Return the winning move, the winning score, and alpha and beta values
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
        currentGene = self.population[self.nextGeneIdx]

        if currentState.phase == SETUP_PHASE_1:
            result = []

            # copy of gene
            gene = currentGene[:]

            # find the top 11 coords
            for i in range(11):
                maxIdx = 0
                for j in range(40):
                    if gene[maxIdx] < gene[j]:
                        maxIdx = j
                y = maxIdx % 4
                x = int(maxIdx / 4)
                result.append((x, y))

                # don't visit this place again
                gene[maxIdx] = -1

            return result

        elif currentState.phase == SETUP_PHASE_2:
            result = []

            # copy of gene
            gene = currentGene[:]

            # find the top 2 unoccupied coords
            while len(result) < 2:
                minIdx = 0
                for j in range(40):
                    if gene[minIdx] > gene[j]:
                        minIdx = j
                y = minIdx % 4 + 6
                x = int(minIdx / 4)

                if getConstrAt(currentState, (x,y)) is None:
                    result.append((x, y))

                # don't visit this place again
                gene[minIdx] = self.RANDOM_NUMBER_CAP + 1

            return result

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

        # on the first move of every game, print the state
        if self.firstMove:
            asciiPrintState(currentState)
            print "\n"
            self.firstMove = False

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
        # gameState.whoseTurn = self.playerId
        ourInventory = gameState.inventories[currentState.whoseTurn]
        opponentId = self.getOpponentId(currentState)

        if move.moveType == MOVE_ANT:
            antToMove = None
            for ant in ourInventory.ants:
                if ant.coords == move.coordList[0]:
                    antToMove = ant
            if antToMove is not None:
                antToMove.coords = move.coordList[-1]
                # antToMove.hasMoved = True

                # check if other ants near by for attack
                # opponentId = self.getOpponentId(currentState)
                enemyInv = gameState.inventories[opponentId]
                ## Checks if can attack.
                self.attackSequence(enemyInv, antToMove)

        elif move.moveType == BUILD:
            # just worried about building Ants and Tunnel
            if move.buildType == WORKER:
                # add ant
                ourInventory.ants.append(Ant(move.coordList[-1], WORKER, currentState.whoseTurn))
                # subtract food
                ourInventory.foodCount -= 1
            elif move.buildType == DRONE:
                ourInventory.ants.append(Ant(move.coordList[-1], DRONE, currentState.whoseTurn))
                ourInventory.foodCount -= 1
            elif move.buildType == SOLDIER:
                ourInventory.ants.append(Ant(move.coordList[-1], SOLDIER, currentState.whoseTurn))
                ourInventory.foodCount -= 2
            elif move.buildType == R_SOLDIER:
                ourInventory.ants.append(Ant(move.coordList[-1], R_SOLDIER, currentState.whoseTurn))
                ourInventory.foodCount -= 2
            elif move.buildType == TUNNEL:
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
    def attackSequence(self, enemyInv, antToMove):
        attackedAntList = []
        for ant in enemyInv.ants:
            if self.isValidAttack(antToMove, ant.coords):
                # keep track of valid ants to attack
                attackedAntList.append(ant)

        if len(attackedAntList) > 0:
            antToAttack = attackedAntList[random.randint(0, len(attackedAntList) - 1)]
            # subtract health
            if antToMove == SOLDIER or antToMove == QUEEN:
                antToAttack.health -= 2
            else:
                antToAttack.health -= 1
            # if ant dies, remove it from list
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
                                        getConstrAt(gameState, ant.coords).type == ANTHILL \
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
            opponentId = (opponentId + 1) % 2

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

        score = sumScore / 8  # divide by number of catagories to
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
        ourHealth = -1
        enHealth = -1
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
        score = (1 / 2) * ratio

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

        # return score
        return diff / (bound * 2) + 0.5

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
        return (-dist + bound) / float(bound)

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
        # return math.sqrt((dest[0] - ant.coords[0])**2 + (dest[1] - ant.coords[1])**2)
        # return stepsToReach(gameState, ant.coords, dest)

    ##
    # registerWin
    # Description: The last method, registerWin, is called when the game ends and simply
    # indicates to the AI whether it has won or lost the game. This is to help with
    # learning algorithms to develop more successful strategies.
    #
    # Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):
        # update fitness
        if hasWon:
            self.fitness[self.nextGeneIdx] += 1
        else:
            self.fitness[self.nextGeneIdx] -= 1

        # advance to next gene
        self.gamesPlayed += 1
        if self.gamesPlayed >= self.NUM_GAMES:
            self.nextGeneIdx += 1
            self.gamesPlayed = 0

        # create new generation
        if self.nextGeneIdx >= self.POPULATION_SIZE:
            # print "Fitnesses:", self.fitness
            self.newGeneration()
            self.nextGeneIdx = 0

        #reset the first move
        self.firstMove = True


