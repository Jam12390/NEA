import math
from suvat import *
from a import precompileGraph, getTestGraph, connectAdjacentWaypoints, findPathsFromQueries, findLowerNodes
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
        pathsContainingQuery = findPathsFromQueries(paths=directionalGraph, queries=[node.coord])
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

def pathfind(graph, nodeMap, start, end, waypoints, disconnectedWaypoints):
    if not (start[0] in range(0, len(nodeMap)) and start[1] in range(0, len(nodeMap[0])) and end[0] in range(0, len(nodeMap)) and end[1] in range(0, len(nodeMap[0]))):
        return []

    start = findLowerNodes(topNodes=[start], nodeMap=nodeMap)[0]
    start = start[len(start) - 1]
    end = findLowerNodes(topNodes=[end], nodeMap=nodeMap)[0]
    end = end[len(end) - 1]

    start = (start[0], start[1])
    end = (end[0], end[1])

    absolutePath = getTopDownPath( #for some reason
        graph=graph,
        start=start,
        end=end,
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
            finalPath = getTopDownPath(graph=graph, start=start, end=nearestStartWaypoint, directionalGraph=None)
            for nodeIndex in range(0, len(waypointPath) - 1):
                finalPath.extend(getTopDownPath(graph=graph, start=waypointPath[nodeIndex], end=waypointPath[nodeIndex + 1], directionalGraph=None))
            finalPath.extend(getTopDownPath(graph=graph, start=nearestEndWaypoint, end=end, directionalGraph=None))
        return finalPath
    else:
        return []


def main():
    testGraph = getTestGraph(graphID=1)

    start = (8, 0)
    end = (8, 19)

    gravityAccel = 9.81 * 15
    nodeSep = 10

    enemyData = {
        "jumpForce": 100,
        "maxSpeed": (0, 25)
    }

    response = precompileGraph(
        nodeMap=testGraph,
        nodeSep=nodeSep,
        gravityAccel=gravityAccel,
        enemyData=enemyData,
        origin=(5, 0)
    )

    graph = response[0]
    strippedGraph = []
    for node in graph:
        if not (node[0], node[1]) in strippedGraph:
            strippedGraph.append((node[0], node[1]))

    waypoints = response[1]

    disconnectedWaypoints = []
    for waypoint in waypoints:
        if not waypoint[0] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[0])
        if not waypoint[2] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[2])
    
    disconnectedWaypoints = tuple(disconnectedWaypoints)
    
    waypoints = connectAdjacentWaypoints(waypoints=waypoints, disconnectedWaypoints=list(disconnectedWaypoints))
    
    #testPath = getTopDownPath(graph=disconnectedWaypoints, start=(94, 1), end=(5, 8), directionalGraph=waypoints)

    path = pathfind(
        graph=strippedGraph,
        nodeMap=testGraph,
        start=start,
        end=end,
        waypoints=waypoints,
        disconnectedWaypoints=list(disconnectedWaypoints)
    )

    for x in path:
        testGraph[x[0]][x[1]] = "x"
    for line in testGraph:
        print(line)

main()