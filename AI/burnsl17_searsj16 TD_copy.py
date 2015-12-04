
from Player import *
from Ant import *
from Building import *
from AIPlayerUtils import *
import math
import pickle
import os.path

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
        # Dictionary of utility states
        self.utilList = {}

        # Keeps track of the total number of states encountered
        self.newStates = 0

        # Learning rate for reward equation
        self.alpha = 0.99

        # Rate of change for alpha
        self.alphaRate = 3

        # Amount of change for alpha
        self.alphaAmt = 0.1

        # Lambda future value of state
        self.lamb = 0.9

        # file to save our utility state into
        self.saveFile = "util.searsj16_burns17"

        # Check if file exists, if so, load util values
        try:
            self.loadUtils()
            print "Loaded util values..."
        except IOError:
            print "Could not find util file. Starting fresh..."
        
        super(AIPlayer,self).__init__(inputPlayerId, "A copy of something unique")

    ##
    # manhattanDistance
    # Description: Given two cartesian coordinates, determines the 
    #   manhattan distance between them (assuming all moves cost 1)
    #
    # Parameters:
    #   self - The object pointer
    #   pos1 - The first position
    #   pos2 - The second position
    #
    # Return: The manhattan distance
    #
    def manhattanDistance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    ##
    # compressState
    # Description: Given a state, consolidate the relevant information into a few characters
    #   based on in game values
    #
    # Parameters:
    #   self - The object pointer
    #   state - The modified state of the game
    #
    # Return: A two dimensional list containing information about the state of the game
    #
    def compressState (self, state):
        # Find the AI's player ID
        myID = PLAYER_ONE
        oppID = PLAYER_TWO
        if state.whoseTurn == PLAYER_TWO:
            myID = PLAYER_TWO
            oppID = PLAYER_ONE

        # Initialize the list to store the state data in
        compState = []

        # Find player and opponent inventories
        myInv = state.inventories[myID]
        oppInv = state.inventories[oppID]

        # Find player and opponent queens
        myQueen = myInv.getQueen()
        oppQueen = oppInv.getQueen()

        # Find a list of player structures
        myDest = [tunnel.coords for tunnel in myInv.getTunnels()]
        myDest.append(myInv.getAnthill().coords)

        # Find a list of all foods
        myFood = [item.coords for item in state.inventories[NEUTRAL].constrs if item.type == FOOD]

        # Check for win or loss conditions, save accordingly
        if oppQueen is None or myInv.foodCount >= 11 or len(oppInv.ants) <=1:
            compState.append(['W', True])
        elif myQueen is None or oppInv.foodCount >= 11 or len(myInv.ants) <=1:
            compState.append(['L', True])

        # Otherwise, save information about queens healths, and worker carrying/noncarrying status
        else:
            compState.append(["MQ", myQueen.health])
            compState.append(["OQ", oppQueen.health])

            antTotal = 0
            for ant in myInv.ants:
                if ant.type == WORKER:
                    antTotal += 1

                    if antTotal > 2:
                        break

                    if ant.carrying:
                        compState.append(['c' + str(antTotal), \
                                          min(self.manhattanDistance(ant.coords, destCoord) for destCoord in myDest)])
                    else:
                        compState.append([str(antTotal), min(self.manhattanDistance(ant.coords, foodCoord) for foodCoord in myFood)])

        return compState

    ##
    # flat
    # Description: Takes a two dimensional list and turns it into a string.
    #
    # Parameters:
    #   stateList - The two dimensional list to flatten
    #
    # Returns: Stringified version of the list
    #
    def flat(self, stateList):
        outString = ""

        for list in stateList:
            for item in list:
                outString += str(item)

        return outString

    ##
    # addStateUtil
    # Description: Adds information to the utility dictionary based on the utility of
    #       the state and the next potential state
    #
    # Parameters:
    #   state - The current state to evaluate
    #   nextState - The potential next state to evaluate
    #
    # Returns: The dictionary of utility values with flattened state lists as keys
    #
    def addStateUtil(self, state, nextState = None):
        # Get the compressed 2D version of the state and flattens it into a string
        currentStateList = self.flat(self.compressState(state))

        # If we are on the first move of the game, set the utility of the state to 0
        if nextState is None:
            if currentStateList not in self.utilList:
                self.newStates += 1

                self.utilList[currentStateList] = 0
        else:
            # Get the compressed 2D version of the nextState and flattens it into a string
            nextStateList = self.flat(self.compressState(nextState))

            # If the next state has not been seen, increment the number
            # of states seen and set its utility to 0
            if nextStateList not in self.utilList:
                self.newStates += 1
                self.utilList[nextStateList] = 0
            else:
                # If we have seen it, calculate the utility
                self.utilList[currentStateList] += self.alpha*\
                    (self.reward(currentStateList) + self.lamb * \
                     self.utilList[nextStateList] - self.utilList[currentStateList])

        return self.utilList[currentStateList]

    ##
    # reward
    # Description: Takes the string version of the state and returns a reward based on the contents
    #
    # Parameters:
    #   compState - The string version of the state
    #
    # Returns: 1.0 for a winning state, -1.0 for a losing state, or -0.01 for anything in between.
    #
    def reward(self, compState):
        if "W" in compState:
            return 1.0
        elif "L" in compState:
            return -1.0
        else:
            return -0.01

    ##
    # bestMove
    # Description: Takes all potential moves in a state and runs them through an evaluation
    #       function to determine the best move. Has a 10% chance of just doing something else
    #       instead to learn more
    #
    # Parameters:
    #   state - The current state of the game to find potential moves from
    #
    # Returns: A move for getMove() to send back to the game
    #
    def bestMove(self, state):
        # Placeholder for the current best move
        best = None

        # Arbitrarily low
        bestUtil = -999999999999999

        # Get all possible moves from the state
        moveList = listAllLegalMoves(state)

        # For each possible move, get the evaluation of the move and check if it is
        # better than the current best move
        for move in moveList:
            tempUtil = self.addStateUtil(state, self.prediction(state, move))

            if tempUtil > bestUtil:
                bestUtil = tempUtil
                best = move

        # Sometimes, just don't do what you should. Just 'cause, you know?
        if random.random() > 0.9:
            return moveList[random.randint(0, len(moveList) - 1)]

        return best

    ##
    # prediction
    # Description: Modifies a fastclone of the game state to send back
    #       based on the given move
    #
    # Parameters:
    #   currentState - The starting state
    #   move - the move to apply to the currentState
    #
    # Returns: the state resulting from the move
    #
    def prediction(self, currentState, move):
        # get a fastclone of the state
        currentState = currentState.fastclone()

        # for movement moves evaluate the ants' movements
        if move.moveType == MOVE_ANT:
            startCoord = move.coordList[0]
            endCoord = move.coordList[-1]

            #take ant from start coord
            antToMove = getAntAt(currentState, startCoord)
            #change ant's coords and hasMoved status
            antToMove.coords = (endCoord[0], endCoord[1])
            antToMove.hasMoved = True

        # for build moves, determine what was built, then add that to the appropriate list
        elif move.moveType == BUILD:
            coord = move.coordList[0]
            currentPlayerInv = currentState.inventories[currentState.whoseTurn]

            if move.buildType == TUNNEL:
                #subtract the cost of the item from the player's food count
                currentPlayerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]

                # add the tunnel to our list of constructions
                tunnel = Building(coord, TUNNEL, currentState.whoseTurn)
                currentPlayerInv.constrs += tunnel
            else:
                #subtract the cost of the item from the player's food count
                currentPlayerInv.foodCount -= UNIT_STATS[move.buildType][COST]

                # add the ant to our list of ants
                ant = Ant(coord, move.buildType, currentState.whoseTurn)
                ant.hasMoved = True
                currentState.inventories[currentState.whoseTurn].ants.append(ant)
        return currentState
	
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
        self.addStateUtil(currentState)
        return self.bestMove(currentState)
    
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
        # calculate the change in our learning factor
        lastAlpha = self.alpha
        decrement = (1.0 - (1.0 / math.exp(lastAlpha ** self.alphaRate ))) * self.alphaAmt

        # adjust a bunch of values
        self.alpha -= decrement
        self.newStates = 0
        # self.saveUtils()

    ##
    # saveUtils
    # Description: Saves a pickled copy of our utility list into a text file
    #
    def saveUtils(self):
        with open("AI/" +self.saveFile, 'wb') as file:
            pickle.dump(self.utilList, file, 0)

    ##
    # loadUtils
    # Description: Loads our utility list out of a previously pickled file
    def loadUtils(self):
        with open(self.saveFile, 'rb') as file:
            self.utilList = pickle.load(file)