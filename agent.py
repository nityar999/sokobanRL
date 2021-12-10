import random 
import json
import math 
import copy

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

    def __init__(self, row, col, epsilon=0.1, gamma=0.9, learning=0.5):
        self.row = row 
        self.col = col

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
        self.q = dict() # self.readQValues()

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

    def possibleMoves(self, state, box, agentLocation):
        legalMoves = []
        agentX, agentY = agentLocation
        visited = self.paths[(box, agentLocation)]

        for (drow, dcol) in self.actions:
            
            boxRow, boxCol = box 
            newBoxX, newBoxY = boxRow + drow, boxCol + dcol 
            newAgentX, newAgentY = boxRow - drow, boxCol - dcol 

            if (newAgentX, newAgentY) not in visited:
                continue

            if (newAgentX, newAgentY) in state.boxes or (newAgentX, newAgentY) in state.walls:
                continue

            if (((newBoxX, newBoxY) not in state.boxes and (newBoxX, newBoxY) not in state.walls and 
                newBoxX >= 0 and newBoxX <= state.cols - 1 and newBoxY >= 0 and newBoxY <= state.rows - 1 and 
                newAgentX >= 0 and newAgentX <= state.cols - 1 and newAgentY >= 0 and newAgentY <= state.rows - 1)):
                legalMoves.append((drow, dcol))

        return legalMoves

    def isValid(self, state, row,col, move, goal):
        drow,dcol = move
        newRow, newCol = row + drow, col + dcol

        if (newRow, newCol) == goal:
            return True

        if (newRow, newCol) in state.walls:
            return False

        if (newRow < 0 or newRow > state.cols - 1 or newCol < 0 or newCol > state.rows - 1):
            return False

        if (newRow, newCol) in state.boxes:
            return False

        return True

    def reachableBoxes(self, state, board, row, col, goal):
        # Use recursive backtracking 
        maze = board
        rows,cols = len(maze),len(maze[0])
        visited = set()
        targetRow,targetCol = goal
        def solve(row,col):
            # base cases
            if (row,col) in visited: return False
            visited.add((row,col))
            if (row,col)==(targetRow,targetCol): return True
            # recursive case
            for drow,dcol in self.actions:
                if self.isValid(state, row,col,(drow,dcol), goal):
                    if solve(row+drow,col+dcol):
                        return True
            visited.remove((row,col))
            return False
        return visited if solve(self.row, self.col) else None

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

    def agentMoveMacro(self, state, board, data):

        # List of reachable boxes and path to box given state and agent position 
        legalBoxes = []
        for (row, col) in state.boxes:
            result = self.reachableBoxes(state, board, self.row, self.col, (row, col))
            if result != None:
                path = result
                self.paths[((row, col), (self.row, self.col))] = path
                legalBoxes.append((row, col))

        probability = random.uniform(0, 1)
        
        # With probability epsilon, make move randomly 
        if probability < self.epsilon:
            # Initialize state for all boxes and actions
            if state not in self.q:
                self.q[state] = dict()
                for block in state.boxes:
                    for direction in self.actions:
                        self.q[state][(block, direction)] = 0

            legalMoves = []
            # Ensure we choose a box with moves 
            for i in range(len(state.boxes)): 
                boxIndex = random.randint(0, len(legalBoxes) - 1)
                box = legalBoxes[boxIndex]
                # These are all of the moves that can be applied to the chosen box
                legalMoves = self.possibleMoves(state, box, (self.row, self.col))
                if len(legalMoves) > 0:
                    break

            if len(legalMoves) == 0: 
                data.isGameOver = True
                return
            moveIndex = random.randint(0, len(legalMoves) - 1)
            move = legalMoves[moveIndex]
            action = (box, move)

        # With probability 1 - epsilon, make the optimal move given by highest q value for state 
        else: 
            if state in self.q:
                box, move, qScore = self.getMaxQValue(state)
                action = (box, move)
  
            else:
                # Initialize state for all boxes and actions 
                self.q[state] = dict()
                for block in state.boxes:
                    for direction in self.actions:
                        self.q[state][(block, direction)] = 0

                legalMoves = []
                # Ensure we choose a box with moves 
                for i in range(len(state.boxes)): 
                    boxIndex = random.randint(0, len(legalBoxes) - 1)
                    box = legalBoxes[boxIndex]
                    # These are all of the moves that can be applied to the chosen box
                    legalMoves = self.possibleMoves(state, box, (self.row, self.col))
                    if len(legalMoves) > 0:
                        break

                if len(legalMoves) == 0: 
                    data.isGameOver = True
                    return
                moveIndex = random.randint(0, len(legalMoves) - 1)
                move = legalMoves[moveIndex]
                action = (box, move)

        # Update history: box locations, agent location, action takes
        stateCopy = copy.deepcopy(state)
        self.history.append((stateCopy, (self.row, self.col), action))
        return action 


    def movePlayer(self, data, state, action):

        if action == None:
            return 
        (box, move) = action 
        drow, dcol = move 
        boxX, boxY = box 

        # self.row = boxX - drow
        # self.col = boxY - dcol 

        # Calculate new indices of the player and any adjacent box
        #newPosition = (self.row + drow, self.col + dcol)
        newPosition = boxX, boxY
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
            
        # No adjacent box, move player only
        elif isInBounds(data, newPosition[0], newPosition[1]) and data.board[newPosition[0]][newPosition[1]] in [0, '.']:
            (self.row, self.col) = newPosition
            data.state.playerRow, data.state.playerCol = newPosition
            data.board = data.state.createBoard()

    def qValueUpdate(self, update, action, state):
        print(self.q)

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
            self.q[s0] = dict()
            for block in s0.boxes:
                for direction in self.actions:
                    self.q[s0][(block, direction)] = 0
        if s1 not in self.q:
            self.q[s1] = dict()
            for block in s1.boxes:
                for direction in self.actions:
                    self.q[s1][(block, direction)] = 0

        # Update q values for the state
        currQValue = self.q[s0][a0]
        _, _, maxQValueS1 = self.getMaxQValue(s1)
        self.q[s0][a0] += self.learning*(reward + self.gamma*(maxQValueS1) - currQValue) 

