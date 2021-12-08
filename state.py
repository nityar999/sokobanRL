import readInput

def isInBounds(row, col, rows, cols):
        if row >= 0 and row < rows - 1 and col >= 0 and col < cols - 1:
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

    def otherAxis(self, axis):
        if axis == "horizontal":
            return "vertical"
        return "horizontal"

    # Freeze deadlocks are when a box cannot be moved
    def freezeDeadlocksWrapper(self, data, box):
        # Is box blocked along an axis?
        blocked = dict()
        blocked[box] = {"horizontal": False, "vertical": False}

        # Have we checked along an axis?
        checked = dict()
        checked[box] = {"horizontal": False, "vertical": False}
        return self.freezeDeadlockCheck(data, box, blocked, checked, axes= None)
    
    def freezeDeadlockCheck(self, data, box, blocked, checked, axes):

        if box not in self.boxes: return False
        boxX, boxY = box

        directions = {"vertical": (-1, 0, 1, 0), "horizontal": (0, -1, 0, 1)}

        if box not in blocked:
            blocked[box] = {"horizontal": False, "vertical": False}

        if box not in checked:
            checked[box] = {"horizontal": False, "vertical": False}

        if axes == None:
            axes = ["horizontal", "vertical"]

        for axis in ["horizontal", "vertical"]:
            if axis not in axes:
                del blocked[box][axis]
        
        # Check two directions along horizontal and vertical axes
        for axis in axes:

            # Don't check axis we've already checked
            if box in checked and checked[box][axis] == True:
                continue

            (dir1, dir2, dir3, dir4) = directions[axis]
            side1X, side1Y = boxX + dir1,  boxY + dir2
            side2X, side2Y = boxX + dir3,  boxY + dir4

            # Check for a wall on either side
            if (side1X, side1Y) in self.walls or (side2X, side2Y) in self.walls:
                blocked[box][axis] = True

            # Check for simple deadlocks on both sides
            if (side1X, side1Y) not in self.safeSquares or (side2X, side2Y) not in self.safeSquares:
                blocked[box][axis] = True

            checked[box][axis] = True

            # Check for blocked box on either side recursively that we have NOT already checked
            if (side1X, side1Y) in self.boxes: 
                # Haven't checked the box yet
                if self.freezeDeadlockCheck(data, (side1X, side1Y), blocked, checked, [self.otherAxis(axis)]):
                    blocked[box][axis] = True
                # Have checked the box already
                elif checked[(side1X, side1Y)][axis] == True:
                    if blocked[(side1X, side1Y)][axis] == True:
                        blocked[box][axis] = True

            # Check for blocked box on either side recursively that we have NOT already checked
            if (side2X, side2Y) in self.boxes: 
                # Haven't checked the box yet
                if self.freezeDeadlockCheck(data, (side2X, side2Y), blocked, checked, [self.otherAxis(axis)]):
                    blocked[box][axis] = True
                # Have checked the box already
                elif checked[(side2X, side2Y)][axis] == True:
                    if blocked[(side2X, side2Y)][axis] == True:
                        blocked[box][axis] = True

        # BASE CASE
        if axes == None:
            for box in blocked:
                for axis in blocked[box]:
                    if blocked[box][axis] == False:
                        return False
            return True

        # Every other case
        else:
            for axis in blocked[box]:
                if blocked[box][axis] == False:
                    return False
            return True

    def checkBoard(self, data, action):
        if action == None:
            print("out of moves")
            return "deadlock"
        
        (box, move) = action
        drow, dcol = move
        boxRow, boxCol = box 
        newBoxX, newBoxY = boxRow + drow, boxCol + dcol 
        agentPosition = boxRow - drow, boxCol - dcol 

        if (newBoxX, newBoxY) not in self.safeSquares:
            print("1")
            return "deadlock"

        #print("# boxes: %s - Location of boxes:%s" % (self.numBoxes, self.boxes))
        #print("# storages: %s - Location of storages:%s" % (self.numStorage, self.storage))

        e_newPosition = boxRow, boxCol # (data.agent.row + action[0], data.agent.col + action[1])
        # Check if there is a box in the position the agent want to move
        if e_newPosition in self.boxes:

            #print('There is a BOX that the agent tries to move')
            ## Expected new position for the box
            e_boxPosition = newBoxX, newBoxY #(e_newPosition[0] + action[0], e_newPosition[1] + action[1])
            #print("Expected new position of the box: (%s, %s)" % (e_boxPosition[0], e_boxPosition[1]))

            # Since we moved a box, check for freeze deadlocks (Deadlocks where a box cannot be moved)
            if self.freezeDeadlocksWrapper(data, e_boxPosition):
                print("freeze deadlock")
                return "deadlock"

            if e_newPosition in self.storage:
                #print("The agent tries to move off a box from a storage location")
                return "box off"
            ## Check if it is a valid position for storage
            if e_boxPosition in self.storage:
                ## If it is already in the boxes array, the location should be used by another box.
                if e_boxPosition not in self.boxes:
                    return "box on"
            ## Can he move the box? Or there is any obstacle in the way of the box?
            elif e_boxPosition in self.walls or e_boxPosition in self.boxes:
                #print("There is an OBSTACLE")
                #print("Is deadlock? %s" % (self.isDeadlock(e_newPosition, e_boxPosition)))
                #print("Is a deadlock position?")
                if self.isDeadlock(e_newPosition, e_boxPosition):
                    print("2")
                    return "deadlock"
            else:
                ## The next position is not a valid storage then the agent just move the box
                ## and It doesn't have any obstacle in its way
                return "move box"

        # Check for timeout after 3 minutes
        if data.time >= 1200:
            return "timeout"

        # Check for simple deadlocks
        for box in self.boxes:
            if box not in self.safeSquares:
                print("3")
                return "deadlock"

        # Check for win condition
        for box in self.boxes:
            if box not in self.storage:
                return "none"

        return "win"

    def isGameOver(self, update):
        if update == "deadlock":
            return True  
        if update == "timeout":
            return True
        if update == "win":
            return True  
        return False

    def isDeadlock(self, pos, obs):
        #print("Agent position expected: %s, Obstacle expected position: %s" % (pos, obs))
        ## If the obstacle is up or down from the agent
        if obs[0] > pos[0] or obs[0] < pos[0]:
            ## Check LEFT and RIGHT obstacle from the agent expected position
            if (pos[0], pos[1] - 1) in self.boxes or (pos[0], pos[1] - 1) in self.walls:
                return True
            elif (pos[0], pos[1] + 1) in self.boxes or (pos[0], pos[1] + 1) in self.walls:
                return True
            else:
                return False
        ## If the obstacle is to the left or the right
        elif obs[1] > pos[1] or obs[1] < pos[1]:
            ## Check UP and DOWN obstacle from the agent expected position
            if (pos[0] - 1, pos[1]) in self.boxes or (pos[0] - 1, pos[1]) in self.walls:
                return True
            elif (pos[0] + 1, pos[1] + 1) in self.boxes or (pos[0] + 1, pos[1]) in self.walls:
                return True
            else:
                return False

    def __repr__(self):
        return str(tuple(sorted(self.boxes)))

    # Need hash and eq functions to let us use State as a key in dictionaries
    def __hash__(self):
        boxes = tuple(sorted(self.boxes))
        return hash(boxes)

    def __eq__(self, other):
        if not isinstance(other, State): 
            return False
        boxes = sorted(self.boxes)
        otherBoxes = sorted(other.boxes)
        return tuple(boxes) == tuple(otherBoxes)


