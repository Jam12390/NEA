import suvat
from typing import Optional

class Point():
    def __init__(self, x, y, nodeMap) -> None:
        self.__x = x
        self.__y = y
        self.__nodeMap = nodeMap
        if x in range(0, len(nodeMap[0])) and y in range(0, len(nodeMap)):
            self.data = nodeMap[y][x]
        else:
            self.data = "null"
        
    def isEmpty(self) -> bool:
        if self.data == " ":
            return True
        return False
    
    def isValid(self) -> bool:
        if self.__x in range(len(self.__nodeMap[0])) and self.__y in range(0, len(self.__nodeMap)):
            return True
        return False

    def __updateData(self) -> None:
        if self.isValid():
            self.data = self.__nodeMap[self.__y][self.__x]

    def x(self) -> int:
        return self.__x
    
    def setX(self, newX: int) -> None:
        self.__x = newX
        self.__updateData()

    def y(self) -> int:
        return self.__y
    
    def setY(self, newY: int) -> None:
        self.__y = newY
        self.__updateData()
    
    def getCoord(self) -> tuple[int, int]:
        return (self.__y, self.__x)

    def setCoord(self, newX: int, newY: int) -> None:
        self.__y = newY
        self.__x = newX
        self.__updateData()


def nearestNode(
        absolute: tuple[float, float],
        nodeSep: int
) -> tuple[int, int]:
    yCo = absolute[0]//nodeSep
    return (int(yCo), int(absolute[1]//nodeSep)) 

def inList(
        query: Point,
        ls: list
) -> bool:
    if len(ls) > 0:
        for item in ls:
            if item.getCoord() == query.getCoord():
                return True
    return False

def find(
        query: Point,
        ls: list[Point]
) -> int:
    for index in range(0, len(ls)):
        if ls[index].getCoord() == query.getCoord():
            return index
    return -1

def getPointsAcrossCurve(
        u: float,
        g: float,
        maxXSpeed: float,
        origin: Point,
        nodeMap: list[list[str]],
        nodeSep: int,
        dirEffect: int
) -> list[Point]:
    numOfPoints = round(10 * maxXSpeed/10)
    points = []

    g = -abs(g)

    roots = [
        suvat.solveS(
            u=u,
            g=g,
            point=0,
            direction="l"
        ),
        suvat.solveS(
            u=u,
            g=g,
            point=0,
            direction="r"
        )
    ]
    roots.remove(0)

    endPoint = roots[0] * 2
    tStep = dirEffect * (endPoint / numOfPoints)
    t = 0

    for x in range(numOfPoints + 1): # 1 to numOfPoints inclusive
        points.append(nearestNode(
            absolute=(suvat.s(u=u, g=g, t=abs(t)), maxXSpeed * t),
            nodeSep=nodeSep,
        ))
        t += tStep
    
    uniquePoints = []
    for point in points:
        if not point in uniquePoints: #removing duplicates
            uniquePoints.append(point)
    
    for pointIndex in range(0, len(uniquePoints)):
        uniquePoints[pointIndex] = Point( #converting each unique point to a Point object
            x=origin.x() + uniquePoints[pointIndex][1], # uniquePoints[pointIndex] => [y, x]
            y=origin.y() - uniquePoints[pointIndex][0],
            nodeMap=nodeMap
        )
    
    for point in uniquePoints:
        print(point.getCoord())
    print("")
    return uniquePoints

def jumpOffEdge(
        jumpForce: float,
        gravity: float,
        maxXSpeed: float,
        origin: Point,
        nodeMap: list[list[str]],
        nodeSep: int,
        direction: str
) -> list[Point]:
    if direction == "l":
        dirEffect = -1
    else:
        dirEffect = 1
    
    parabolaPoints = list[Point](getPointsAcrossCurve(
        u=jumpForce,
        g=gravity,
        maxXSpeed=maxXSpeed,
        origin=origin,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        dirEffect=dirEffect
    ))
    topNodes = list[Point]([])

    hitRoof = False
    hitWall = False
    hitFloor = False
    roofNode = None

    for currentNode in parabolaPoints:
        if not (hitRoof or hitWall or hitFloor) and currentNode.isValid():
            upperNode = Point(
                x=currentNode.x(),
                y=currentNode.y() - 1,
                nodeMap=nodeMap
            )
            lowerNode = Point(
                x=currentNode.x(),
                y=currentNode.y() + 1,
                nodeMap=nodeMap
            )
            adjacentNode = Point(
                x=currentNode.x() + 1 * dirEffect,
                y=currentNode.y(),
                nodeMap=nodeMap
            )

            yVelocity = suvat.v(
                u=jumpForce,
                g=gravity,
                t=suvat.solveS(
                    u=jumpForce,
                    g=gravity,
                    point=currentNode.y(),
                    direction=direction
                )
            )

            if not currentNode.isEmpty() and lowerNode.isEmpty() and yVelocity >= 0:
                hitRoof = True
                roofNode = Point(
                    x=lowerNode.x(),
                    y=lowerNode.y(),
                    nodeMap=nodeMap
                )
                topNodes.append(lowerNode)
            elif not currentNode.isEmpty() and upperNode.isEmpty():
                hitFloor = True
            elif not currentNode.isEmpty() and adjacentNode.isEmpty():
                hitWall = True
            elif not currentNode in topNodes:
                topNodes.append(currentNode)
    
    if hitRoof:
        reverseAt = find(query=roofNode, ls=parabolaPoints)
        listSegment = [parabolaPoints[index] for index in range(0, reverseAt)]
        listSegment.reverse()

        for reversedPoint in listSegment:
            xDiff = dirEffect * abs(roofNode.x() - reversedPoint.x())
            yDiff = abs(roofNode.y() - reversedPoint.y())
            newPoint = Point(
                x=roofNode.x() + xDiff,
                y=roofNode.y() + yDiff,
                nodeMap=nodeMap
            )
            if not newPoint in topNodes:
                topNodes.append(newPoint)
    
    return topNodes

def getLowerNodes(
        topNodes: list[Point],
        nodeMap: list[list[str]]
) -> dict[str, list[Point]]:
    
    foundNodes = list[Point]([])
    floorNodes = list[Point]([])

    while len(topNodes) != 0:
        newTopNodes = list[Point]([])
        distanceFromTopNode = 0
        for node in topNodes:
            if not inList(query=node, ls=foundNodes):
                foundNodes.append(node)

            currentNode = Point(
                x=node.x(),
                y=node.y() + 1,
                nodeMap=nodeMap
            )
            indexes = {
                -1: 0,
                1: 1
            }
            foundNewTopNode = [False, False]
            xStep = -1
            if not (inList(query=currentNode, ls=topNodes) or inList(query=currentNode, ls=foundNodes)):
                while currentNode.isEmpty() and currentNode.isValid():
                    distanceFromTopNode += 1
                    foundNodes.append(currentNode)
                    if distanceFromTopNode / 2 >= 1:
                        for x in range(2):
                            if currentNode.x() + xStep in range(0, len(nodeMap[0])) and not foundNewTopNode[indexes[xStep]]:
                                potentialNode = Point(
                                    x=currentNode.x() + xStep,
                                    y=currentNode.y(),
                                    nodeMap=nodeMap
                                )
                                if potentialNode.isEmpty() and not inList(query=potentialNode, ls=newTopNodes):
                                    newTopNodes.append(potentialNode)
                                    foundNewTopNode[indexes[xStep]] = True
                            xStep *= 1

                    currentNode.setY(newY=currentNode.y() + 1)
                
                if not currentNode.isEmpty():
                    currentNode.setY(newY=currentNode.y() - 1)
                    floorNodes.append(currentNode)
        topNodes = list(tuple(newTopNodes))
    
    return {
        "nodes": foundNodes,
        "floorNodes": floorNodes
    }

def traverseFloor(
        nodeMap: list[list[str]],
        jumpForceInNodes: int,
        origin: Point
) -> dict[str, list]:
    step = 1
    current = Point(
        x=origin.x(),
        y=origin.y(),
        nodeMap=nodeMap
    )
    next = Point(
        x=origin.x(),
        y=origin.y(),
        nodeMap=nodeMap
    )
    nextFloor = Point(
        x=origin.x(),
        y=origin.y(),
        nodeMap=nodeMap
    )
    foundNodes = list[Point]([])
    newFloors = list[tuple[Point, str]]([])
    corners = list[tuple[Point, str]]([])

    waypoints = list[tuple[tuple[int, int], str, tuple[int, int]]]([]) # e.g. ( (1, 0), "->", (1, 4) )
    for x in range(2):
        stop = False
        next.setX(newX=next.x() + step)
        nextFloor.setCoord(
            newX=next.x(),
            newY=next.y() + 1
        )
        while current.isValid() and not stop:
            previousCollisionStates = [False, False]
            if nextFloor.isEmpty() or not next.isEmpty() or not next.isValid():
                stop = True
                if not current in corners:
                    corners.append((
                        Point(
                            x=current.x(),
                            y=current.y(),
                            nodeMap=nodeMap
                        ),
                        "l" if step == -1 else "r"
                    ))
            if current.isEmpty():
                foundNodes.append(
                    Point(
                        x=current.x(),
                        y=current.y(),
                        nodeMap=nodeMap
                    )
                )
                stepUp = 0
                while current.isValid() and current.isEmpty() and stepUp <= jumpForceInNodes:
                    leftNode = Point(
                        x=current.x() - 1,
                        y=current.y(),
                        nodeMap=nodeMap
                    )
                    rightNode = Point(
                        x=current.x() + 1,
                        y=current.y(),
                        nodeMap=nodeMap
                    )
                    if not inList(query=current, ls=foundNodes):
                        foundNodes.append(
                            Point(
                                x=current.x(),
                                y=current.y(),
                                nodeMap=nodeMap
                            )
                        )
                    currentCollisionStates = [
                        leftNode.isValid() and not leftNode.isEmpty(),
                        rightNode.isValid() and not rightNode.isEmpty()
                    ]
                    if previousCollisionStates[0] and not currentCollisionStates[0]:
                        newFloors.append(leftNode)
                        waypoints.append((
                            (current.y() + stepUp, current.x()),
                            "->",
                            (leftNode.y(), leftNode.x())
                        ))
                    if previousCollisionStates[1] and not currentCollisionStates[1]:
                        newFloors.append(rightNode)
                        waypoints.append((
                            (current.y() + stepUp, current.x()),
                            "->",
                            (rightNode.y(), rightNode.x())
                        ))
                    previousCollisionStates = list(tuple(currentCollisionStates))
                    currentCollisionStates = [False, False]
                    stepUp += 1 #keep at end
                    current.setY(newY=current.y() - 1)
            current.setCoord(newX=next.x(), newY=next.y())
            next.setX(newX=next.x() + step)
            nextFloor.setX(newX=next.x())
        step *= -1 #reverse direction
        current = Point(
            x=origin.x(),
            y=origin.y(),
            nodeMap=nodeMap
        )
        next = Point(
            x=origin.x(),
            y=origin.y(),
            nodeMap=nodeMap
        )
    
    return {
        "nodes": foundNodes, 
        "corners": corners,
        "newFloors": newFloors,
        "waypoints": waypoints
        }

def removeDuplicateWaypoints(waypoints: list):
    cleanWaypoints = []
    while len(waypoints) != 0:
        waypoint = waypoints[0]
        waypoints.pop(0)
        if (waypoint[2], "->", waypoint[0]) in waypoints:
            waypoints.remove((waypoint[2], "->", waypoint[0]))
            waypoint = (waypoint[0], "<->", waypoint[2])
        if not waypoint[0] == waypoint[2] and not waypoint in cleanWaypoints:
            cleanWaypoints.append(waypoint)
    return cleanWaypoints

def connectAdjacentWaypoints(
        waypoints: list[tuple],
        disconnectedWaypoints: list[tuple[int, int]] # (y, x) coord
) -> list[tuple]: #note: removed newWaypoints list
    waypointGroups = []
    while len(disconnectedWaypoints) != 0:
        newGroup = []
        yQuery = disconnectedWaypoints[0][0] #y coordinate of first index
        preservedWaypoints = list[tuple[int, int]]([])
        for point in disconnectedWaypoints:
            if point[0] == yQuery:
                newGroup.append(point)
            else:
                preservedWaypoints.append(point)

        disconnectedWaypoints = list(tuple(preservedWaypoints))
        
        newGroup.sort(key=lambda point: point[1]) # index 1 == x coord
        waypointGroups.append(newGroup)
    
    for group in waypointGroups:
        if not group == []:
            cornerIndexes = list[int]([0])
            for index in range(0, len(group) - 1):
                if group[index][1] == group[index + 1][1] - 1:
                    waypoints.append((group[index], "<->", group[index + 1]))
                else:
                    cornerIndexes.append(index)
            cornerIndexes.append(len(group) - 1)

            ignoreNext = False
            for cornerIndex in range(0, len(cornerIndexes) - 1):
                potentialWaypoint = (group[cornerIndexes[cornerIndex]], "<->", group[cornerIndexes[cornerIndex + 1]])
                if not potentialWaypoint in waypoints and not ignoreNext:
                    waypoints.append(potentialWaypoint)
                    ignoreNext = True
                else:
                    ignoreNext = False
    
    return removeDuplicateWaypoints(waypoints=waypoints)


def precompileGraph(
        nodeMap: list[list[str]],
        nodeSep: int,
        gravity: float,
        enemyData: dict,
        origin: tuple[int, int]
) -> dict[str, list]:
    origin = getLowerNodes(
        topNodes=[Point(
            x=origin[1],
            y=origin[0],
            nodeMap=nodeMap
        )],
        nodeMap=nodeMap
    )["floorNodes"][0]

    floors = list[Point]([origin])
    traversedFloors = list[tuple[int, int]]([])
    corners = []

    gravity = -abs(gravity)

    maxJumpHeight = suvat.s(
        u=enemyData["jumpForce"],
        g=gravity,
        t=suvat.solveV(
            targetV=0,
            u=enemyData["jumpForce"],
            g=gravity
        )
    )
    jumpHeightInNodes = maxJumpHeight // nodeSep

    allNodes = list[tuple[int, int]]([])
    waypoints = []

    while len(floors) != 0:
        print(traversedFloors)
        print([floor.getCoord() for floor in floors])
        newFloors = []
        for floor in floors:
            if not floor.getCoord() in traversedFloors:
                traversedFloors.append(floor.getCoord())
                floorData = traverseFloor(
                    nodeMap=nodeMap,
                    jumpForceInNodes=jumpHeightInNodes,
                    origin=floor
                )
                floorData["nodes"] = list[Point](floorData["nodes"])
                floorY = floor.y()
                for corner in floorData["corners"]:
                    if not corner in corners:
                        corners.append(corner)
                for node in floorData["nodes"]:
                    if node.y() == floorY and not node.getCoord() in traversedFloors:
                        traversedFloors.append(node.getCoord())
                for newFloor in floorData["newFloors"]:
                    if not newFloor.getCoord() in allNodes and not newFloor.getCoord() in traversedFloors: #traversedFloors:
                        newFloors.append(newFloor)
                for waypoint in floorData["waypoints"]:
                    if not waypoint in waypoints:
                        waypoints.append(waypoint)
                for node in floorData["nodes"]: #can be shortened but harms readability too much
                    if not node.getCoord() in allNodes:
                        allNodes.append(node.getCoord())
        
        for corner in corners: # corner => (Point, direction)
            topNodes = jumpOffEdge(
                jumpForce=enemyData["jumpForce"],
                gravity=gravity,
                maxXSpeed=enemyData["maxSpeed"][1],
                origin=corner[0],
                nodeMap=nodeMap,
                nodeSep=nodeSep,
                direction = corner[1]
            )
            indexesToRemove = list[int]([])
            for node in topNodes:
                if node.data != " ":
                    indexesToRemove.append(topNodes.index(node))
            for index in indexesToRemove:
                topNodes.pop(index)
            columnNodeData = getLowerNodes(
                topNodes=topNodes,
                nodeMap=nodeMap
            )
            for newFloor in columnNodeData["floorNodes"]:
                if not newFloor.getCoord() in traversedFloors and not (newFloor.getCoord() in allNodes or inList(query=newFloor, ls=floors)): #(newFloor.getCoord() in traversedFloors or newFloor in floors):
                    newFloors.append(newFloor)
                waypoints.append((corner[0].getCoord(), "->", newFloor.getCoord()))
            for node in columnNodeData["nodes"]:
                if not node in allNodes:
                    allNodes.append(node.getCoord())
        corners = []
        floors = list(tuple(newFloors))

    

    return {
        "nodes": allNodes,
        "waypointData": compileWaypointData(waypoints=waypoints)
    }

def queryWaypoints(
        waypoints: list[tuple],
        query: tuple[int, int]
) -> list[tuple]:
    foundWaypoints = []
    for waypoint in waypoints:
        if waypoint[0] == query or waypoint[2] == query:
            foundWaypoints.append(waypoint)
    
    return foundWaypoints

def compileWaypointData(
        waypoints: list[tuple[tuple[int, int], str, tuple[int, int]]] # e.g. [ ( (y1, x1) "<->", (y2, x2) ) ]
) -> dict[str, list]:
    waypoints = removeDuplicateWaypoints(waypoints=waypoints)

    disconnectedWaypoints = []
    for waypoint in waypoints:
        if not waypoint[0] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[0])
        if not waypoint[2] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[2])
    
    waypoints = connectAdjacentWaypoints(
        waypoints=waypoints,
        disconnectedWaypoints=disconnectedWaypoints
    )

    return {
        "waypoints": waypoints,
        "disconnectedWaypoints": disconnectedWaypoints
    }

