import math
from suvat import *
import time
import precompile
from typing import Optional, Union

class Stack():
    def __init__(self) -> None:
        self.__data = []
    def push(self, newData):
        self.__data.append(newData)
    def pop(self):
        data = self.__data[len(self.__data)-1]
        self.__data.pop()
        return data
    def peek(self):
        return self.__data[len(self.__data)-1]
    def isEmpty(self):
        return len(self.__data) == 0

class TopDownNode():
    def __init__(self, coord, previousNode, end, shortestDistance) -> None:
        self.coord = coord
        self.shortestDistance = shortestDistance
        self.heuristic = getHeuristic(start=coord, end=end)
        self.previousNode = previousNode
        self.nextNodes = []
        self.visited = False

def getHeuristic(start, end) -> float:
    return math.sqrt( (start[0]-end[0])**2 + (start[1]-end[1])**2)

def getAdjacentNodes(graph, node, directionalGraph: Optional[list[tuple[Union[tuple[int, int], str], ...]]]):
    if directionalGraph != None:
        useDirections = True
    else:
        useDirections = False
    adjacentNodes = []
    if useDirections and directionalGraph != None:
        #pathsContainingQuery = findPathsFromQueries(paths=directionalGraph, queries=[node.coord])
        pathsContainingQuery = precompile.queryWaypoints(waypoints=directionalGraph, query=node.coord)
        for potentialPath in pathsContainingQuery:
            if potentialPath == (node.coord, "->", potentialPath[2]) or potentialPath[1] == "<->":
                if node.coord == potentialPath[0]:
                    adjacentNodes.append(potentialPath[2])
                else:
                    adjacentNodes.append(potentialPath[0])
    else:
        presence = [ #(Exists, coord)
            ((node.coord[0], node.coord[1] - 1) in graph, (node.coord[0], node.coord[1] - 1)),
            ((node.coord[0], node.coord[1] + 1) in graph, (node.coord[0], node.coord[1] + 1)),
            ((node.coord[0] - 1, node.coord[1]) in graph, (node.coord[0] - 1, node.coord[1])),
            ((node.coord[0] + 1, node.coord[1]) in graph, (node.coord[0] + 1, node.coord[1]))
        ]
        for nodeIndex in range(0, len(presence)):
            if presence[nodeIndex][0]: #if coord exists in the graph and is reachable by an optional directionalGraph
                adjacentNodes.append(presence[nodeIndex][1]) #add coord to valid
    return adjacentNodes

def getNextNodeToVisit(nodes: list[TopDownNode]):
    nodes.sort(key=lambda node: node.shortestDistance + node.heuristic)
    index = 0
    while nodes[min(len(nodes) - 1, index)].visited and index < len(nodes):
        index += 1
    if index >= len(nodes):
        return -1
    return index

def getNodeFromCoord(nodes: list[TopDownNode], coord):
    for index, node in enumerate(nodes):
        if node.coord == coord:
            return index
        else:
            index -= 1
    return -1

def cascadeUpdate(nodes: list[TopDownNode], startNode: TopDownNode):
    for nextNode in startNode.nextNodes:
        index = getNodeFromCoord(nodes=nodes, coord=nextNode)
        nodes[index].shortestDistance = startNode.shortestDistance + 1
        nodes = cascadeUpdate(nodes=nodes, startNode=nodes[index])
    return nodes


def getTopDownPath(graph, start, end, directionalGraph: Optional[list[tuple[tuple[int, int], str, tuple[int, int]]]]): #[((y, x), "->", (y2, x2))] | None
    if directionalGraph != None:
        useDirections = True
    else:
        useDirections = False

    nodes = list[TopDownNode]([
        TopDownNode(
            coord=start,
            shortestDistance=0,
            previousNode=None,
            end=end
        )
    ])
    currentNode = nodes[0]
    path = []
    while not end in currentNode.nextNodes:
        currentNodeIndex = getNextNodeToVisit(nodes=nodes)
        if currentNodeIndex == -1:
            return []
        currentNode = nodes[currentNodeIndex]
        adjacentNodes = getAdjacentNodes(graph=graph, node=currentNode, directionalGraph=directionalGraph)
        for node in adjacentNodes:
            index = getNodeFromCoord(nodes=nodes, coord=node)
            if useDirections:
                newDistance = currentNode.shortestDistance + getHeuristic(start=currentNode.coord, end=node)
            else:
                newDistance = float(currentNode.shortestDistance + 1)
            if index == -1:
                nodes.append(TopDownNode(
                    coord=node,
                    previousNode=currentNode,
                    end=end,
                    shortestDistance=newDistance
                )) #continue here with cascade updating
                nodes[currentNodeIndex].nextNodes.append(node)
            else:
                if newDistance < nodes[index].shortestDistance:
                    nodes[index].shortestDistance = newDistance
                    overriddenPreviousNodeIndex = getNodeFromCoord(nodes=nodes, coord=nodes[index].previousNode.coord)
                    if nodes[index].coord in nodes[overriddenPreviousNodeIndex].nextNodes:
                        nodes[overriddenPreviousNodeIndex].nextNodes.remove(nodes[index].coord)
                    nodes = cascadeUpdate(nodes=nodes, startNode=nodes[index])
        nodes[currentNodeIndex].visited = True
    

    stack = Stack()
    stack.push(end)
    path.append(start)
    while currentNode.coord != start:
        stack.push(currentNode.coord)
        currentNode = nodes[getNodeFromCoord(nodes=nodes, coord=currentNode.previousNode.coord)] #I KNOW THIS IS AN ERROR, IT WONT LET ME SPECIFY THE TYPE TO REMOVE THE ERROR DDD:
    while not stack.isEmpty():
        path.append(stack.pop())
    
    return path

