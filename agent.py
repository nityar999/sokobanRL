import random 

def isInBounds(data, row, col):
    if row > 0 and row < data.state.rows - 1 and col > 0 and col < data.state.cols - 1:
        return True
    return False

class Agent(object):

    def __init__(self, row, col, state):
        self.row = row 
        self.col = col
        self.state = state

        # what should these values be 
        self.epsilon = 0.1      # fraction of the time agents acts randomly
        self.gamma = 0.9        # discount factor
        self.learning = 0.5     # also known as alpha

        # Basic actions: LEFT, RIGHT, UP, DOWN
        self.actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Record of state and action taken from that state
        self.history = []

        # Maps state to q value for each action, initialize to 0
        # {state: [0, 0, 0, 0]}
        self.q = {}

    def __repr__(self):
        return "<Agent row:%s col:%s q:%s>" % (self.row, self.col, self.q)

    # Move according to the epsilon-greedy policy
    def agentMove(self, state):

        probability = random.uniform(0, 1)
        
        # With probability epsilon, make move randomly 
        if probability < self.epsilon:
            action = random.choice(self.actions)
        # With probability 1 - epsilon, make the optimal move given by highest q value for state 
        else: 
            if str(state) in self.q:
                qScore = self.q[str(state)]
                actionIndex = qScore.index(max(qScore))
                action = self.actions[actionIndex]
            else:
                self.q[str(state)] = [0, 0, 0, 0]
                action = random.choice(self.actions)
        # Update history 
        self.history.append((str(state), action))
        return action 

    def movePlayer(self, data, state, action):
        # Calculate new indices of the player and any adjacent box
        newPosition = (self.row + action[0], self.col + action[1])
        boxPosition = (newPosition[0] + action[0], newPosition[1] + action[1])

        #  Check if we're moving in the direction of an adjacent box
        if newPosition in data.state.boxes:
            # if box is next to another box, do nothing
            if boxPosition in data.state.boxes:
                return
            # Move box and player if both and in bounds
            if isInBounds(data, boxPosition[0], boxPosition[1]) and data.board[boxPosition[0]][boxPosition[1]] in [0, '.']:
                data.state.boxes.remove(newPosition)
                data.state.boxes.append(boxPosition)
                (self.row, self.col) = newPosition
                data.state.playerRow, data.state.playerCol = newPosition
                data.state.createBoard()
                self.state = data.state
            
        # No adjacent box, move player only
        elif isInBounds(data, newPosition[0], newPosition[1]) and data.board[newPosition[0]][newPosition[1]] in [0, '.']:
            (self.row, self.col) = newPosition
            data.state.playerRow, data.state.playerCol = newPosition
            data.state.createBoard()
            self.state = data.state

    def qValueUpdate(self, update):
        if len(self.history) < 2:
            return
        s1, a1, s0, a0 = self.history[-1][0], self.history[-1][1], self.history[-2][0], self.history[-2][1]
        # Compute rewards for the action
        if update == "deadlock": 
            reward = - 100
        elif update == "win":
            reward = 100
        elif update == "box on":
            reward = 10
        elif update == "box off": 
            reward = -10
        else:
            reward = -1
        # Update q values for the state
        currQValue = self.q[s0][self.actions.index(a0)]
        self.q[s0][self.actions.index(a0)] += self.learning*(reward + self.gamma*(max(self.q[s1])) - currQValue) 

