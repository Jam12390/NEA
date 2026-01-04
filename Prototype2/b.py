import math
from suvat import *
from a import precompileGraph, getTestGraph
import time

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

def getHeuristic(start, end):
    return math.sqrt( (start[0]-end[0])**2 + (start[1]-end[1])**2)

def getAdjacentNodes(graph, node):
    presence = [
        ((node.coord[0], node.coord[1] - 1) in graph, (node.coord[0], node.coord[1] - 1)),
        ((node.coord[0], node.coord[1] + 1) in graph, (node.coord[0], node.coord[1] + 1)),
        ((node.coord[0] - 1, node.coord[1]) in graph, (node.coord[0] - 1, node.coord[1])),
        ((node.coord[0] + 1, node.coord[1]) in graph, (node.coord[0] + 1, node.coord[1]))
    ]
    valid = []
    for node in presence:
        if node[0]:
            valid.append(node[1])
    return valid

def getNextNodeToVisit(nodes: list[TopDownNode]):
    nodes.sort(key=lambda node: node.shortestDistance + node.heuristic)
    index = 0
    while nodes[index].visited:
        index += 1
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


def getTopDownPath(graph, start, end):
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
        currentNode = nodes[currentNodeIndex]
        adjacentNodes = getAdjacentNodes(graph=graph, node=currentNode)
        for node in adjacentNodes:
            index = getNodeFromCoord(nodes=nodes, coord=node)
            if index == -1:
                nodes.append(TopDownNode(
                    coord=node,
                    previousNode=currentNode,
                    end=end,
                    shortestDistance=currentNode.shortestDistance + 1
                )) #continue here with cascade updating
                nodes[currentNodeIndex].nextNodes.append(node)
            else:
                if nodes[index].shortestDistance > currentNode.shortestDistance + 1:
                    nodes[index].shortestDistance = currentNode.shortestDistance + 1
                    overriddenPreviousNodeIndex = getNodeFromCoord(nodes=nodes, coord=nodes[index].previousNode)
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

#def path(graph, waypoints, start, end, jumpForceInNodes):
#    #todo: check if end is higher than start. if so, use getTopDownPath and other shit



def main():
    testGraph = getTestGraph()

    start = (5, 0)
    end = (16, 19)

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

    path = getTopDownPath(
        graph=strippedGraph,
        start=start,
        end=end
    )

    path = flattenPath(nodeMap=testGraph, path=path)

    for x in path:
        testGraph[x[0]][x[1]] = "x"
    for line in testGraph:
        print(line)

main()