import json, time

import baseGame
import gameNoAnimation
from state import *
from agent import *

import readInput

total = 100
epsilon = 0.2
gamma = 0.9
alpha = 0.5

firstWin = False
timeToFirstWin = 0
winCount = 0
initialTime = time.perf_counter()

path = "sokoban-05b.txt"

# Setup Agent - Load Q Values, clear history

numRows, numCols, numWallBlocks, wallBlocks, numBoxes, boxes, numStorageLocations, storageLocations, playerX, playerY = readInput.readProblemSpecs(path)

agent = Agent(playerX, playerY, epsilon, gamma, alpha)

# Initialize Q Values
# with open("qvalues.json", "wt") as f:
#     json.dump({}, f)

for i in range(total):
    state = State(path)
    agent.row = playerX
    agent.col = playerY

    # Decay epsilon value
    #epsilon = epsilon - (0.1*epsilon)
    # state = State("sokoban01.txt")

    # Play Game - Comment out one of these function calls
    # With Animation
    baseGame.runGame(state, agent, winCount)

    # Without Animation
    # winCount = gameNoAnimation.gameLoop(state, agent, winCount)
    if not firstWin and winCount == 1:
        timeToFirstWin = time.perf_counter() - initialTime
        firstWin = True

    agent.history = []
    #agent.writeQValues(str(agent.q))

finalTime = time.perf_counter() - initialTime
print("Total Execution Time: %d seconds" % (finalTime))
if winCount > 0:
    print("Time to first win: %d" % (timeToFirstWin))
print("Total Win Count out of %d: %d" % (total, winCount))


