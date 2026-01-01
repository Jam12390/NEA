import math

def s(u, g, t) -> float:
    return u*t + 0.5*g*t**2

def v(u, g, t) -> float:
    return u + g*t

def solveS(u, g, point, direction) -> float:
    #equ = 0 = ut + 0.5at^2 - point
    solutions = [
        (-u + math.sqrt(u**2 - 2*g*-point))/(2*g),
        (-u - math.sqrt(u**2 - 2*g*-point))/(2*g)
    ] #solutions to point

    if direction == "l":
        t = min(solutions)
    else:
        t = max(solutions)
    return t

def nearestNode(absolute, nodeSep):
    yCo = absolute[0]//nodeSep
    #if s(u=u, g=g, t=solveS(u=u, g=g, point=absolute[0], direction=direction)) > yCo:
    #    yCo += 1

    return (int(yCo), int(absolute[1]//nodeSep))

def getPointsAcrossCurve(u, g, maxXSpeed, nodeSep, direction, dirEffect):
    numOfPoints = round(10 * (maxXSpeed/20))
    points = []

    solutions = [solveS(u, g/2, point=0, direction="l"), solveS(u, g/2, point=0, direction="r")]
    if direction == "l":
        solutions[1] = abs(solutions[1])
    else:
        solutions[0] = abs(solutions[0])
    tStep = dirEffect * (solutions[1] - solutions[0])/numOfPoints
    t = 0

    for x in range(numOfPoints + 1):
        points.append(nearestNode(absolute=(s(u, g, t), maxXSpeed * t), nodeSep=nodeSep))
        t += tStep
    
    buffer = []
    for point in points:
        if point not in buffer:
            buffer.append(point)
    
    return buffer

def jumpOffEdge(u, g, maxXSpeed, origin, nodeMap, nodeSep, direction):
    if direction == "l":
        dirEffect = -1
    else:
        dirEffect = 1

    u = dirEffect * abs(u)
    g = -abs(g)

    points = getPointsAcrossCurve(u, g, maxXSpeed, nodeSep, direction, dirEffect)

    topNodes = []

    hitRoof = False
    hitWall = False
    roofNode = (0,0)
    for pointIndex in range(0, len(points)):
        points[pointIndex] = (origin[0] - points[pointIndex][0], points[pointIndex][1] + origin[1])
    for point in points:
        if not hitRoof and not hitWall:
            currentNodeData = nodeMap[point[0]][point[1]]
            if currentNodeData != " " and nodeMap[point[0] + 1][point[1]] == " " and v(u=u, g=g, t=solveS(u=u, g=g, point=point[0], direction=direction)) > 0:
                hitRoof = True
                roofNode = (point[0] + 1, point[1])
                topNodes.append((point[0] + 1, point[1]))
            elif currentNodeData != " " and (((nodeMap[point[0] + 1][point[1]] == " " and nodeMap[point[0] - 1][point[1]]) == " " and (nodeMap[point[0]][point[1]] != " " or nodeMap[point[0]][point[1]] != " ")) or nodeMap[point[0] + 1][point[1]] != " " or nodeMap[point[0] - 1][point[1]] != " "):
                hitWall = True
            elif not point in topNodes:
                topNodes.append(point)
    
    if hitRoof:
        u *= -1
        index = points.index((roofNode[0] - 1, roofNode[1]))
        buffer = []
        while index >= 0:
            if index == points.index((roofNode[0] - 1, roofNode[1])):
                buffer.append((points[index][0] + 1, points[index][1]))
            else:
                buffer.append(points[index])
            index -= 1
        points = list(tuple(buffer))
        for point in points:
            yDiff = abs(roofNode[0] - point[0])
            xDiff = dirEffect * abs(roofNode[1] - point[1])
            newPoint = (roofNode[0] + yDiff, roofNode[1] + xDiff)
            if not newPoint in topNodes:
                topNodes.append(newPoint)
            
    ##Finished topnode stuff

    return topNodes

def findLowerNodes(topNodes, nodeMap) -> tuple[list[tuple], list[tuple]]:
    foundNodes = []
    floorNodes = []

    while len(topNodes) != 0:
        buffer = []
        for node in topNodes:
            currentNode = [node[0] + 1, node[1]]
            end = currentNode in topNodes or currentNode in foundNodes
            if not end:
                currentNodeData = nodeMap[currentNode[0]][currentNode[1]]
                while currentNodeData == " " and currentNode[0] in range(0, len(nodeMap)) and currentNode[1] in range(0, len(nodeMap[0])):
                    if not currentNode in foundNodes:
                        foundNodes.append((currentNode[0], currentNode[1]))
                        if node[0] - currentNode[0] % 2 == 0:
                            if currentNode[1] - 1 >= 0:
                                if nodeMap[currentNode[0]][currentNode[1] - 1] == " " and not (nodeMap[currentNode[0]][currentNode[1] - 1] in foundNodes or nodeMap[currentNode[0]][currentNode[1] - 1] in topNodes):
                                    buffer.append((currentNode[0], currentNode[1] - 1))
                            if currentNode[1] + 1 <= len(nodeMap[currentNode[0]]):
                                if nodeMap[currentNode[0]][currentNode[1] + 1] == " " and not (nodeMap[currentNode[0]][currentNode[1] + 1] in foundNodes or nodeMap[currentNode[0]][currentNode[1] + 1] in topNodes):
                                    buffer.append((currentNode[0], currentNode[1] + 1))
                    currentNode[0] += 1
                    currentNodeData = nodeMap[currentNode[0]][currentNode[1]]
                currentNode[0] -= 1
                if not tuple(currentNode) == node:
                    floorNodes.append((currentNode[0], currentNode[1]))
        topNodes = list(tuple(buffer))
    
    return (foundNodes, floorNodes)

def traverseFloor(nodeMap, jumpForce, nodeSep, origin):
    step = 1
    current = list(origin)
    foundNodes = []
    corners = []
    for x in range(2):
        stop = False
        while current[0] in range(0, len(nodeMap)) and current[1] in range(0, len(nodeMap[0])) and not stop:
            if nodeMap[current[0] + 1][current[1]] == " ":
                stop = True
                corners.append(tuple(current))
            else:
                foundNodes.append((current[0], current[1], "ground"))
                stepUp = 1
                while

if __name__ == "__main__":
    testGraph = []

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
    
    origin = (8,10)
    jumpForce = 125

    gravityAccel = 9.81 * 15
    maxSpeed = (0, 90)
    nodeSep = 13

    topNodes = jumpOffEdge(u=jumpForce, g=gravityAccel, maxXSpeed=maxSpeed[1], origin=origin, nodeMap=testGraph, nodeSep=nodeSep, direction="l")
    response = findLowerNodes(topNodes=topNodes, nodeMap=testGraph)
    for x in topNodes:
        testGraph[x[0]][x[1]] = "x"
    for x in response[0]:
        testGraph[x[0]][x[1]] = "x"
    for line in testGraph:
        print(line)