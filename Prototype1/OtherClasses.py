import pygame
from pygame.sprite import _Group
from dictionaries import allItems, allWeapons
from main import FPS, screen, playerGroup

class Weapon(pygame.sprite.Sprite):
    def __init__(self, pID: int, startingPosition: pygame.Vector2):
        super().__init__()
        self.ID = pID
        self.__replaces = allWeapons[pID]["replaces"]
        self.image = pygame.transform.smoothscale(pygame.image.load(allWeapons[pID]["imgPath"]), (100, 100))
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (round(startingPosition.x), round(startingPosition.y))
        self.damage = allWeapons[pID]["damage"]
        self.currentlyAttacking = False
        self.__attackTimer = 0
        self.__anim = {} #placeholder for anim dictionary
    
    def playAnim(self):
        pass

    def attack(self, parent):
        if parent.simulated and self.__attackTimer <= 0: #the instance of object will be whichever entity has the weapon (e.g. Player.simulated)
            self.currentlyAttacking = True
            self.__attackTimer = self.__anim["time"] #treating __anim as a map here since it's the easiest to read and understand
            self.playAnim()
    
    def update(self):
        self.__attackTimer -= 1/FPS
        if self.__attackTimer <= 0:
            self.currentlyAttacking = False
    
    def killSelf(self):
        self.kill()

class WallObj(pygame.sprite.Sprite):
    def __init__(
            self,
            size: pygame.Vector2,
            position: pygame.Vector2,
            spritePath: str,
            pTag: str = "wall"
        ):
        super().__init__()
        self.image = pygame.transform.smoothscale(pygame.image.load(spritePath), (round(size.x), round(size.y)))
        self.tag = pTag
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (round(position.x), round(position.y))
    
    def killSelf(self):
        self.kill()
    
    def update(self):
        screen.blit(self.image, self.rect)

class Item(pygame.sprite.Sprite):
    def __init__(
            self,
            pID: int,
            startingPosition: pygame.Vector2
        ):
        self.ID = pID
        self.__replaces = allItems[pID]["replaces"]
        self.image = pygame.transform.smoothscale(pygame.image.load(allItems[pID]["imgPath"]), (100, 100))
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (round(startingPosition.x), round(startingPosition.y))
    
    def pickup(self):
        playerGroup.sprite.pickupItem(ID=self.ID, replaces=self.__replaces)
        self.killSelf()
    
    def swapItem(self, newID: int):
        self.ID = newID
        if self.__replaces == "weapon":
            self.__replaces = "weapon"
            self.image = pygame.transform.smoothscale(pygame.image.load(allWeapons[newID]["imgPath"]), (100, 100))
        else:
            self.__replaces = allItems[newID]["replaces"]
            self.image = pygame.transform.smoothscale(pygame.image.load(allItems[newID]["imgPath"]), (100, 100))
        screen.blit(self.image, self.rect) #ensure screen updates
    
    def killSelf(self):
        self.kill()