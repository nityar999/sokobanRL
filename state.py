import readInput

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
    
    def checkBoard(self, data, action):
        if self.isGameOver(data):
            return "win"

    def isGameOver(self, data): 
        for (row, col) in self.boxes:
            if (row, col) not in self.storage:
                return False
        return True

    def __str__(self):
        return str(self.board)

    # Need hash and eq function to let us use State as a key in dictionaries
    def __hash__(self):
        return hash(str(self.board))

    def __eq__(self, other):
        if not isinstance(other, State): 
            return False
        return str(self.board) == str(other.board)

