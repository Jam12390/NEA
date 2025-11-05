import pygame
from Entity import Entity
from OtherClasses import Weapon
from dictionaries import allItems
import math

hardVCap = (-75, 75)

class Player(Entity):
    def __init__(
            self,
            FPS: int,
            offset: pygame.Vector2,
            jumpForce: float,
            maxHP: int,
            defense: int,
            speed: float, 
            pAttackCooldown: float,
            pSize: pygame.Vector2,
            spritePath: str,
            pMass: float,
            startingPosition: pygame.Vector2,
            pVelocityCap: pygame.Vector2,
            startingVelocity: pygame.Vector2 = pygame.Vector2(0,0),
            pTag: str = "None",
            startingWeaponID: int = 0
        ):
        super().__init__(
            FPS=FPS,
            jumpForce=jumpForce,
            maxHP=maxHP,
            defense=defense,
            speed=speed,
            pAttackCooldown=pAttackCooldown,
            pSize=pSize,
            spritePath=spritePath,
            pMass=pMass,
            startingPosition=startingPosition,
            pVelocityCap=pVelocityCap,
            startingVelocity=startingVelocity,
            pTag=pTag
        )
        self.inventory = {}
        self.__offset = offset
        self.fastFalling = False
        self.crouched = False
        self.weapon = Weapon(FPS=FPS, pID=startingWeaponID, startingPosition=pygame.Vector2(round(self.rect.centerx + self.__offset.x), round(self.rect.centery + self.__offset.y)))
        self.facing = "r"
        self.changeDirFrames = 0
    
    def pickupItem(self, ID: int, replaces: str):
        newData = None
        if replaces == "weapon":
            newData = self.weapon.ID
            self.weapon.killSelf() #destroy the current weapon
            self.weapon = Weapon(FPS=self.FPS, pID=ID, startingPosition=pygame.Vector2(round(self.rect.centerx + self.__offset.x), round(self.rect.centery + self.__offset.y))) #and replace it with a new instance of the picked up weapon
        
        elif replaces.isdigit(): #if replaces is an ID (defaults to item)
            if int(replaces) in self.inventory.keys(): #presence check for item to replace
                newData = int(replaces)
                self.inventory.pop(int(replaces)) #delete it
            self.inventory[ID] = ["item", allItems[ID]["description"], 1] #add the new item to the inventory
        
        elif ID in self.inventory.keys(): #if there is nothing to replace and the item is in the inventory
            self.inventory[ID][2] += 1 #increment the quantity of said item
        
        else: #otherwise
            self.inventory[ID] = ["item", allItems[ID]["description"], 1] #add the item normally
        self._recalculateAttributes()
        return newData
    
    def _recalculateAttributes(self):
        self._maxHP = self._originalAttributes["maxHP"]
        self._defense = self._originalAttributes["defense"]
        self._speed = self._originalAttributes["speed"]
        self.attackCooldown = self._originalAttributes["attackCooldown"]

        keys = [item for item in self.inventory.keys()]
        values = [value for value in self.inventory.values()]

        for index in range(0, len(keys)): #value is in format [tag: string, details: string]
            key = keys[index]
            value = values[index]
            if value[0] == "item":
                splitValue = allItems[key]["effects"].split(", ")
                splitEffects = [item.split(" ") for item in splitValue] #double split to cover effects which affect multiple attributes
                for effect in splitEffects: #effedct is now in format [variableAffected: string, operator: string, operand: float]
                    for i in range(value[2]):
                        self.modifyStat(effect[0], effect[1], float(effect[2]))

        effectValues = [value for value in self._effects.values()]

        for index in range(0, len(effectValues)):
            splitValue = effectValues[index].split(", ") #double split to cover effects which affect multiple attributes
            splitEffects = [item.split(" ") for item in splitValue]
            for effect in splitEffects:
                self.modifyStat(effect[0], effect[1], effect[2])
        
        #increase speed cap by a factor of _speed
        if self._baseVCap.x * self._speed > self._baseVCap.x:
            self._velocityCap.x = self._baseVCap.x * self._speed
        else:
            self._velocityCap.x = self._baseVCap.x
        if self._baseVCap.y * self._speed > self._baseVCap.y:
            self._velocityCap.y = self._baseVCap.y * self._speed
        else:
            self._velocityCap.y = self._baseVCap.y
        
        self._baseVCap = pygame.Vector2(35, 35)

        self._velocityCap.x = max(hardVCap[0], min(self._velocityCap.x, hardVCap[1]))
        self._velocityCap.y = max(hardVCap[0], min(self._velocityCap.y, hardVCap[1]))

    def update(self, collidableObjects):
        for key in self._effects.keys():
            self._effects[key][1] -= 1/self.FPS #FPS is a global variable denoting the number of game updates per second - 1/FPS is the time since last frame
            if self._effects[key][1] <= 0:
                self.removeEffect(ID=int(key.split("-")[0]), instance=key.split("-")[1], forced=False)

        if self.simulated:
            #self._recalculateAttributes()

            self._resultantForce = self.recalculateResultantForce(forceMult=self._speed, includedForces=["UserInputLeft", "UserInputRight", "UserInputDown"])
            self._acceleration = self.getAcceleration()
            directionChanged = self.getVelocity()
            displacement = self.displaceObject(collidableObjects=collidableObjects)

            if round(displacement.x) != 0: #if we are actually registering movement
                if self._velocity.x < 0: #then allow self.facing to change
                    self.facing = "l"
                else:
                    self.facing = "r"

            if directionChanged:
                self.weapon.image = pygame.transform.flip(self.image, True, False)
            
            if self.facing == "l":
                self.weapon.rect.right = round(self.rect.left + self.__offset.x)
            else:
                self.weapon.rect.left = self.rect.right
            
            self.weapon.rect.centery = round(self.rect.centery + self.__offset.y)
            #self.weapon.rect.center = (round(self.rect.centerx + self.__offset.x * 2 * directionEffect), round(self.rect.centery + self.__offset.y))
            self.weapon.update()

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())
