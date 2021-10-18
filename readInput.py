# Convert list of ints to a list of tuples of pairs
# [1, 1, 2, 3] -> [(1, 1), (2, 3)]
def makePairs(l):
    result = []
    if (len(l) % 2) != 0:
        return result
    # Decrease each index by 1 so they are 0-indexed
    for i in range(0, len(l) -1, 2):
        result.append((l[i] -1 , l[i + 1] -1))
    return result

# Input is 5 lines defining the board
def readProblemSpecs(path):
    with open(path, "rt") as f:
        contents = f.read().splitlines()

    # Convert strings of indices to ints
    information = [[int(contents[i].split(" ")[j]) for j in range(len(contents[i].split(" ")))] 
                                                   for i in range(len(contents))]

    # 0 - Height, Width
    numRows, numCols = information[0]

    # 1 - Number of wall blocks, coordinates of wall blocks
    numWallBlocks = information[1].pop(0)
    wallBlocks = makePairs(information[1])

    # 2 - Number of boxes, coordinates of boxes
    numBoxes = information[2].pop(0)
    boxes = makePairs(information[2])

    # 3 - Number of storage locations, coordinates of storage locations
    numStorageLocations = information[3].pop(0)
    storageLocations = makePairs(information[3])

    # 4 - Player's initial location 
    playerX, playerY = information[4]

    return (numRows, numCols, numWallBlocks, wallBlocks, numBoxes, boxes, 
            numStorageLocations, storageLocations, playerX - 1, playerY - 1)

#print(readProblemSpecs("sokoban00.txt"))