def getTestGraph(graphID: int) -> list[list[str]]:
    testGraph = []
    match graphID:
        case 0:
            for x in range(6):
                testGraph.append([" " for x in range(20)])
            a = ["#" for x in range(9)]
            a += [" " for x in range(11)]
            testGraph.append(a)
            for x in range(10):
                testGraph.append([" " for x in range(20)])
            a = [" " for x in range(10)]
            a += ["#" for x in range(10)]
            testGraph.append(a)
            for x in range(2):
                testGraph.append([" " for x in range(20)])
            for x in range(1):
                testGraph.append(["#" for x in range(20)]) #stupid python
        case 1:
            for x in range(9):
                testGraph.append([" " for x in range(20)])
            a = ["#" for x in range(9)]
            a.extend(" " for x in range(3))
            a.extend("#" for x in range(8))
            testGraph.append(a)
            testGraph.append(["#" for x in range(20)])
        case 2:
            for x in range(8):
                testGraph.append([" " for x in range(20)])
            for x in range(2):
                a = [" " for x in range(12)]
                a.extend("#" for x in range(8))
                testGraph.append(a)
            a = ["#" for x in range(9)]
            a.extend(" " for x in range(3))
            a.extend("#" for x in range(8))
            testGraph.append(a)
            testGraph.append(["#" for x in range(20)])
    
    return testGraph


