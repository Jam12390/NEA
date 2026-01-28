import pygame
import Prototype1.OtherClasses as OtherClasses
import csv

def loadMapData(
        mapName: str,
        originNode: tuple[int, int],
        tileSize: int,
        tileData: dict[int, tuple[str, float]] = {0: ("Sprites/DefaultSprite.png", 1)}, # ID: (spritePath, frictionCoef)
) -> pygame.sprite.Group:
    mapData = pygame.sprite.Group()
    with open(f"Prototype2/Pathing/Maps/{mapName}.csv", "r") as map:
        data = csv.reader(map, delimiter=" ", quotechar="|")
        segmentedData = []
        for row in data:
            segmentedData.append([x for x in row[0].split(",")])
        segmentedData.pop(0)
        map.close()

    currentNodePosition = [0, 0] #shouldn't be extended but needs to be modifiable => [y, x]
    initialOffset = tileSize / 2
    for row in segmentedData:
        currentNodePosition[1] = 0
        for column in row:
            if not int(column) == -1: #if tile not empty
                try:
                    sprite = tileData[column][0]
                    frictionCoef = tileData[column][1]
                except:
                    sprite = tileData[0][0]
                    frictionCoef = tileData[0][1]
                mapData.add(OtherClasses.WallObj(
                    size= pygame.Vector2(tileSize, tileSize),
                    position= pygame.Vector2(
                        x=initialOffset + (currentNodePosition[1] * tileSize),
                        y=initialOffset + (currentNodePosition[0] * tileSize)
                    ),
                    frictionCoef=frictionCoef,
                    spritePath=sprite
                ))
            currentNodePosition[1] += 1
        currentNodePosition[0] += 1
    
    originOffset = pygame.Vector2(
        x=((originNode[1] * tileSize) + initialOffset) * -1,
        y=((originNode[0] * tileSize) + initialOffset) * -1
    )
    mapData.update(offset=originOffset)

    return mapData

response = loadMapData(
    mapName="tightArea",
    originNode=(13, 18),
    tileSize=10
)
responseLs = [x for x in response]
responseLs.sort(key=lambda tile: tile.rect.centery)
for tile in responseLs:
    print(tile.rect.center)