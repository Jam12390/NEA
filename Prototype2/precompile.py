import math

def getNearestNode(absolute: tuple, nodeSep: float, nodeMap: list, ignoreRounding: bool = False):
    xCo = absolute[1]//nodeSep #inverted x, y coordinates to stay consistent with list indexes (y, x)
    yCo = absolute[0]//nodeSep

    if not ignoreRounding:
        if xCo % nodeSep >= nodeSep/2:
            xCo += 1
    else:
        if yCo % nodeSep >= nodeSep/2:
            yCo += 1
    
    xCo = min(len(nodeMap[0])-1, max(xCo, 0)) #clamp xCo to the bounds of nodeMap
    yCo = min(len(nodeMap)-1, max(yCo, 0))

    return (yCo, xCo)

def getLowerNodes(start: tuple, nodeMap: list, exclusionList: list):
    nodes = []
    currentNode = start
    while nodeMap[currentNode[0]][currentNode[1]] == "":
        if not currentNode in exclusionList:
            nodes.append(currentNode)
        currentNode = (currentNode[0]+1, currentNode[1])
    return nodes

def findJumpNodes(jumpForce: float, gravityAccel: float, maxSpeed: tuple, startingNode: tuple, nodeMap: list, nodeSep: float, direction: str):
    foundNodes = []

    if direction == "l":
        dirEffect = -1
    else:
        dirEffect = 1
    
    u = abs(jumpForce)
    a = -abs(gravityAccel)

    currentT = 0
    step = 0.1 #t step
    topNodes = []
    currentNode = startingNode
    currentNodeData = ""

    #travelling across curve
    while currentNodeData == "" and currentNode[0] in range(0, len(nodeMap)) and currentNode[1] in range(0, len(nodeMap[0])):
        currentT += step
        xDisplacement = (dirEffect * abs(maxSpeed[1]) * currentT) 
        yDisplacement = dirEffect * ((u * currentT) + (0.5 * a * currentT**2))
        x = startingNode[1] * nodeSep + xDisplacement
        y = startingNode[0] * nodeSep + yDisplacement
        currentNode = getNearestNode(absolute=(y, x), nodeSep=nodeSep, nodeMap=nodeMap, ignoreRounding=True)
        currentNodeData = nodeMap[currentNode[0]][currentNode[1]]
        if currentNodeData == "" and not currentNode in topNodes:
            topNodes.append(currentNode)
    
    while len(topNodes) != 0:
        nodeBuffer = []
        constTopNodes = []
        currentIndex = 0
        for node in topNodes:
            constTopNodes.append(node)
            nodeBuffer.append([])
            nodeBuffer[currentIndex] = getLowerNodes(start=node, nodeMap=nodeMap, exclusionList=foundNodes)
            foundNodes += nodeBuffer[currentIndex]
            currentIndex += 1

        topNodes = []
        '''
        idea: since this recursion could be problematic for large falls
        (i.e. a 1-1 relationship between x and y movement could cause too much of the graph to be added to foundNodes)
        we could just change the ratio to like 1-3 or 1-4 to limit how fast the graph expands horizontally
        '''

        excludeCoordinates = [] #janky workaround to not adding repeat coordinates to topNodes D:

        for columnIndex in range(0, len(nodeBuffer)-1):
            for node in nodeBuffer[columnIndex]:
                if not node in constTopNodes:
                    leftNode = (node[1], node[0]-1)
                    rightNode = (node[1], node[0]+1)

                    if not leftNode[1] in excludeCoordinates and nodeMap[leftNode[0]][leftNode[1]] == "" and nodeMap[leftNode[0] - 2][leftNode[1]] == "" and not leftNode in foundNodes: #remember, + is down and - is up in pygame
                        topNodes.append(leftNode)
                        excludeCoordinates.append(leftNode[1])
                    elif nodeMap[leftNode[0]][leftNode[1]] != "" and leftNode[1] in excludeCoordinates:
                        excludeCoordinates.remove(leftNode[1])
                    
                    if not rightNode[1] in excludeCoordinates and nodeMap[rightNode[0]][rightNode[1]] == "" and nodeMap[rightNode[0] - 2][rightNode[1]] == "" and not rightNode in foundNodes: #remember, + is down and - is up in pygame
                        topNodes.append(rightNode)
                        excludeCoordinates.append(rightNode[1])
                    elif nodeMap[rightNode[0]][rightNode[1]] != "" and rightNode[1] in excludeCoordinates:
                        excludeCoordinates.remove(rightNode[1])
    
    return foundNodes #<= no way im done :O