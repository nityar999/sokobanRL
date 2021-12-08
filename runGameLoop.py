import json, time

import baseGame
import gameNoAnimation
from state import *
from agent import *

total = 1
epsilon = 0.2
gamma = 0.9
alpha = 0.5

firstWin = False
timeToFirstWin = 0
winCount = 0
initialTime = time.perf_counter()

# Initialize Q Values
with open("qvalues.json", "wt") as f:
    json.dump({}, f)

for i in range(total):

    # Setup Agent - Load Q Values, clear history
    state = State("sokoban01.txt")
    agent = Agent(state.playerRow, state.playerCol, state, epsilon, gamma, alpha)

    # Decay epsilon value
    #epsilon = epsilon - (0.1*epsilon)

    # Play Game - Comment out one of these function calls
    # With Animation
    baseGame.runGame(state, agent, winCount)

    # Without Animation
    #winCount = gameNoAnimation.gameLoop(state, agent, winCount)
    if not firstWin and winCount == 1:
        timeToFirstWin = time.perf_counter() - initialTime
        firstWin = True

    # Save Q Values 
    # l = []
    # for state in agent.q:
    #      l.append(agent.q[state])
    # print("hi", l)

    agent.writeQValues(str(agent.q))

finalTime = time.perf_counter() - initialTime
print("Total Execution Time: %d seconds" % (finalTime))
if winCount > 0:
    print("Time to first win: %d" % (timeToFirstWin))
print("Total Win Count out of %d: %d" % (total, winCount))


