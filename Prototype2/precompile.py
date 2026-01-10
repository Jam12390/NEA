import suvat
from typing import Optional

class Point():
    def __init__(self, x, y, nodeMap) -> None:
        self.__x = x
        self.__y = y
        self.__nodeMap = nodeMap
        self.data = nodeMap[y][x]
        
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
            direction="l"
        )
    ]
    roots.remove(0)

    endPoint = roots[0]
    tStep = dirEffect * (endPoint / numOfPoints)
    t = 0

    for x in range(numOfPoints + 1): # 1 to numOfPoints inclusive
        points.append(nearestNode(
            absolute=suvat.s(u=u, g=g, t=t),
            nodeSep=nodeSep,
        ))
        t += tStep
    
    uniquePoints = []
    for point in points:
        if not point in uniquePoints: #removing duplicates
            uniquePoints.append(point)
    
    for pointIndex in uniquePoints:
        uniquePoints[pointIndex] = Point( #converting each unique point to a Point object
            x=origin.x() - uniquePoints[pointIndex][1], # uniquePoints[pointIndex] => [y, x]
            y=origin.y() - uniquePoints[pointIndex][0],
            nodeMap=nodeMap
        )
    
    return uniquePoints

def jumpOffEdge(
        jumpForce: float,
        gravity: float,
        maxXSpeed: float,
        origin: tuple[int, int],
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
        nodeSep=nodeSep,
        dirEffect=dirEffect
    ))
    topNodes = list[Point]([])

    hitRoof = False
    hitWall = False
    roofNode = Optional[Point](None)

    for currentNode in parabolaPoints:
        if not (hitRoof or hitWall) and currentNode.isValid():
            upperNode = Point(
                x=currentNode.x(),
                y=currentNode.y() - 1,
                nodeMap=nodeMap
            ),
            lowerNode = Point(
                x=currentNode.x(),
                y=currentNode.y() + 1,
                nodeMap=nodeMap
            ),
            adjacentNode = Point(
                x=currentNode.x() + 1 * dirEffect,
                y=currentNode.y(),
                nodeMap=nodeMap
            ),

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
            elif not currentNode.isEmpty() and adjacentNode.isEmpty():
                hitWall = True
            elif not currentNode in topNodes:
                topNodes.append(currentNode)
    
    if hitRoof:
        reverseAt = parabolaPoints.index(roofNode)
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
) -> tuple[list[Point], list[Point]]:
    
    foundNodes = list[Point]([])
    floorNodes = list[Point]([])

    while len(topNodes) != 0:
        newTopNodes = list[Point]([])
        distanceFromTopNode = 0
        for node in topNodes:
            if not node in foundNodes:
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
            if not (currentNode in topNodes or currentNode in foundNodes):
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
                                if potentialNode.isEmpty() and not potentialNode in newTopNodes:
                                    newTopNodes.append(potentialNode)
                                    foundNewTopNode[indexes[xStep]] = True
                            xStep *= 1

                    currentNode.setY(newY=currentNode.y() + 1)
                
                if not currentNode.isEmpty():
                    currentNode.setY(newY=currentNode.y() - 1)
                    floorNodes.append(currentNode)
        topNodes = list(tuple(newTopNodes))
    
    return (foundNodes, topNodes)

def traverseFloor(
        nodeMap: list[list[str]],
        jumpForceInNodes: int,
        origin: Point
) -> tuple[
    list[Point],
    list[tuple[Point, str]],
    list[tuple[Point, str]],
    list[tuple[tuple[int, int], str, tuple[int, int]]]
]:
    step = 1
    current = origin
    next = origin
    nextFloor = origin
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
                    corners.append((current, "l" if step == -1 else "r"))
            foundNodes.append(current)
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
                if not current in foundNodes:
                    foundNodes.append(current)

                currentCollisionStates = [
                    leftNode.isValid() and not leftNode.isEmpty(),
                    rightNode.isValid() and not rightNode.isEmpty()
                ]
                if previousCollisionStates[0] and not currentCollisionStates[0]:
                    newFloors.append(leftNode, "r")
                    waypoints.append((
                        (current.y() + stepUp, current.x()),
                        "->",
                        (leftNode.y(), leftNode.x())
                    ))
                if previousCollisionStates[1] and not currentCollisionStates[1]:
                    newFloors.append(rightNode, "l")
                    waypoints.append((
                        (current.y() + stepUp, current.x()),
                        "->",
                        (rightNode.y(), rightNode.x())
                    ))
                
                previousCollisionStates = list(tuple(currentCollisionStates))
                currentCollisionStates = [False, False]
                stepUp += 1 #keep at end
                current.setY(newY=current.y() - stepUp)
                next.setX(newX=next.x() + step)
                nextFloor.setX(newX=next.x())
        step *= -1 #reverse direction
        current = origin
        next = origin
    
    return (foundNodes, corners, newFloors, waypoints)


def precompileGraph(
        nodeMap: list[list[str]],
        nodeSep: int,
        gravity: float,
        enemyData: dict,
        origin: tuple[int, int]
):
    origin = getLowerNodes(
        topNodes=[Point(
            x=origin[1],
            y=origin[0],
            nodeMap=nodeMap
        )],
        nodeMap=nodeMap
    )[1][0]

    floors = list[Point]([origin])
    traversedFloors = []
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

    allNodes = []
    waypoints = []

    while len(floors) != 0:
        