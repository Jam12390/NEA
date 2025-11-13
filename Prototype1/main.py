import pygame
import sys
from EntitySubclasses import Player
from OtherClasses import WallObj, Item, ItemUIWindow
from button import Button
from dictionaries import *

screenWidth = 800
screenHeight = screenWidth*0.8 #keep the ratio for w-h at 1:0.8 - could change later

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((screenWidth, screenHeight))
clock = pygame.time.Clock()
paused = False

FPS = 60

#player = pygame.sprite.GroupSingle()
player = Player(
    FPS=FPS,
    jumpForce=75, #pixels/second
    maxHP=100,
    defense=5,
    speed=1,
    pAttackCooldown=0.75,
    pSize=pygame.math.Vector2(50, 50),
    spritePath="Sprites/DefaultSprite.png", #path to the player's sprite goes here
    pTag="player",
    pMass=5,
    startingPosition=pygame.math.Vector2(screenWidth/2, screenHeight/2),
    startingVelocity=pygame.math.Vector2(0, 0),
    pVelocityCap=pygame.math.Vector2(50, 50),
    startingWeaponID=0
)

walls = pygame.sprite.Group()
walls.add(
    WallObj(
        size=pygame.Vector2(500, 100),
        position=pygame.Vector2(screenWidth/2, (screenHeight/2)+200), #position the floor beneath the player
        spritePath="Sprites/DefaultSprite.png", #placeholder for actual image path in development
        pTag="floor",
        frictionCoef=1
    )
)

items = pygame.sprite.Group()
items.add(
    Item(
        pID=0,
        startingPosition=pygame.Vector2(screenWidth/2 + 150, (screenHeight/2)+175),
        UIWindow=ItemUIWindow(
            itemID=0,
            replaces=allItems[0]["replaces"],
            pos=(screenWidth/2 + 150, (screenHeight/2) + 50),
            size=(400, 150)
        ),
    )
)
items.add(
    Item(
        pID=1,
        startingPosition=pygame.Vector2(screenWidth/2 - 150, (screenHeight/2)+175),
        UIWindow=ItemUIWindow(
            itemID=1,
            replaces=allItems[1]["replaces"],
            pos=(screenWidth/2 - 150, (screenHeight/2) + 50),
            size=(400, 150)
        )
    )
)

mainLoopRunning = True

inventoryOpen = False

def mainloop():
    global inventoryOpen
    global paused
    pygame.display.set_caption("Main loop")

    while mainLoopRunning:
        clock.tick(FPS)

        events = pygame.event.get()

        for event in events:
            '''
            KEYDOWN is for events which should only happen once if the key is pressed.
            i.e. I is likely to be held for 2-3 frames. If KEYDOWN wasn't used, the inventory screen would open and close rapidly.
            '''
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    for item in items:
                        if item.UIWindow.shown: #if the UI is shown, the item is in pickup range
                            item.pickup(target=player)
                if event.key == pygame.K_i:
                    inventoryOpen = True
                    paused = True
                    inventory()
                if event.key == pygame.K_ESCAPE and not inventoryOpen:
                    paused = True
                    pauseMenu()
                if event.key == pygame.K_SPACE and ("l" in player.blockedMotion or "r" in player.blockedMotion) and not player.isGrounded:
                    player.wallJump()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not player.weapon.currentlyAttacking:
                    player.weapon.attack(parent=player)

            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()

        if not paused:
            #cycle through all potential movement inputs
            if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and player.isGrounded and not "u" in player.blockedMotion:
                player.jump()

            if keys[pygame.K_a] and not player.containsForce(axis="x", ref="UserInputLeft") and not "l" in player.blockedMotion and not player.crouched:
                player.addForce(axis="x", direction="l", ref="UserInputLeft", magnitude=2500)
            elif not keys[pygame.K_a]:
                player.removeForce(axis="x", ref="UserInputLeft")

            if keys[pygame.K_d] and not player.containsForce(axis="x", ref="UserInputRight") and not "r" in player.blockedMotion and not player.crouched:
                player.addForce(axis="x", direction="r", ref="UserInputRight", magnitude=2500)
            elif not keys[pygame.K_d]:
                player.removeForce(axis="x", ref="UserInputRight")

            if keys[pygame.K_s]:
                if not player.containsForce(axis="y", ref="UserInputDown") and not player.isGrounded:
                    player.fastFalling = True #start fast falling
                    player.addForce(axis="y", direction="d", ref="UserInputDown", magnitude=2500)
                    player.modifySpeedCap(axis="y", magnitude=15)
                elif player.isGrounded:
                    if player.fastFalling: #are we fast falling
                        player.fastFalling = False #stop fast falling
                        player.modifySpeedCap(axis="y", magnitude=-15) #change speed cap back
                    player.removeForce(axis="y", ref="UserInputDown")
                    if not player.crouched: #if we're not crouched
                        player.crouch() #crouch
                elif not player.isGrounded:
                    if player.crouched: #if we're crouched
                        player.uncrouch() #uncrouch
            else: #not holding S
                player.removeForce(axis="y", ref="UserInputDown") #remove downwards force
                if player.crouched:
                    player.uncrouch()
                if player.fastFalling:
                    player.modifySpeedCap(axis="y", magnitude=-15) #stop fast falling
                    player.fastFalling = False

            if keys[pygame.K_q]: #debug code, resets the player position to center
                player.rect.center = (round(screenWidth/2), round(screenHeight/2))
                player._velocity = pygame.Vector2(0,0)

            screen.fill((0, 0, 0)) #rgb value for black background

            #update all objects (this includes collision detection)
            player.update(collidableObjects=[walls, items])

            #print(player._xForces, player._yForces)
            print(player._velocity)

            walls.update()
            items.update()
            redraw()
            pygame.display.flip()

