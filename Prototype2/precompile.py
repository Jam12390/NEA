import math

#######################
## OTHER SUBROUTINES

def getNearestNode(absolute: tuple[float, float], nodeSep: float, nodeMap: list[list[tuple]], boundToCurve: bool = False) -> tuple[int, int]:
    xCo = absolute[1]//nodeSep #inverted x, y coordinates to stay consistent with list indexes (y, x)
    yCo = absolute[0]//nodeSep

    if xCo % nodeSep >= nodeSep/2:
        xCo += 1
    if yCo % nodeSep <= nodeSep/2:
        yCo += 1
    
    #xCo = int(min(len(nodeMap[0])-1, max(xCo, 0))) #clamp xCo to the bounds of nodeMap
    #yCo = int(min(len(nodeMap)-1, max(yCo, 0)))

    return (int(yCo), int(xCo))

def getLowerNodes(start: tuple, nodeMap: list, exclusionList: list):
    nodes = []
    currentNode = start
    while nodeMap[currentNode[0]][currentNode[1]] == " ":
        if not currentNode in exclusionList:
            nodes.append((currentNode[0], currentNode[1], None))
        currentNode = (currentNode[0]+1, currentNode[1])
    return nodes

#####################################
## PARABOLAS AND JUMPING OFF EDGES

