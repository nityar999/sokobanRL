import time
from state import *
from agent import *
from tkinter import *

def init(data, state, agent):
    data.state = state 
    data.board = data.state.board
    data.agent = agent

    data.boxWidth = data.width / data.state.cols
    data.boxHeight = data.height / data.state.rows

    data.time = 0
    data.isGameOver = False

    # Start timing execution time
    data.initialTime = time.perf_counter()

# Handles input from mouse 
def mousePressed(event, data):
    pass

# Convert string to direction
def actionDict(move):
    if move == "Up":
        return (-1, 0)
    elif move == "Down":
        return (1, 0)
    elif move == "Left":
        return (0, -1)
    elif move == "Right":
        return (0, 1)

# Handles input from keyboard - evetn.keysym is the key that was pressed
# For Human Control
def keyPressed(event, data):
    # Resets state
    if event.keysym == "space":
        init(data)

    if event.keysym in ["Up", "Down", "Left", "Right"]:
        data.agent.movePlayer(data, data.state, actionDict(event.keysym))

    # Check for game over condition after every action
    data.isGameOver = data.state.isGameOver(data)

# Handles time based events
# AI moves in this loop
def timerFired(data):
    data.time += 1
    if not data.isGameOver:

        # Move happens every second
        
        #if data.time % 1 == 0:

        # Get Action from epsilon greedy policy
        action = data.agent.agentMove(data.board)

        # Check for outcome 
        update = data.state.checkBoard(data, action) 

        #print("ACTION: (%s, %s)" % (action[0], action[1]))

        #print("EXPECTED OUTCOME: %s" % (update))

        # Wait for 2 seconds
        #time.sleep(5)

        # Move Agent
        data.agent.movePlayer(data, data.board, action)

        # Update q values
        data.agent.qValueUpdate(update)

        if update == "win":
            data.winCount += 1
            print("WIN")

        # Check for game over condition 
        data.isGameOver = data.state.isGameOver(update)
        if data.isGameOver: print(update)
    else:
        finalTime = time.perf_counter() - data.initialTime
        print("Execution Time: %s seconds" % (finalTime))
        data.root.destroy()

####################################
# Draw Functions
####################################

# Draw game over screen
def drawGameOver(canvas, data):
    canvas.create_text(data.width / 2, data.height / 2, text = "Game Over!")

# Draw boxes and storage locations
def drawBoard(canvas, data):
    for row in range(len(data.board)):
        for col in range(len(data.board[row])):
            if data.board[row][col] == '#':
                canvas.create_rectangle(data.boxWidth * col, data.boxHeight * row, 
                    data.boxWidth * (col + 1), data.boxHeight * (row + 1), fill = "beige")
            if data.board[row][col] == '.':
                canvas.create_oval(data.boxWidth * col + 15, data.boxHeight * row + 15, 
                    data.boxWidth * (col + 1) - 15, data.boxHeight * (row + 1) - 15, fill = "pink")

# Draw player
def drawPlayer(canvas, data):
    canvas.create_oval(data.boxWidth * data.agent.col, data.boxHeight * data.agent.row, 
                    data.boxWidth * (data.agent.col + 1), data.boxHeight * (data.agent.row + 1), fill = "red")

# Draw boxes, can draw over storage locations
def drawBoxes(canvas, data):
    for (row, col) in data.state.boxes:
        canvas.create_rectangle(data.boxWidth * col, data.boxHeight * row, 
                    data.boxWidth * (col + 1), data.boxHeight * (row + 1), fill = "brown")

# Highlight safe squares (not simple deadlocks)
def drawSafeLocations(canvas, data):
    for (row, col) in data.state.safeSquares:
        canvas.create_rectangle(data.boxWidth * col, data.boxHeight * row, 
                    data.boxWidth * (col + 1), data.boxHeight * (row + 1), fill = "light blue")

def redrawAll(canvas, data):
    if data.isGameOver:
        drawGameOver(canvas, data)
        return

    drawSafeLocations(canvas, data)
    drawBoard(canvas, data)
    drawPlayer(canvas, data)
    drawBoxes(canvas, data)

####################################
# Run Game
####################################

def runGame(state, agent, winCount, width=800, height=800):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    data.winCount = winCount
    init(data, state, agent)
    # create the root and the canvas
    root = Tk()
    data.root = root
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")