def redraw(): #it's important to note that redraw() DOES NOT update() any of the objects it's drawing
    screen.blit(player.image, player.rect)

    if player.weapon.currentlyAttacking:
        screen.blit(player.weapon.image, player.weapon.rect)

    for sprite in walls:
        screen.blit(sprite.image, sprite.rect)
    walls.draw(screen)
    
    for item in items:
        if item.UIWindow.shown:
            item.UIWindow.update()
            screen.blit(item.UIWindow.surface, item.UIWindow.rect)
    items.draw(screen)

def inventory():
    global inventoryOpen
    global paused
    font = pygame.font.SysFont("Calibri", 20)
    title = font.render("Inventory", False, (255, 255, 255))
    itemHeaders = [
        [
            font.render(f"{allItems[ID]["name"]} - ", False, (255, 255, 255)),
            font.render(f"Effects: {allItems[ID]["effects"]}", False, (255, 255, 255))
        ]
        for ID in player.inventory.keys() #makes separate lists for each item's name and headers in inventory
    ]
    itemDescriptions = [font.render(item[1], False, (255, 255, 255)) for item in player.inventory.values()]
    while inventoryOpen:
        startingPos = [10, 50]
        #clock.tick(FPS) #note for future prototypes: ticking the clock twice imitates slow motion (at the cost of FPS ofc)
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0,0,0))
        dim.set_alpha(200)
        screen.blit(dim, (0,0))
        
        background = pygame.Surface((screenWidth-100, screenHeight-100))
        background.fill((0, 0, 125))

        background.blit(title, (10,10))
        for itemIndex in range(0, len(itemHeaders)):
            background.blit(itemHeaders[itemIndex][0], (startingPos[0], startingPos[1])) #itemHeaders[itemIndex] = [itemName, itemEffects]
            background.blit(itemHeaders[itemIndex][1], (startingPos[0] + pygame.Surface.get_rect(itemHeaders[itemIndex][0]).right, startingPos[1]))
            startingPos[1] += 25
            background.blit(itemDescriptions[itemIndex], (startingPos[0], startingPos[1])) #itemDescriptions
            startingPos[1] += 50

        screen.blit(background, (25, 50))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    inventoryOpen = False
                    paused = False
        pygame.display.flip()

def pauseMenu():
    global paused
    pauseText = pygame.font.SysFont("Calibri", 90).render("Paused", False, (255, 255, 255))

    buttonText = ["Resume", "Abandon Run", "Options", "Exit to Desktop"]
    renderedText = []
    functions = [unpause, abandonRun, openOptions, quit]

    startingPos = pygame.Vector2(125, screenHeight - (75*4) + 25)
    for index in range(0, len(buttonText)):
        renderedText.append(Button(
            position=startingPos,
            text=buttonText[index],
            func=functions[index],
            textSize=25,
            size=pygame.Vector2(200, 50)
        ))
        startingPos.y += renderedText[0].size.y + 25
    
    while paused:
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0,0,0))
        dim.set_alpha(200)
        screen.blit(dim, (0,0))

        screen.blit(pauseText, (25, 25))

        mousePos = pygame.mouse.get_pos()

        for button in renderedText:
            button.update(mousePos)
            screen.blit(button.surface, button.rect)
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                unpause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in renderedText:
                    if button.hoveredOver:
                        button.onClick()
        pygame.display.flip()

def unpause():
    global paused
    paused = False

def abandonRun():
    global paused
    paused = False
    player.rect.center = (round(screenWidth/2), round(screenHeight/2))
    player._velocity = pygame.Vector2(0,0)

def openOptions():
    pass

def quit():
    pygame.quit()
    sys.exit()

mainloop()