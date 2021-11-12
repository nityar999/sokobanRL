import readInput

def isInBounds(row, col, rows, cols):
        if row > 0 and row < rows - 1 and col > 0 and col < cols - 1:
            return True
        return False

class State(object):

    def __init__(self, path):
        rows, cols, numWalls, walls, numBoxes, boxes, numStorage, storage, playerX, playerY = readInput.readProblemSpecs(path)
        self.rows = rows
        self.cols = cols
        self.numWalls = numWalls
        self.walls = walls
        self.numBoxes = numBoxes
        self.boxes = boxes
        self.numStorage = numStorage
        self.storage = storage
        self.playerCol = playerX
        self.playerRow = playerY
        self.board = self.createBoard()
        self.safeSquares = set()
        self.simpleDeadlocks() # Use hash table to store locations that are safe - locations
                               # not in this set are simple deadlocks

    # List representation of the board 
    def createBoard(self):
        board = [[0] * self.cols for i in range(self.rows)]
        for (row, col) in self.walls:
            board[row][col] = "#"
        for (row, col) in self.boxes:
            board[row][col] = "$"
        for (row, col) in self.storage:
            board[row][col] = "."
        board[self.playerRow][self.playerCol] = "@"
        return board    

    # General algorithm for simple deadlock detection is:
    # For each storage location, locations reachable by box are safe (use DFS for search)
    # Remaining locations are deadlocks
    def simpleDeadlocks(self):
        for storageLocation in self.storage:
            # 'Place' box on storage location 
            boxLocation = storageLocation
            self.depthFirstSearch(boxLocation)


    def depthFirstSearch(self, boxLocation):
        if boxLocation in self.safeSquares: return 
        row, col = boxLocation
        for move in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            newLocation = (row + move[0], col + move[1])
            twoStepsLocation = (newLocation[0] + move[0], newLocation[1] + move[1])
            if ((isInBounds(newLocation[0], newLocation[1], self.rows, self.cols) and (newLocation not in self.walls) and 
                (twoStepsLocation not in self.walls))):
                self.safeSquares.add(boxLocation)
                self.depthFirstSearch(newLocation)

    
    def checkBoard(self, data, action):
        for box in self.boxes:
            if box not in self.safeSquares:
                return "deadlock"
        for box in self.boxes:
            if box not in self.storage:
                return "none"
        return "win"

    def isGameOver(self, data, update):
        if update == "deadlock":
            return True  
        if update == "deadlock":
            return True  
        if update == "none":
            return False
        return False

    def __str__(self):
        return str(self.board)

    # Need hash and eq functions to let us use State as a key in dictionaries
    def __hash__(self):
        return hash(str(self.board))

    def __eq__(self, other):
        if not isinstance(other, State): 
            return False
        return str(self.board) == str(other.board)

