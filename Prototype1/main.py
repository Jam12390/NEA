import pygame
import sys
from PhysicsObject import PhysicsObject
from Entity import Entity
from EntitySubclasses import Player
from OtherClasses import Weapon, WallObj, Item
from button import Button

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
    offset=pygame.math.Vector2(25, 0),
    jumpForce=50, #pixels/second
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
    pVelocityCap=pygame.math.Vector2(35, 35),
    startingWeaponID=0
)

walls = pygame.sprite.Group()
walls.add(
    WallObj(
        size=pygame.Vector2(500, 100),
        position=pygame.math.Vector2(screenWidth/2, (screenHeight/2)+250), #position the floor beneath the player
        spritePath="Sprites/DefaultSprite.png", #placeholder for actual image path in development
        pTag="floor",
        frictionCoef=1.25
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    inventoryOpen = True
                    paused = True
                    inventory()
                if event.key == pygame.K_ESCAPE and not inventoryOpen:
                    paused = True
                    pauseMenu()

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

            #if keys[pygame.K_s] and not player.fastFalling and not "d" in player.blockedMotion: #are we falling and holding S?
            #    player.fastFalling = True #fast fall
            #    player.modifySpeedCap(axis="y", magnitude=15)
            #elif not keys[pygame.K_s] and player.fastFalling: #then are we not holding S and fast falling?
            #    player.fastFalling = False #stop fast falling
            #    player.modifySpeedCap(axis="y", magnitude=-15)
            #elif keys[pygame.K_s] and player.isGrounded: #then are we holding S while grounded?
            #    player.crouched = True #crouch
            #    if player.fastFalling:
            #        player.fastFalling = False #make sure the program recognises we aren't fast falling anymore
            #        player.modifySpeedCap(axis="y", magnitude=-15)
            #    player.rect.height = round(player.rect.height/2) #make the player half as tall
            #elif (not keys[pygame.K_s] or not player.isGrounded) and player.crouched: #are we crouched while either falling or not holding S?
            #    player.crouched = False
            #    player.rect.height = player.rect.height*2

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
                    if not player.crouched:
                        player.rect.height //= 2 #make player shorter
                        player.rect.centery += player.rect.height
                        player.crouched = True #crouch
                elif not player.isGrounded:
                    if player.crouched: #if we're crouched
                        player.crouched = False #uncrouch
                        player.rect.centery -= player.rect.height #move centre to correct position
                        player.rect.height *= 2 #make player taller
            else: #not holding S
                player.removeForce(axis="y", ref="UserInputDown") #remove downwards force
                if player.crouched:
                    player.crouched = False #uncrouch
                    player.rect.centery -= player.rect.height #move centre up
                    player.rect.height *= 2 #make player taller again
                if player.fastFalling:
                    player.modifySpeedCap(axis="y", magnitude=-15) #stop fast falling
                    player.fastFalling = False

            if keys[pygame.K_q]:
                player.rect.center = (round(screenWidth/2), round(screenHeight/2))


            #print(f"xForces{player._xForces}")
            #print(f"yForces{player._yForces}")


            #update all objects (this includes collision detection)
            player.update(collidableObjects=walls)
            screen.blit(player.image, player.rect)
            walls.update()
            for sprite in walls:
                screen.blit(sprite.image, sprite.rect)

            #print(f"Pos{player.rect.center}")

            #draw groups and update display
            screen.fill((0, 0, 0)) #rgb value for black background
            #player.draw(screen)
            pygame.draw.rect(screen, (255, 0, 0), player.rect)
            walls.draw(screen)
            pygame.display.flip()

def inventory():
    global inventoryOpen
    global paused
    font = pygame.font.SysFont("Calibri", 20)
    title = font.render("Inventory", False, (255, 255, 255))
    exSubtitle = font.render("TestData", False, (255, 255, 255))
    while inventoryOpen:
        clock.tick(FPS) #cool note: ticking the clock twice imitates slow motion (at the cost of FPS ofc)
        pygame.draw.rect(screen, (255, 0, 0), player.rect)
        walls.draw(screen)

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0,0,0))
        dim.set_alpha(200)
        screen.blit(dim, (0,0))
        
        background = pygame.Surface((screenWidth-100, screenHeight-100))
        background.fill((0, 0, 125))

        background.blit(title, (10,10))
        background.blit(exSubtitle, (10, 50))

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
        pygame.draw.rect(screen, (255, 0, 0), player.rect)
        walls.draw(screen)

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