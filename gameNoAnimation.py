import time
from state import *
from agent import *

class Struct(object): pass

# Game Loop with no animation
def gameLoop(state, agent, count):

    data = Struct()
    data.state = state
    data.board = data.state.board
    data.agent = agent 
    data.time = 0
    data.isGameOver = False

    data.initialTime = time.perf_counter()

    while not data.isGameOver:
        data.time += 1

        # Get Action from epsilon greedy policy
        action = data.agent.agentMoveMacro(data.state, data.board, data)

        if action == None: 
            data.isGameOver = True

        # Check for outcome 
        update = data.state.checkBoard(data, action) 
        #print("ACTION: (%s, %s)" % (action[0], action[1]))

        #print("EXPECTED OUTCOME: %s" % (update))

        # Wait for 2 seconds
        #time.sleep(5)

        # Update q values
        data.agent.qValueUpdate(update, action, data.state)

        # Move Agent
        data.agent.movePlayer(data, data.state, action)

        if update == "win":
            count += 1

        # Check for game over condition 
        data.isGameOver = data.state.isGameOver(update)

        winFlag = True
        for box in data.state.boxes:
            if box not in data.state.storage:
                winFlag = False
        if winFlag: data.isGameOver 

    # List of moves til end of time
    moves = []
    for (state, path, action) in data.agent.history:
        moves.append(action)

    finalTime = time.perf_counter() - data.initialTime
    #print("Execution Time: %s seconds" % (finalTime))

    return count

