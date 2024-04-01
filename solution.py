from dis import Instruction
from operator import invert
import sys
import threading
from tracemalloc import start

sys.settrace

lettersDirValues = {
    "R": 1,
    "L": -1,
    "U": -1,
    "D": 1
}
lettersDirs = {
    "U": [-1, 0],
    "R": [0, 1],
    "D": [1, 0],
    "L": [0, -1]
}
numToLetter = {
    "0": "R",
    "1": "D",
    "2": "L",
    "3": "U"
}

def solvepart1():
    #read in data
    data = fileRead("input.txt")
    instructions = []
    for row in data:
        splitRow = row.split(" ")
        instructions.append((splitRow[0],int(splitRow[1])))

    #generate grid
    global grid
    grid, sum, startingPos = generateGrid(instructions)

    print(len(grid),len(grid[0]))
    for row in grid:
        print("".join(row))

    #fill grid to calculate area of pit
    global checkedSpaces
    checkedSpaces = []
    for i in range(startingPos[0]-1, startingPos[0]+2):
        for j in range(startingPos[1]-1, startingPos[1]+2):
            if inGrid((i,j), grid) and grid[i][j] != "#" and ((i,j) not in checkedSpaces):
                enclosed, totalSpaces = flood((i,j))
                if enclosed:
                    sum = sum + totalSpaces
    print(sum)

#generates a grid with a map of the outline of the hole using the instructions
#returns the grid, the area of the trenches, and the starting position
def generateGrid(instructions):
    greatestWidth = 0
    greatestHeight = 0
    leastWidth = 0
    leastHeight = 0
    width = 0
    height = 0
    for instruction in instructions:
        if instruction[0] in ("L","R"):
            width = width + ( instruction[1] * lettersDirValues[instruction[0]] )
            if width > greatestWidth: greatestWidth = width
            if width < leastWidth: leastWidth = width
        else:
            height = height + ( instruction[1] * lettersDirValues[instruction[0]] )
            if height > greatestHeight: greatestHeight = height
            if height < leastHeight: leastHeight = height
    totalWidth = greatestWidth - leastWidth + 1
    totalHeight = greatestHeight - leastHeight + 1
    startingPos = (leastHeight * -1, leastWidth * -1 )

    grid = [ ["."] * totalWidth for _ in range(totalHeight) ]
    currentPos = startingPos
    area = 0
    grid[currentPos[0]][currentPos[1]] = "#"
    for instruction in instructions:
        dirCoords = lettersDirs[instruction[0]]
        for _ in range(1,instruction[1]+1):
            area += 1
            currentPos = posAdd(currentPos,dirCoords)
            grid[currentPos[0]][currentPos[1]] = "#"

    return grid, area, startingPos

#check if a location is fully within the trench by recursively checking all adjacent spaces, returns whether space is in pipe and how much space it covered
def flood(target):
    if ( not inGrid(target, grid) ):
        return False, 0 #location is off of grid (area is not enclosed)
    elif (grid[target[0]][target[1]] == "#") or (target in checkedSpaces):
        return True, 0 #location is invalid (trench or already checked)
    else:
        checkedSpaces.append(target)
        sumSpaces = 0;
        enclosed = True

        for dirCoord in lettersDirs.values():
            newTarget = posAdd(target, dirCoord)
            newEnclosed, numSpaces = flood(newTarget)
            sumSpaces = sumSpaces + numSpaces
            enclosed = enclosed and newEnclosed

        return enclosed, sumSpaces + 1 #location is open

def solvepart2():
    #read in data
    data = fileRead("input.txt")
    instructions = []
    for row in data:
        splitRow = row.split(" ")
        dist = int(splitRow[2][2:7],16)
        direc = numToLetter[splitRow[2][7]]
        instructions.append((direc, dist))

    #find the max and min height of the pit, plus the left-most and right-most x-y and their positions in the instructions 
    leftmostPos = (0,0)
    leftInstrIndex = -1
    rightmostPos = (0,0)
    rightInstrindex = -1
    maxHeight = 0
    minHeight = 0
    width = 0
    height = 0
    for i in range(len(instructions)):
        instruction = instructions[i]
        if instruction[0] in ("L","R"):
            width = width + ( instruction[1] * lettersDirValues[instruction[0]] )
            if width <= leftmostPos[1]:
                leftmostPos = (height, width)
                leftInstrIndex = i+1
            if width >= rightmostPos[1]:
                rightmostPos = (height, width)
                rightInstrindex = i+1
        else:
            height = height + ( instruction[1] * lettersDirValues[instruction[0]] )
            if height > maxHeight: maxHeight = height
            if height < minHeight: minHeight = height

    #find the amount of space not in the pit by adding and subtracting rectangles whenever you move sideways
    invertedSum = 0
    currentPos = leftmostPos
    currentInstrIndex = leftInstrIndex
    percentDone = 0
    prevDown = False
    downAmount = 0
    while True:
        instruction = instructions[currentInstrIndex]
        if instruction[0] in ("L","R"):
            if percentDone < .5:
                addHeight = currentPos[0] - minHeight
                if instruction[0] == "L": addHeight = addHeight + 1
            else:
                addHeight = (maxHeight - currentPos[0]) * -1
                if instruction[0] == "R": addHeight = addHeight - 1

            invertedSum = invertedSum + ( instruction[1] * addHeight * lettersDirValues[instruction[0]] )

            currentPos = (currentPos[0], currentPos[1] + ( instruction[1] * lettersDirValues[instruction[0]] ) )
        else:
            currentPos = (currentPos[0] + ( instruction[1] * lettersDirValues[instruction[0]] ), currentPos[1] )
        
        if prevDown:
            invertedSum = invertedSum - downAmount
            prevDown = False

        if percentDone == 0 or percentDone == .75:
            if instruction[0] == "D":
                prevDown = True
                downAmount = instruction[1]
            if instruction[0] == "U": 
                prevDown = False
        else:
            if instruction[0] == "D": 
                prevDown = False
            if instruction[0] == "U": 
                prevDown = True
                downAmount = instruction[1]

        if currentInstrIndex == (len(instructions)-1):
            currentInstrIndex = 0
        else:
            currentInstrIndex = currentInstrIndex + 1

        if percentDone == .5 and currentPos[0] == maxHeight:
            percentDone = .75
        if percentDone == .25 and currentPos[1] == rightmostPos[1]:
            percentDone = .5
            prevDown = False
        if percentDone == 0 and currentPos[0] == minHeight: 
            percentDone = .25

        if currentPos == leftmostPos: break

    #invert the space not in pit to find the space in pit
    sum = ( ( maxHeight - minHeight + 1 ) * ( rightmostPos[1] - leftmostPos[1] + 1 ) ) - invertedSum
    print(sum)

#adds two coordinates together
def posAdd(pos1, pos2):
    return tuple([ sum(coords) for coords in zip(pos1, pos2) ])

#checks if a coordinate is in a grid
def inGrid(pos, grid):
    return pos[0] >= 0 and pos[0] < len(grid) and pos[1] >= 0 and pos[1] < len(grid[0])

def fileRead(name):
    data = []
    f = open(name, "r")
    for line in f:
        data.append(line);
    return data


# sys.setrecursionlimit(100000)
# threading.stack_size(134217728)
# thread = threading.Thread(target=solvepart1)
# thread.start()
# thread.join()

solvepart2()