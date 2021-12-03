import json

from baseGame import *
from state import *
from agent import *

total = 10
epsilon = 0.1
gamma = 0.9
alpha = 0.5

# Initialize Q Values
with open("qvalues.json", "wt") as f:
    json.dump({}, f)

for i in range(total):

    # Setup Agent - Load Q Values, clear history
    state = State("sokoban01.txt")
    agent = Agent(state.playerRow, state.playerCol, state, epsilon, gamma, alpha)

    # Decay epsilon value
    epsilon = epsilon - (0.1*epsilon)

    # Play Game
    runGame(state, agent)

    # Save Q Values 
    agent.writeQValues(agent.q)