def main(graphID: int):
    testGraph = getTestGraph(graphID=graphID)

    origin = (len(testGraph) - 3, 0)

    gravityAccel = 9.81 * 15
    nodeSep = 10

    enemyData = {
        "jumpForce": 100,
        "maxSpeed": (0, 25)
    }

    response = precompileGraph(
        nodeMap=testGraph,
        nodeSep=nodeSep,
        gravity=gravityAccel,
        enemyData=enemyData,
        origin=origin
    )

    allNodes = response["nodes"]
    waypoints = response["waypointData"]["waypoints"]

    #disconnectedWaypoints = []
    #for waypoint in waypoints:
    #    if not waypoint[0] in disconnectedWaypoints:
    #        disconnectedWaypoints.append(waypoint[0])
    #    if not waypoint[2] in disconnectedWaypoints:
    #        disconnectedWaypoints.append(waypoint[2])
    #
    #waypoints = connectAdjacentWaypoints(
    #    waypoints=waypoints,
    #    disconnectedWaypoints=disconnectedWaypoints
    #)

    for x in allNodes:
        testGraph[x[0]][x[1]] = "x"
    for x in waypoints:
        testGraph[x[0][0]][x[0][1]] = "W"
        testGraph[x[2][0]][x[2][1]] = "W"
    
    for line in testGraph:
        print(line)
    for waypoint in waypoints:
        print(waypoint)
    pass

for x in range(0, 1):
    main(graphID=x)
    print("\n")