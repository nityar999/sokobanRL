import json

from baseGame import *
from state import *
from agent import *

total = 25

# Initialize Q Values
with open("qvalues.json", "wt") as f:
    json.dump({}, f)

for i in range(total): 

    # Setup Agent - Load Q Values, clear history
    state = State("sokoban01.txt")
    agent = Agent(state.playerRow, state.playerCol, state)

    # Update epsilon value here?????
    # Decay epsilon

    # Play Game
    runGame(state, agent)

    # Save Q Values 
    agent.writeQValues(agent.q)


