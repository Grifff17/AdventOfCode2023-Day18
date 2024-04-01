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

def solvepart1():
    data = fileRead("input.txt")
    instructions = []
    for row in data:
        splitRow = row.split(" ")
        instructions.append((splitRow[0],int(splitRow[1])))

    global grid
    grid, sum, startingPos = generateGrid(instructions)

    print(startingPos)

    global checkedSpaces
    checkedSpaces = []
    enclosed, totalSpaces = flood(posAdd(startingPos, lettersDirs["U"]))
    sum = sum + totalSpaces
    # for i in range(startingPos[0]-1, startingPos[0]+2):
    #     for j in range(startingPos[1]-1, startingPos[1]+2):
    #         if inGrid((i,j), grid) and grid[i][j] != "#" and ((i,j) not in checkedSpaces):
    #             enclosed, totalSpaces = flood(grid, checkedSpaces, (i,j))
    #             if enclosed:
    #                 sum = sum + totalSpaces
    
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

sys.setrecursionlimit(100000)
threading.stack_size(134217728)
thread = threading.Thread(target=solvepart1)
thread.start()
thread.join()