def flattenPath(nodeMap, path):
    flattenedPath = []
    for node in path:
        currentCo = list(node)
        while nodeMap[currentCo[0] + 1][currentCo[1]] == " ":
            currentCo[0] += 1
        flattenedPath.append(tuple(currentCo))
    return flattenedPath

def pathfind(
        graph: list[tuple[int, int]],
        nodeMap: list[list[str]],
        nodeSep: int,
        start: tuple[int, int],
        end: tuple[int, int],
        waypoints: list[tuple[tuple, str, tuple]],
        disconnectedWaypoints: list[tuple[int, int]],
        jumpForce: float,
        maxXSpeed: float,
        gravity: float
    ):
    rangeCheckSt = precompile.Point(
        x=start[1],
        y=start[0],
        nodeMap=nodeMap
    )
    rangeCheckEn = precompile.Point(
        x=end[1],
        y=end[0],
        nodeMap=nodeMap
    )
    if not (rangeCheckSt.isValid() and rangeCheckEn.isValid()):
        return []

    start = precompile.getLowerNodes(
        topNodes=[precompile.Point(
            x=start[1],
            y=start[0],
            nodeMap=nodeMap
        )],
        nodeMap=nodeMap
    )["floorNodes"][0]

    end = precompile.getLowerNodes(
        topNodes=[precompile.Point(
            x=end[1],
            y=end[0],
            nodeMap=nodeMap
        )],
        nodeMap=nodeMap
    )["floorNodes"][0]
    #end = end[len(end) - 1]

    #start = (start[0], start[1])
    #end = (end[0], end[1])

    absolutePath = getTopDownPath( #for some reason
        graph=graph,
        start=start.getCoord(),
        end=end.getCoord(),
        directionalGraph=None
    )
    if len(absolutePath) != 0:
        flattenedPath = flattenPath(nodeMap, absolutePath)
        nearestStartWaypoint = None
        nearestEndWaypoint = None
        for node in flattenedPath:
            if node in disconnectedWaypoints and nearestStartWaypoint == None:
                nearestStartWaypoint = node
                break
        flattenedPath.reverse()
        flattenedReversePath = flattenedPath
        for node in flattenedReversePath:
            if node in disconnectedWaypoints and nearestEndWaypoint == None:
                nearestEndWaypoint = node
                break
            
        waypointPath = getTopDownPath(graph=graph, start=nearestStartWaypoint, end=nearestEndWaypoint, directionalGraph=waypoints)
        finalPath = []
        if len(waypointPath) != 0:
            finalPath = getTopDownPath(graph=graph, start=start.getCoord(), end=nearestStartWaypoint, directionalGraph=None)
            for nodeIndex in range(0, len(waypointPath) - 1):
                requiresJump, intermediatePoint = waypointJump(
                    start=waypointPath[nodeIndex],
                    end=waypointPath[nodeIndex + 1],
                    nodeMap=nodeMap,
                    jumpForce=jumpForce,
                    maxXSpeed=maxXSpeed,
                    gravity=gravity,
                    nodeSep=nodeSep
                )
                if requiresJump:
                    finalPath.extend(getTopDownPath(graph=graph, start=waypointPath[nodeIndex], end=intermediatePoint.getCoord(), directionalGraph=None))
                    finalPath.extend(getTopDownPath(graph=graph, start=intermediatePoint.getCoord(), end=waypointPath[nodeIndex + 1], directionalGraph=None))
                else:
                    finalPath.extend(getTopDownPath(graph=graph, start=waypointPath[nodeIndex], end=waypointPath[nodeIndex + 1], directionalGraph=None))
            finalPath.extend(getTopDownPath(graph=graph, start=nearestEndWaypoint, end=end.getCoord(), directionalGraph=None))
        return finalPath
    else:
        return []