def findJumpNodes(jumpForce: float, gravityAccel: float, maxSpeed: tuple[float, float], startingNode: tuple[int, int], nodeMap: list[list[tuple]], nodeSep: float, direction: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    foundNodes = []
    floorNodes = []

    if direction == "l":
        dirEffect = -1
    else:
        dirEffect = 1
    
    u = abs(jumpForce) #this makes sure u and a are the correct signs
    a = -abs(gravityAccel)

    currentT = 0
    currentXT = 0
    step = dirEffect * 0.1 #t step
    topNodes = []
    currentNode = startingNode
    currentNodeData = " "
    stopCurve = False

    #travelling across curve
    while (not stopCurve) and currentNode[0] in range(0, len(nodeMap)-1) and currentNode[1] in range(0, len(nodeMap[0])-1):
        currentT += step
        currentXT += dirEffect * abs(step) #t on the x axis shouldn't be effected by graph reflections
        xDisplacement = dirEffect * abs(abs(maxSpeed[1]) * currentXT)
        yDisplacement = dirEffect * ((u * currentT) + (0.5 * a * currentT**2))
        x = startingNode[1] * nodeSep + xDisplacement
        y = startingNode[0] * nodeSep - yDisplacement
        currentNode = getNearestNode(absolute=(y, x), nodeSep=nodeSep, nodeMap=nodeMap, boundToCurve=True)
        if currentNode[0] in range(0, len(nodeMap)-1) and currentNode[1] in range(0, len(nodeMap[0])-1):
            currentNodeData = nodeMap[currentNode[0]][currentNode[1]]
            if currentNodeData == " " and not currentNode in topNodes and not currentNode in foundNodes:
                topNodes.append(currentNode)
            elif currentNodeData != " ": #currentNode[0] + 1 in range(0, len(nodeMap)-1) and
                if u + a*currentT < 0 and nodeMap[currentNode[0] + 1][currentNode[1]] == " ": #checking if a roof was hit AND ds/dt is negative
                    step *= -1 #then reflect the graph
                else:
                    stopCurve = True
    constTopNodes = []
    constTopNodesBuffer = []
    while len(topNodes) != 0:
        nodeBuffer = []
        currentIndex = 0
        for node in topNodes:
            constTopNodes.append(node)
            nodeBuffer.append([])
            nodeBuffer[currentIndex] = getLowerNodes(start=node, nodeMap=nodeMap, exclusionList=foundNodes)
            if not nodeBuffer[currentIndex][len(nodeBuffer[currentIndex]) - 1] in floorNodes:
                temp = nodeBuffer[currentIndex][len(nodeBuffer[currentIndex]) - 1]
                nodeBuffer[currentIndex][len(nodeBuffer[currentIndex]) - 1] = (temp[0], temp[1], "ground")
                floorNodes.append(nodeBuffer[currentIndex][len(nodeBuffer[currentIndex])-1])
            foundNodes += nodeBuffer[currentIndex]
            currentIndex += 1

        topNodes = []
        '''
        idea: since this recursion could be problematic for large falls
        (i.e. a 1-1 relationship between x and y movement could cause too much of the graph to be added to foundNodes)
        we could just change the ratio to like 1-3 or 1-4 to limit how fast the graph expands horizontally
        '''

        excludeCoordinates = [] #janky workaround to not adding repeat coordinates to topNodes D:

        buffer = []
        bufferXCoordinate = None
        for nodeListIndex in range(0, len(nodeBuffer)):
            if bufferXCoordinate != None:
                if bufferXCoordinate != nodeBuffer[nodeListIndex][0][1]:
                    buffer.append(nodeBuffer[nodeListIndex-1])
                    constTopNodesBuffer.append(nodeBuffer[nodeListIndex][0])
                    bufferXCoordinate = nodeBuffer[nodeListIndex][0][1]
                elif nodeListIndex == len(nodeBuffer)-1:
                    buffer.append(nodeBuffer[nodeListIndex])
                    constTopNodesBuffer.append(nodeBuffer[nodeListIndex][0])
            else:
                bufferXCoordinate = nodeBuffer[nodeListIndex][0][1]
        
        nodeBuffer = buffer
        constTopNodes = constTopNodesBuffer

        for columnIndex in range(0, len(nodeBuffer)):
            for node in nodeBuffer[columnIndex]: #top to bottom
                if not node in constTopNodes and nodeBuffer[columnIndex].index(node) != 0:
                    leftNode = (node[1], node[0]-1)
                    rightNode = (node[1], node[0]+1)

                    if not leftNode[1] in excludeCoordinates and nodeMap[leftNode[0]][leftNode[1]] == " " and nodeMap[min(max(leftNode[0] - 2, 0), len(nodeMap)-1)][leftNode[1]] == " " and not leftNode in foundNodes and not leftNode in constTopNodes: #remember, + is down and - is up in pygame
                        topNodes.append(leftNode)
                        excludeCoordinates.append(leftNode[1])
                    elif nodeMap[leftNode[0]][leftNode[1]] != " " and leftNode[1] in excludeCoordinates:
                        excludeCoordinates.remove(leftNode[1])
                    
                    if not rightNode[1] in excludeCoordinates and nodeMap[rightNode[0]][rightNode[1]] == " " and nodeMap[min(max(rightNode[0] - 2, 0), len(nodeMap)-1)][rightNode[1]] == " " and not rightNode in foundNodes and not rightNode in constTopNodes: #remember, + is down and - is up in pygame
                        topNodes.append(rightNode)
                        excludeCoordinates.append(rightNode[1])
                    elif nodeMap[rightNode[0]][rightNode[1]] != " " and rightNode[1] in excludeCoordinates:
                        excludeCoordinates.remove(rightNode[1])
    
    return (foundNodes, floorNodes) #<= no way im done :O - not just yet <= need to add triangle - *still* need to add triangle <= i dont think the triangle matters

#####################
## FLOOR TRAVERSAL

def traverseFloor(startingNode: tuple, jumpHeightNodes: int, nodeMap: list) -> tuple[list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]]]:
    corners = []
    groundedNodes = []
    airNodes = []
    newFloors = []
    offset = 0
    offsetStep = 1
    for x in range(2):
        while nodeMap[min(len(nodeMap), max(startingNode[0] + 1, 0))][min(len(nodeMap[0])-1, max(startingNode[1] + offset, 0))] != " " and startingNode[0] in range(0, len(nodeMap)) and startingNode[1] + offset in range(0, len(nodeMap[0])):
            groundedNodes.append((startingNode[0], startingNode[1] + offset))
            airNodes.append([])
            for y in range(jumpHeightNodes):
                yNode = startingNode[0] - y
                if yNode in range(0, len(nodeMap)):
                    if nodeMap[yNode][startingNode[1] + offset] == " ":
                        airNodes[len(airNodes)-1].append((yNode, startingNode[1] + offset))
            offset += offsetStep
        offset -= offsetStep
        corners.append((startingNode[0], startingNode[1] + offset, "l" if offset < 0 else "r"))
        offset = 0
        offsetStep *= -1
    
    airNodes = sorted(airNodes, key=lambda node:(node[0][1]), reverse=False) #sorted on x axis
    for listIndex in range(0, len(airNodes)):
        airNodes[listIndex] = sorted(airNodes[listIndex], key=lambda node:(node[0]), reverse=True) #each list sorted on y axis
    
    for column in airNodes:
        previousState = [False, False] #left collision, right collision
        for node in column:
            if node[1] - 1 >= 0:
                if nodeMap[node[0]][node[1] - 1] == " " and previousState[0] == True:
                    newFloors.append((node[0], node[1]-1))
                    previousState[0] = False
                elif nodeMap[node[0]][node[1] - 1] != " ":
                    previousState[0] = True
                
            if node[1] + 1 <= len(nodeMap[0])-1:
                if nodeMap[node[0]][node[1] + 1] == " " and previousState[1] == True:
                    newFloors.append((node[0], node[1]+1))
                    previousState[1] = False
                elif nodeMap[node[0]][node[1] + 1] != " ":
                    previousState[1] = True
    
    compiledList = []
    for node in groundedNodes:
        compiledList.append((node[0], node[1], "ground"))
    for column in airNodes:
        for node in column:
            compiledList.append((node[0], node[1], None))
    
    return (compiledList, corners, newFloors) #newFloors are also classed as corners but we cover those anyway

