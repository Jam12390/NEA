import pygame

pygame.init()

class GridLine(pygame.sprite.Sprite):
    def __init__(self, SIZE: tuple[int, int], pos: tuple[int, int]) -> None:
        super().__init__(*groups)
        self.image = pygame.transform.smoothscale(pygame.image.load("Sprites/DefaultSprite.png"), round(SIZE[0]), round(SIZE[1]))
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (pos[0], pos[1])
    

def initGrid(gDim: tuple[int, int], SPACING: list[int], lineThickness: int, screenDim: tuple[int, int]) -> tuple[list[pygame.sprite.Group], list[list[str]]]:
    GRID = [
        pygame.sprite.Group(),
        pygame.sprite.Group()
    ]
    for x in range(1, gDim[0]):
        GRID[0].add( #vertical lines
            GridLine(
                SIZE=(lineThickness, S_HEIGHT),
                pos=(SPACING[0] * x, 0)
            )
        )
    for x in range(1, gDim[1]):
        GRID[1].add(
            GridLine(
                SIZE=(S_WIDTH, lineThickness),
                pos=(0, SPACING[1] * x)
            )
        )
    gridState = []
    for rowNumber in range(0, gDim[1]):
        gridState.append(" " for x in range(gDim[0]))
    return (GRID, gridState)

def getNearestNode(gDim: tuple[int, int], offSet: tuple[int, int], mousePos: tuple[int, int]) -> tuple[int, int]:
    x = round(mousePos[0] / gDim[0])
    y = round(mousePos[1] / gDim[1])
    return (x, y)

GRID_WIDTH = 10
GRID_HEIGHT = 10
LINE_THICKNESS = 5
highlightedObjects = dict[tuple[int, int], pygame.draw.rect]({})

S_WIDTH = 500
S_HEIGHT = 500

SCREEN = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60

SPACING = [
    (S_WIDTH - LINE_THICKNESS * GRID_WIDTH) // GRID_WIDTH,
    (S_HEIGHT - LINE_THICKNESS * GRID_HEIGHT) // GRID_HEIGHT
]

response = initGrid(
    gDim=(GRID_WIDTH, GRID_HEIGHT),
    SPACING=SPACING,
    lineThickness=LINE_THICKNESS,
    screenDim=(S_WIDTH, S_HEIGHT)
)
GRID = response[0]
gridState = response[1]

def main():
    pygame.display.set_caption("Map Editor")

    recentlyUpdatedCoords = []

    running = True

    m1State = False
    previousM1State = False

    while running:
        CLOCK.tick(FPS)

        events = pygame.event.get()
        mousePos = pygame.mouse.get_pos()
        mousePressed = pygame.mouse.get_pressed()[0]

        if mousePressed:
            nearestNode = getNearestNode(
                gDim=(GRID_WIDTH, GRID_HEIGHT),
                mousePos=mousePos
            )
            if not nearestNode in recentlyUpdatedCoords:
                recentlyUpdatedCoords.append(nearestNode)
                if nearestNode in highlightedObjects.keys:
                    highlightedObjects.pop(nearestNode)
                else:
                    highlightedObjects[nearestNode] = pygame.draw.rect(
                        surface=SCREEN,
                        color=(255, 255, 255),
                        rect=(SPACING[0] * nearestNode[0], SPACING[1] * nearestNode[1], SPACING[0], SPACING[1])
                    )
        else:
            recentlyUpdatedCoords = []
        
main()