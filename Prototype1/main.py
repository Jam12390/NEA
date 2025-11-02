import pygame
from PhysicsObject import *
from Entity import *
from EntitySubclasses import *
from OtherClasses import *

FPS = 60

screenWidth = 800
screenHeight = screenWidth*0.8 #keep the ratio for w-h at 1:0.8 - could change later

pygame.init()

screen = pygame.display.set_mode((screenWidth, screenHeight))
clock = pygame.time.Clock()
paused = False

player = Player(
    offset=pygame.math.Vector2(25, 0),
    jumpForce=50, #pixels/second
    maxHP=100,
    defense=5,
    speed=1,
    pAttackCooldown=0.75,
    pSize=pygame.math.Vector2(50, 50),
    spritePath="\\...", #path to the player's sprite goes here
    pTag="player",
    pMass=5,
    startingPosition=pygame.math.Vector2(screenWidth/2, screenHeight/2),
    startingVelocity=pygame.math.Vector2(0, 0),
    pVelocityCap=pygame.math.Vector2(25, 25)
)