####################
## PRECOMPILATION

def precompileEntityGraph(
        #Parameters for precompileEntityGraph
        origin: tuple,

        #Parameters for findJumpNodes and traverseFloor
        jumpForce: float,
        gravityAccel: float,
        maxSpeed: tuple,
        nodeMap: list,
        nodeSep: float,
        ) -> list[tuple[int, ...]]: #ITS TIME ITS TIME :DDDDDDDDDDDDDDDD
    jumpForceNodes = int(abs(-(jumpForce**2)/(2*-abs(gravityAccel))) // nodeSep)
    graph = []

    #Assume origin is grounded
    floorNodes = [(origin[0], origin[1], None)]
    cornersToCheck = []

    while len(floorNodes) != 0:
        floorBuffer = []
        for node in floorNodes:
            if not node in graph:
                response = traverseFloor(startingNode=node, jumpHeightNodes=jumpForceNodes, nodeMap=nodeMap) #responds with [compiledList, corners, newFloors]
                pass
                for responseNode in response[0]:
                    if not responseNode in graph:
                        graph.append(responseNode)
                for corner in response[1]:
                    if not corner in cornersToCheck:
                        cornersToCheck.append(corner)
                for newFloor in response[2]:
                    if not (newFloor in floorNodes and newFloor in floorBuffer):
                        floorBuffer.append(newFloor)
        
        #floorNodes = [floorBuffer[x] for x in range(0, len(floorBuffer)-1)] #WHY IS IT BEING PASSED IN BY REFERENCE
        #WHAT THE FUCK
        #PYTHON
        temp = tuple(floorBuffer)
        floorNodes = list(temp)
        floorBuffer = []
        print(temp)

        for corner in cornersToCheck:
            response = findJumpNodes(jumpForce=jumpForce, gravityAccel=gravityAccel, maxSpeed=maxSpeed, startingNode=corner, nodeMap=nodeMap, nodeSep=nodeSep, direction=corner[2])
            for newFloor in response[1]:
                if not newFloor in graph and not newFloor in floorNodes:
                    floorNodes.append(newFloor)
            for node in response[0]:
                if not node in graph:
                    graph.append(node)
        
        cornersToCheck = []
    
    return graph

if __name__ == "__main__":
    #testGraph = [
    #    [" " for x in range(20)] for x in range(4),
    #    ["#" for x in range(8), " " for x in range(12)],
    #    [" " for x in range(20)] for x in range(2),
    #    [" " for x in range(12), "#" for x in range(8)],
    #    [" " for x in range(20)] for x in range(3),
    #    ["#" for x in range(20)] for x in range(2)
    #]
    testGraph = []
    for x in range(6):
        testGraph.append([" " for x in range(20)])
    a = ["#" for x in range(9)]
    a += [" " for x in range(11)]
    testGraph.append(a)
    for x in range(2):
        testGraph.append([" " for x in range(20)])
    a = [" " for x in range(10)]
    a += ["#" for x in range(10)]
    testGraph.append(a)
    for x in range(2):
        testGraph.append([" " for x in range(20)])
    for x in range(1):
        testGraph.append(["#" for x in range(20)]) #stupid python

    #for line in testGraph:
    #    print(line)
    
    origin = (4, 19)
    origin = getLowerNodes(start=origin, nodeMap=testGraph, exclusionList=[])
    origin = origin[len(origin)-1]
    #Test data:
    jumpForce = 125

    gravityAccel = 9.81 * 15
    maxSpeed = (0, 10)
    nodeSep = 13

    response = precompileEntityGraph(origin=origin, jumpForce=jumpForce, gravityAccel=gravityAccel, maxSpeed=maxSpeed, nodeMap=testGraph, nodeSep=nodeSep)
    for node in response:
        testGraph[node[0]][node[1]] = "x"
    
    for line in testGraph:
        print(line)