def waypointJump(
        start: tuple[int, int],
        end: tuple[int, int],
        nodeMap: list[list[str]],
        jumpForce: float,
        maxXSpeed: float,
        gravity: float,
        nodeSep: int
):
    start = precompile.Point(
        x=start[1],
        y=start[0],
        nodeMap=nodeMap
    )
    end = precompile.Point(
        x=end[1],
        y=end[0],
        nodeMap=nodeMap
    )
    if not (start.isValid() and end.isValid()):
        return False, None
    traversableByGround = precompile.attemptGroundTraversal(
        start=start.getCoord(),
        end=end.getCoord(),
        nodeMap=nodeMap
    )
    if traversableByGround:
        return False, None
    if abs(start.x() - end.x()) < 2:
        return False, None
    
    if start.x() < end.x():
        dirEffect = 1
    else:
        dirEffect = -1
    tempStart = precompile.Point(
        x=start.x() + dirEffect,
        y=start.y(),
        nodeMap=nodeMap
    )
    topNodes = precompile.getPointsAcrossCurve(
        u=jumpForce,
        g=gravity,
        maxXSpeed=maxXSpeed,
        origin=tempStart,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        dirEffect=dirEffect,
        solveForMax=True
    )
    topNodes[0].setY(topNodes[0].y() + dirEffect)
    currentNode = 0
    while not canFallTowardsPoint(
        target=end,
        gravity=gravity,
        maxXSpeed=maxXSpeed,
        origin=topNodes[currentNode],
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        dirEffect=dirEffect
    ):
        currentNode += 1
    return True, topNodes[currentNode]
    
def canFallTowardsPoint(
        target: precompile.Point,
        gravity: float,
        maxXSpeed: float,
        origin: precompile.Point,
        nodeMap: list[list[str]],
        nodeSep: float,
        dirEffect: int
):
    fallNodes = list[precompile.Point](precompile.getPointsAcrossCurve(
        u=0,
        g=gravity,
        origin=origin,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        maxXSpeed=maxXSpeed,
        dirEffect=dirEffect
    ))
    for node in fallNodes:
        if target.x() == node.x() and target.y() > node.y():
            return True
    return False
    

def main(
        start: tuple[int, int],
        end: tuple[int, int],
        precompiledData: dict[str, list],
        nodeMap: list[list[str]],
        nodeSep: int,
        jumpForce: float,
        maxXSpeed: float,
        gravity: float
):    

    #start = (29, 80)
    #end = (18, 38)

    graph = precompiledData["nodes"]

    waypoints = precompiledData["waypointData"]["waypoints"]
    disconnectedWaypoints = precompiledData["waypointData"]["disconnectedWaypoints"]

    path = pathfind(
        graph=graph,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        start=start,
        end=end,
        waypoints=waypoints,
        disconnectedWaypoints=list(disconnectedWaypoints),
        jumpForce=jumpForce,
        maxXSpeed=maxXSpeed,
        gravity=gravity
    )
    #print(path)

    for x in path:
        testGraph[x[0]][x[1]] = "x"
    for line in testGraph:
        print(line)
    if path == []:
        print("Invalid Path")
    print("\n")

startTestSet = [
    (29, 80),
    (14, 0),
    (18, 38),
    (18, 38)
]
endTestSet = [
    (18, 38),
    (29, 0),
    (18, 41),
    (20, 5)
]

testGraph = precompile.loadMap(fileName="Prototype2/Pathing/Maps/sideJumps.csv")

gravityAccel = 9.81 * 15
nodeSep = 10

enemyData = {
    "jumpForce": 100,
    "maxSpeed": (0, 35)
}

response = precompile.precompileGraph(
    nodeMap=testGraph,
    nodeSep=nodeSep,
    gravity=gravityAccel,
    enemyData=enemyData,
    origin=(7, 6)
)

debug = True
t = time.time()
if debug:
    main(
        start=(7, 6),
        end=(10, 6),
        precompiledData=response,
        nodeMap=testGraph,
        nodeSep=nodeSep,
        jumpForce=enemyData["jumpForce"],
        maxXSpeed=enemyData["maxSpeed"][1],
        gravity=gravityAccel
    )
else:
    for index in range(0, len(startTestSet)):
        main(
            start=startTestSet[index],
            end=endTestSet[index]
        )
        pass
e = time.time()
print(e - t)