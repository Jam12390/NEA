import pygame
from Entity import Entity
from OtherClasses import Weapon
from dictionaries import allItems

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
        self.weapon = Weapon(FPS=FPS, pID=startingWeaponID, startingPosition=pygame.Vector2(round(self.rect.centerx + self.__offset.x), round(self.rect.centery + self.__offset.y))) #TODO: change once default weapon implemented
    
    def pickupItem(self, ID: int, replaces: str):
        newData = None
        if replaces == "weapon":
            newData = self.weapon.ID
            self.weapon.killSelf() #destroy the current weapon
            self.weapon = Weapon(FPS=self.FPS, pID=ID, startingPosition=pygame.Vector2(round(self.rect.centerx + self.__offset.x), round(self.rect.centery + self.__offset.y))) #and replace it with a new instance of the picked up weapon
        
        elif replaces.isdigit(): #if replaces is an ID (defaults to item)
            if ID in self.inventory.keys(): #presence check for item to replace
                newData = ID
                self.inventory.pop(ID) #delete it
            self.inventory[ID] = ["item", allItems[ID]["details"], 1] #add the new item to the inventory
        
        elif ID in self.inventory.keys(): #if there is nothing to replace and the item is in the inventory
            self.inventory[ID][2] += 1 #increment the quantity of said item
        
        else: #otherwise
            self.inventory[ID] = ["item", allItems[ID]["details"], 1] #add the item normally
        return newData
    
    def _recalculateAttributes(self):
        self._maxHP = self._originalAttributes["maxHP"]
        self._defense = self._originalAttributes["defense"]
        self._speed = self._originalAttributes["speed"]
        self.attackCooldown = self._originalAttributes["attackCooldown"]

        for value in self.inventory.values(): #value is in format [tag: string, details: string]
            if value[0] == "item":
                splitValue = value[1].split(", ")
                splitEffects = [item.split(" ") for item in splitValue] #double split to cover effects which affect multiple attributes
                for effect in splitEffects: #effect is now in format [variableAffected: string, operator: string, operand: float]
                    for i in range(value[2]):
                        self.modifyStat(effect[0], effect[1], effect[2])

        effectValues = [value for value in self._effects.values()]

        for index in range(0, len(effectValues)):
            splitValue = effectValues[index].split(", ") #double split to cover effects which affect multiple attributes
            splitEffects = [item.split(" ") for item in splitValue]
            for effect in splitEffects:
                self.modifyStat(effect[0], effect[1], effect[2])
            
        self._velocityCap *= self._speed #increase speed cap by a factor of _speed
    
    def update(self, collidableObjects):
        for key in self._effects.keys():
            self._effects[key][1] -= 1/self.FPS #FPS is a global variable denoting the number of game updates per second - 1/FPS is the time since last frame
            if self._effects[key][1] <= 0:
                self.removeEffect(ID=int(key.split("-")[0]), instance=key.split("-")[1], forced=False)

        if self.simulated:
            self._recalculateAttributes()

            self.recalculateResultantForce()
            self._acceleration = self.getAcceleration(accelerationMultiplier=self._speed)
            directionChanged = self.getVelocity()
            displacement = self.displaceObject(collidableObjects=collidableObjects)
            self.weapon.rect.center = (round(self.weapon.rect.centerx + displacement[0]), self.weapon.rect.centery)
            if directionChanged:
                self.weapon.image = pygame.transform.flip(self.image, True, False) #flip the weapon sprite on the x axis
                if self._velocity.x < 0: #right -> left
                   self.weapon.rect.center = (round(self.weapon.rect.centerx - (self.__offset.x * 2)), self.weapon.rect.centery) #move the weapon center left by 2*offset to swap the side it's attached to
                else: #left -> right
                    self.weapon.rect.center = (round(self.weapon.rect.centerx + (self.__offset.x * 2)), self.weapon.rect.centery)

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())
