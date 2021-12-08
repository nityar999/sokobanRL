import random 
import json
import math 

def isInBounds(data, row, col):
    if row >= 0 and row < data.state.rows - 1 and col >= 0 and col < data.state.cols - 1:
        return True
    return False

class Node(object):

    def __init__(self, node):
        self.node = node
        self.parent = None

    def __hash__(self):
        return hash(self.node)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.node == other.node

    def __repr__(self):
        return str(self.node)

    def pathToNode(self):
        path = []
        parent = self.parent
        while parent != None:
            path.append(parent.node)
            parent = parent.parent
        return path[::-1]

class Agent(object):

    def __init__(self, row, col, state, epsilon=0.1, gamma=0.9, learning=0.5):
        self.row = row 
        self.col = col
        self.state = state

        # What should these values be 
        self.epsilon = epsilon     # Fraction of the time agents acts randomly
        self.gamma = gamma         # Discount factor
        self.learning = learning   # Also known as alpha

        # Basic actions: LEFT, RIGHT, UP, DOWN
        self.actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Record of state and action taken from that state
        self.history = []

        # Maps state to q value for each action, initialize to 0
        # {((bx1, by1), ... (bxn, byn)): {(bx1, by1, move): q value}}}
        self.q = self.readQValues()

        self.paths = dict()

    # Read saved Q values, so agent remembers what it's learned previously
    def readQValues(self, path="qvalues.json"):
        with open(path, "rt") as f:
            contents = json.load(f)
        return contents

    def writeQValues(self, contents, path="qvalues.json"):
        with open(path, "wt") as f:
            json.dump(contents, f)

    def __repr__(self):
        return "<Agent row:%s col:%s q:%s>" % (self.row, self.col, self.q)

    # Move according to the epsilon-greedy policy
    def agentMove(self, state):

        probability = random.uniform(0, 1)
        
        # With probability epsilon, make move randomly 
        if probability < self.epsilon:
            actionIndex = random.randint(0, 3)
            action = self.actions[actionIndex]
            if str(state) not in self.q:
                self.q[state] = [0, 0, 0, 0]

        # With probability 1 - epsilon, make the optimal move given by highest q value for state 
        else: 
            if str(state) in self.q:
                qScore = self.q[str(state)]
                maxQ = max(qScore)
                if maxQ == 0:
                    indices = [i for i in range(len(qScore)) if qScore[i] == 0]
                    actionIndex = random.choice(indices)
                else:
                    actionIndex = qScore.index(maxQ)
                action = self.actions[actionIndex]
  
            else:
                self.q[str(state)] = [0, 0, 0, 0]
                actionIndex = random.randint(0, 3)
                action = self.actions[actionIndex]

        # Update history 
        self.history.append((str(state), action))
        return action 

    def possibleMoves(self, state, board, box):
        legalMoves = []
        (row, col) = box
        for (drow, dcol) in self.actions:
            newRow, newCol = row + drow, col + dcol
            if (((newRow, newCol) not in state.boxes and (newRow, newCol) not in state.walls and 
                newRow >= 0 and newRow < state.rows - 1 and newCol >= 0 and newCol < state.cols - 1)):
                legalMoves.append((drow, dcol))
        return legalMoves

    def neighbors(self, state, node, goal):
        result = []
        (row, col) = node.node 
        for (drow, dcol) in self.actions:
            newRow, newCol = row + drow, col + dcol

            if (newRow, newCol) in state.walls:
                continue

            if (newRow < 0 or newRow > state.rows - 1 or newCol < 0 or newCol > state.cols - 1):
                continue

            if (newRow, newCol) in state.boxes and (newRow, newCol) == goal:
                result.append((newRow, newCol)) 

            else:
                result.append((newRow, newCol)) 


        return result

    def reachableBoxes(self, state, board, row, col, goal):
        # BFS 
        observation = []
        node = Node((row, col))

        frontier = [node]
        while not frontier == []:

            node = frontier.pop(0)
            observation.append(node)

            for (nextRow, nextCol) in self.neighbors(state, node, goal):
                child = Node((nextRow, nextCol))
                child.parent = node

                if child == Node(goal):
                    path = child.pathToNode() + [child]
                    observation.append(child)
                    return child.node, path

                frontier.append(child)
        return None

    def getMaxQValue(self, state):
        bestQValue = -math.inf
        bestBox = None
        bestMove = None

        for (box, move) in self.q[state]:
            qValue = self.q[state][(box, move)]
            if qValue >= bestQValue:
                bestQValue = qValue
                bestBox = box
                bestMove = move 

        return bestBox, bestMove, bestQValue

    def agentMoveMacro(self, state, board):
        #print("move before", self.q)
        # List of reachable boxes and path to box given state and agent position 
        legalBoxes = []
        for (row, col) in state.boxes:
            result = self.reachableBoxes(state, board, self.row, self.col, (row, col))
            if result != None:
                box, path = result
                self.paths[(box, (self.row, self.col))] = path
                legalBoxes.append(box)

        probability = random.uniform(0, 1)
        
        # With probability epsilon, make move randomly 
        if probability < self.epsilon:

            # Initialize state for all boxes and actions
            if str(state) not in self.q:
                self.q[state] = dict()
                for block in state.boxes:
                    for direction in self.actions:
                        self.q[state][(block, direction)] = 0

            boxIndex = random.randint(0, len(legalBoxes) - 1)
            box = legalBoxes[boxIndex]

            # These are all of the moves that can be applied to the chosen box
            legalMoves = self.possibleMoves(state, board, box)
            moveIndex = random.randint(0, len(legalMoves) - 1)
            move = legalMoves[moveIndex]
            action = (box, move)

        # With probability 1 - epsilon, make the optimal move given by highest q value for state 
        else: 
            if str(state) in self.q:
                box, move, qScore = self.getMaxQValue(state)
                action = (box, move)
  
            else:
                # Initialize state for all boxes and actions 
                self.q[state] = dict()
                for block in state.boxes:
                    for direction in self.actions:
                        self.q[state][(block, direction)] = 0

                boxIndex = random.randint(0, len(legalBoxes) - 1)
                box = legalBoxes[boxIndex]

                legalMoves = self.possibleMoves(state, board, box)
                moveIndex = random.randint(0, len(legalMoves) - 1)
                move = legalMoves[moveIndex]

                action = (box, move)
        #print("move after", self.q)
        # Update history: box locations, agent location, action takes
        self.history.append((str(state), (self.row, self.col), action))
        return action 


    def movePlayer(self, data, state, action):
        (box, move) = action 
        drow, dcol = move 
        boxX, boxY = box 

        self.row = boxX - drow
        self.col = boxY - dcol 

        # Calculate new indices of the player and any adjacent box
        newPosition = (self.row + drow, self.col + dcol)
        boxPosition = (newPosition[0] + drow, newPosition[1] + dcol)

        #  Check if we're moving in the direction of an adjacent box
        if newPosition in data.state.boxes:
            # if box is next to another box, do nothing
            if boxPosition in data.state.boxes:
                return
            # Move box and player if both are in bounds
            if isInBounds(data, boxPosition[0], boxPosition[1]) and data.board[boxPosition[0]][boxPosition[1]] in [0, '.']:
                data.state.boxes.remove(newPosition)
                data.state.boxes.append(boxPosition)
                (self.row, self.col) = newPosition
                data.state.playerRow, data.state.playerCol = newPosition
                data.board = data.state.createBoard()
                self.state = data.state
            
        # No adjacent box, move player only
        elif isInBounds(data, newPosition[0], newPosition[1]) and data.board[newPosition[0]][newPosition[1]] in [0, '.']:
            (self.row, self.col) = newPosition
            data.state.playerRow, data.state.playerCol = newPosition
            data.board = data.state.createBoard()
            self.state = data.state

    def qValueUpdate(self, update, action, state):
        #print("update before", self.q)
        if len(self.history) < 2:
            return
        s1, a1, s0, a0 = self.history[-1][0], self.history[-1][2], self.history[-2][0], self.history[-2][2]
        # Compute rewards for the action
        if update == "deadlock": 
            reward = - 100
        elif update == "timeout":
            reward = -100
        elif update == "win":
            reward = 100
        elif update == "box on":
            reward = 10
        elif update == "box off": 
            reward = -10
        ## Adding rewards for just move a box
        #elif update == "move box":
        #    reward = 5
        else:
            reward = -1

        # Update q values for the state 
        if s0 not in self.q:
            #print("HELLO", s0, state.boxes)
            self.q[s0] = dict()
            for block in eval(s0):
                for direction in self.actions:
                    self.q[s0][(block, direction)] = 0
        if s1 not in self.q:
            self.q[s1] = dict()
            for block in eval(s1):
                for direction in self.actions:
                    self.q[s1][(block, direction)] = 0

        # Update q values for the state
        # print("s0", s0)
        # print("a0", a0)
        # #print("s1", s1)
        # #print("a1", a1)
        # print("q", self.q)
        # print("q[s0]", self.q[s0])
        # print("update after", self.q)

        currQValue = self.q[s0][a0]
        _, _, maxQValueS1 = self.getMaxQValue(s1)
        self.q[s0][a0] += self.learning*(reward + self.gamma*(maxQValueS1) - currQValue) 

