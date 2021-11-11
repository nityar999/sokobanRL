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
        self.corners = self.findCorners()
        self.deadlockedSquares = set()
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

    def findCorners(self):
        corners = set()
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == 0 and self.board[row][col] not in self.storage:
                    for row1, col1, row2, col2 in ((0, -1, -1, 0), (-1, 0, 0, 1), (0, 1, 1, 0), (1, 0, 0, -1)):
                        newRow1, newCol1 = row + row1, col + col1
                        newRow2, newCol2 = row + row2, col + col2
                        if self.board[newRow1][newCol1] == "#" and self.board[newRow2][newCol2] == "#":
                            corners.add((row, col))
        return corners 

    # General algorithm for simple deadlock detection is:
    # For each storage location, locations reachable by box are safe (use DFS for search)
    # Remaining locations are deadlocks
    def simpleDeadlocks(self):
        for storageLocation in self.storage:
            # 'Place' box on storage location 
            boxLocation = storageLocation
            self.depthFirstSearch(boxLocation)

    def depthFirstSearch(self, boxLocation):
        row, col = boxLocation
        for move in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            newLocation = (row + move[0], col + move[1])
            if isInBounds(row, col, self.rows, self.cols) and newLocation not in self.deadlockedSquares:
                self.deadlockedSquares.add(boxLocation)
                self.depthFirstSearch(newLocation)
    
    def checkBoard(self, data, action):
        if (self.playerRow, self.playerCol) not in self.deadlockedSquares:
            return "deadlock"
        for boxRow, boxCol in self.boxes:
            if (boxRow, boxCol) in self.corners:
                return "deadlock"
        for (row, col) in self.boxes:
            if (row, col) not in self.storage:
                return False
            return "win"

    def isGameOver(self, data, update):
        if update == "deadlock":
            return True  
        if update == "win":
            return True
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

