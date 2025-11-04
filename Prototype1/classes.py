import pygame
from dictionaries import *
import operator

operators = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv
}

def normalise(value):
    return value * (-1 if value<0 else 1) 

class PhysicsObject(pygame.sprite.Sprite):
    def __init__(
            self,
            pSize: pygame.Vector2,
            spritePath: str,
            pMass: float,
            startingPosition: pygame.Vector2,
            pVelocityCap: pygame.Vector2,
            startingVelocity: pygame.Vector2 = pygame.Vector2(0, 0),
            pTag: str = "none",
    ):
        super().__init__()
        self.size = pSize
        self.image = pygame.transform.smoothscale(pygame.image.load(spritePath), (pSize.x, pSize.y))
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (round(startingPosition.x), round(startingPosition.y))
        self.simulated = True
        self.tag = pTag
        self._mass = pMass
        self._xForces = {}
        self._yForces = {"gravity": pMass*9.81*10}
        self._resultantForce = pygame.Vector2(0,0)
        self._velocity = startingVelocity
        self._velocityCap = pVelocityCap
        self._acceleration = pygame.Vector2(0,0)
        self.blockedMotion = []
        self.isGrounded = False
    
    def recalculateResultantForce(self):
        resXForce = 0
        resYForce = 0
        for force in self._xForces.values(): #sum of horizontal forces
            resXForce += force
        for force in self._yForces.values(): #sum of vertical forces
            resYForce += force
        self._resultantForce = pygame.math.Vector2(resXForce, resYForce) #store as vector2 (easier for later operations)
        print(f"ResForce{self._resultantForce}")
    
    def getAcceleration(self, accelerationMultiplier: float = 1.0):
        print(f"Acceleration{(self._resultantForce / self._mass) * accelerationMultiplier}")
        return (self._resultantForce / self._mass) * accelerationMultiplier
    
    def getVelocity(self):
        initialVelocity = self._velocity
        velocityChanged = []

        if initialVelocity.x > self._velocityCap.x:
            xVelocity = initialVelocity.x - 0.5
            xVelocity += self._acceleration.y*(1/FPS) if self._acceleration.y <= 0 else 0
        elif initialVelocity.x < self._velocityCap.x*-1:
            xVelocity = initialVelocity.x + 0.5
            xVelocity += self._acceleration.y*(1/FPS) if self._acceleration.y >= 0 else 0
        else:
            xVelocity = self._velocity.x + self._acceleration.x*(1/FPS)
            xVelocity = max(self._velocityCap.x * -1, min(xVelocity, self._velocityCap.x)) #clamping xVelocity to _velocityCap.x
        
        if initialVelocity.y > self._velocityCap.y:
            yVelocity = initialVelocity.y - 0.5
            yVelocity += self._acceleration.y*(1/FPS) if self._acceleration.y <= 0 else 0
        elif initialVelocity.y < self._velocityCap.y*-1:
            yVelocity = initialVelocity.y + 0.5
            yVelocity += self._acceleration.y*(1/FPS) if self._acceleration.y >= 0 else 0
        else:
            yVelocity = self._velocity.y + self._acceleration.y*(1/FPS)
            yVelocity = max(self._velocityCap.y * -1, min(yVelocity, self._velocityCap.y)) #same with yVelocity

        print(f"Velocity{xVelocity, yVelocity}")
        
        if xVelocity == initialVelocity.x: #check if either velocity has changed for displaceObject() equation
            velocityChanged.append(True)
        else:
            velocityChanged.append(False)
        
        if yVelocity == initialVelocity.y:
            velocityChanged.append(True)
        else:
            velocityChanged.append(False)
        
        if (initialVelocity.x < 0 and xVelocity >= 0) or (initialVelocity.x > 0 and xVelocity <= 0): #check if the object's weapon needs to change position
            directionChanged = True
        else:
            directionChanged = False
        
        return velocityChanged, initialVelocity, pygame.math.Vector2(xVelocity, yVelocity), directionChanged

    def getVelocityValue(self):
        return self._velocity
    
    def getMass(self):
        return self._mass
    
    def displaceObject(
            self,
            velocityChanged: list,
            initialVelocity: pygame.Vector2,
            finalVelocity: pygame.Vector2,
            directionChanged: bool,
            collidableObjects
    ):
        #xDenominator = 1 if self._acceleration.x*2 == 0 else self._acceleration.x*2 #prevent /0 errors
        #yDenominator = 1 if self._acceleration.y*2 == 0 else self._acceleration.y*2

        if False:#velocityChanged[0]: #if the velocity has changed, use s = (v^2 - u^2)/(2*a)
            xDisplacement = (finalVelocity.x**2 - initialVelocity.x**2)/xDenominator
        else:
            xDisplacement = self._velocity.x*5*(1/FPS)
        
        if False:#velocityChanged[1]:
            yDisplacement = (finalVelocity.y**2 - initialVelocity.y**2)/yDenominator
        else:
            yDisplacement = self._velocity.y*5*(1/FPS) #conversion of 1m -> 5pix?
        
        print(f"Displacement{xDisplacement, yDisplacement}")

        self.renderCollisions(collidableObjects=collidableObjects, velocity=[finalVelocity.x, finalVelocity.y], displacement=pygame.Vector2(xDisplacement, yDisplacement)) #update position

        if "l" in self.blockedMotion:
            xDisplacement = 0 #don't move the object
            finalVelocity.x = 0 #assume velocity is in the same direction and therefore set it to 0
        
        if "r" in self.blockedMotion:
            xDisplacement = 0
            finalVelocity.x = 0
        
        if "d" in self.blockedMotion:
            yDisplacement = 0
            finalVelocity.y = 0
        
        if "u" in self.blockedMotion:
            yDisplacement = 0
            finalVelocity.y = 0
        
        self._velocity = finalVelocity #update velocity
        return pygame.math.Vector2(xDisplacement, yDisplacement) #for use in updating weapon position in Player subclass
    
    def renderCollisions(self, collidableObjects, velocity: list, displacement: pygame.math.Vector2):
        self.blockedMotion = []
        collidingDirections = []

        newRectx = self.rect
        newRectx.center = (round(newRectx.center[0] + displacement.x), newRectx.center[1])

        newRecty = self.rect
        newRecty.center = (newRecty.center[0], round(newRectx.center[1] + displacement.y))

        self.rect.center = (round(self.rect.centerx + displacement.x), round(self.rect.centery + displacement.y))

        for collidable in collidableObjects:
            if collidable.tag in ["wall", "floor"] and collidable.simulated: #thinking ahead for when objects are de-rendered to improve performance
                #bottom left corner
                if pygame.Rect.collidepoint(collidable.rect, self.rect.bottomleft):
                    xDiff = normalise(self.rect.left - collidable.rect.right)
                    yDiff = normalise(self.rect.bottom - collidable.rect.top)

                    if xDiff < yDiff:
                        self.rect.left = collidable.rect.right
                        collidingDirections.append("l")
                    else:
                        self.rect.bottom = collidable.rect.top
                        collidingDirections.append("d")
                        if collidable.tag == "floor":
                            self.isGrounded = True

                #top left corner
                if pygame.Rect.collidepoint(collidable.rect, self.rect.topleft):
                    xDiff = normalise(self.rect.left - collidable.rect.right)
                    yDiff = normalise(self.rect.top - collidable.rect.bottom)

                    if xDiff < yDiff:
                        self.rect.left = collidable.rect.right
                        collidingDirections.append("l")
                    else:
                        self.rect.top = collidable.rect.bottom
                        collidingDirections.append("u")
                
                #top right corner
                if pygame.Rect.collidepoint(collidable.rect, self.rect.topright):
                    xDiff = normalise(self.rect.right - collidable.rect.left)
                    yDiff = normalise(self.rect.top - collidable.rect.bottom)

                    if xDiff < yDiff:
                        self.rect.right = collidable.rect.left
                        collidingDirections.append("r")
                    else:
                        self.rect.top = collidable.rect.bottom
                        collidingDirections.append("u")
                
                #bottom right corner
                if pygame.Rect.collidepoint(collidable.rect, self.rect.bottomright):
                    xDiff = normalise(self.rect.right - collidable.rect.left)
                    yDiff = normalise(self.rect.bottom - collidable.rect.top)

                    if xDiff < yDiff:
                        self.rect.right = collidable.rect.left
                        collidingDirections.append("r")
                    else:
                        self.rect.bottom = collidable.rect.top
                        collidingDirections.append("d")
                        if collidable.tag == "floor":
                            self.isGrounded = True

                #if pygame.Rect.colliderect(collidable.rect, newRectx):
                #    if velocity[0] >= 0:
                #        collidingDirections.append("r")
                #        self.rect.right = collidable.rect.left
                #    else:
                #        collidingDirections.append("l")
                #        self.rect.left = collidable.rect.right
                #if pygame.Rect.colliderect(collidable.rect, newRecty):
                #    if velocity[1] >= 0:
                #        collidingDirections.append("u")
                #        self.rect.top = collidable.rect.bottom
                #    else:
                #        collidingDirections.append("d")
                #        self.rect.bottom = collidable.rect.top

        for direction in collidingDirections:
            if not direction in self.blockedMotion:
                self.blockedMotion.append(direction)

    def addForce(
            self,
            axis: str, #python doesn't have a char datatype, so we need data validation to ensure len(axis) = 1
            direction: str,
            ref: str,
            magnitude: float

    ):
        if len(axis) > 0:
            axis = axis[0:1] #data validation to ensure axis is 1 character
        if direction == "l" or direction == "d": #dirEffect is used to ensure magnitude follows the convention (-) = left or down, (+) = up or right
            dirEffect = -1
        else:
            dirEffect = 1
        
        if axis == "x":
            if ref in self._xForces.values(): #presence check for force reference
                self._xForces[ref] += dirEffect*magnitude #if the force exists, add magnitude to it
            else:
                self._xForces[ref] = dirEffect*magnitude #otherwise add it to the dictionary
        else:
            if ref in self._yForces.values():
                self._yForces[ref] += dirEffect*magnitude
            else:
                self._yForces[ref] = dirEffect*magnitude

    def removeForce(
            self,
            axis: str,
            ref: str
    ):
        if len(axis) > 0:
            axis = axis[0:1] #data validation to ensure axis is 1 character
        if axis == "x":
            if ref in self._xForces.keys():
                self._xForces.pop(ref)
        elif ref in self._yForces.keys():
            self._yForces.pop(ref)
    
    def containsForce(self, axis: str, ref: str):
        if len(axis) > 1:
            axis = axis[0:1] #truncate axis to only be 1 character
        if axis == "x":
            return ref in self._xForces.keys()
        else:
            return ref in self._yForces.keys()

    def killSelf(self):
        self.kill()

    def update(self, collidableObjects):
        if self.simulated:
            self.recalculateResultantForce() #methods are called in dependency order i.e. ResForce is required for getAcceleration() which is required for getVelocity(), etc.
            self._acceleration = self.getAcceleration()
            velocityChanged, initialVelocity, finalVelocity, directionChanged = self.getVelocity()
            self.displaceObject(velocityChanged=velocityChanged, initialVelocity=initialVelocity, finalVelocity=finalVelocity, directionChanged=directionChanged, collidableObjects=collidableObjects)

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())
            screen.blit(self.image, self.rect)

class Entity(PhysicsObject):
    def __init__(
            self,
            jumpForce: float,
            maxHP: int,
            defense: int,
            speed: float,
            pAttackCooldown: float,
            pSize: pygame.math.Vector2,
            spritePath: str,
            pMass: float,
            startingPosition: pygame.math.Vector2,
            pVelocityCap: pygame.math.Vector2,
            startingVelocity: pygame.math.Vector2 = pygame.math.Vector2(0,0),
            pTag: str = "None"
    ):
        super().__init__(
            pSize=pSize,
            spritePath=spritePath,
            pTag=pTag,
            pMass=pMass,
            startingPosition=startingPosition,
            startingVelocity=startingVelocity,
            pVelocityCap=pVelocityCap
        )
        self.isGrounded = False
        self._jumpForce = jumpForce
        self._originalAttributes = {
            "maxHP": maxHP,
            "defense": defense,
            "speed": speed,
            "attackCooldown": pAttackCooldown
        }
        self._maxHP = maxHP
        self.remainingHP = maxHP
        self._defense = defense
        self._speed = speed
        self.attackCooldown = pAttackCooldown
        self.cooldownRemaining = 0.0
        self._effects = {}
    
    def addEffect(self, ID: int):
        freeInstance = False
        currInstance = 0
        while not freeInstance:
            if not str(ID) + "-" + str(currInstance) in self._effects.keys():
                freeInstance = True
            else:
                currInstance += 1
        self._effects[str(ID)+"-"+str(currInstance)] = allEffects[ID] #allEffects is an IMPORTed dictionary containing all effects in the game in the format: array[2]
    
    #default instance to -1 to remove all instances of effect and default ID to -1 to remove all effects
    #forced is a local variable which tracks if an effect timed out or was forcefully removed by another function
    def removeEffect(self, ID: int = -1, instance: str = "-1", forced: bool =False):
        if ID > -1:
            if int(instance) > -1 and str(ID)+"-"+instance in self._effects.keys():
                self._effects.pop(str(ID)+"-"+instance)
            elif int(instance) < 0:
                for key in self._effects.keys():
                    if int(key.split("-")[0]) == ID:
                        self._effects.pop(key)
        else:
            self._effects = {}

        #if the removal was forced, recalculateAttributes() wouldn't have been run, so we need to run it here
        if forced:
            self._recalculateAttributes()
    
    def _recalculateAttributes(self):
        self._maxHP = self._originalAttributes["maxHP"]
        self._defense = self._originalAttributes["defense"]
        self._speed = self._originalAttributes["speed"]
        self.attackCooldown = self._originalAttributes["attackCooldown"]

        effectValues = [value for value in self._effects.values()]

        for index in range(0, len(effectValues)):
            splitValue = effectValues[index].split(", ") #double split to cover effects which affect multiple attributes
            splitEffects = [item.split(" ") for item in splitValue]
            for effect in splitEffects:
                self.modifyStat(effect[0], effect[1], effect[2])
            
        self._velocityCap *= self._speed #increase speed cap by a factor of _speed
    
    def modifyStat(self, stat: str, operator: str, magnitude: float):
        match stat:
            case "jumpForce":
                self._jumpForce = operators[operator](self._jumpForce, magnitude)
            case "maxHP":
                self._maxHP = operators[operator](self._maxHP, magnitude) #effect is a string in the format "[affected_variable] [operator] [operand]"
            case "defense":
                self._defense = operators[operator](self._defense, magnitude)
            case "speed":
                self._speed = operators[operator](self._speed, magnitude)
            case "cooldown":
                self.attackCooldown = operators[operator](self.attackCooldown, magnitude)
    
    def jump(self):
        self._velocity.y += self._jumpForce
        self.isGrounded = False
    
    def update(self, collidableObjects):
        for key in self._effects.keys():
            self._effects[key][1] -= 1/FPS #FPS is a global variable denoting the number of game updates per second - 1/FPS is the time since last frame
            if self._effects[key][1] <= 0:
                self.removeEffect(ID=int(key.split("-")[0]), instance=key.split("-")[1], forced=False)

        if self.simulated:
            self._recalculateAttributes()

            self.recalculateResultantForce()
            self._acceleration = self.getAcceleration(accelerationMultiplier=self._speed)
            velocityChanged, initialVelocity, finalVelocity, directionChanged = self.getVelocity()
            self.displaceObject(velocityChanged=velocityChanged, initialVelocity=initialVelocity, finalVelocity=finalVelocity, directionChanged=directionChanged, collidableObjects=collidableObjects)

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())
            screen.blit(self.image, self.rect)

class Player(Entity):
    def __init__(
            self,
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
            jumpForce,
            maxHP,
            defense,
            speed,
            pAttackCooldown,
            pSize,
            spritePath,
            pMass,
            startingPosition,
            pVelocityCap,
            startingVelocity,
            pTag
        )
        self.inventory = {}
        self.__offset = offset
        self.weapon = Weapon(pID=startingWeaponID, startingPosition=pygame.Vector2(round(self.rect.centerx + self.__offset.x), round(self.rect.centery + self.__offset.y))) #TODO: change once default weapon implemented
    
    def pickupItem(self, ID: int, replaces: str):
        newData = None
        if replaces == "weapon":
            newData = self.weapon.ID
            self.weapon.killSelf() #destroy the current weapon
            self.weapon = Weapon(pID=ID, startingPosition=pygame.Vector2(round(self.rect.centerx + self.__offset.x), round(self.rect.centery + self.__offset.y))) #and replace it with a new instance of the picked up weapon
        
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
            self._effects[key][1] -= 1/FPS #FPS is a global variable denoting the number of game updates per second - 1/FPS is the time since last frame
            if self._effects[key][1] <= 0:
                self.removeEffect(ID=int(key.split("-")[0]), instance=key.split("-")[1], forced=False)

        if self.simulated:
            self._recalculateAttributes()

            self.recalculateResultantForce()
            self._acceleration = self.getAcceleration(accelerationMultiplier=self._speed)
            velocityChanged, initialVelocity, finalVelocity, directionChanged = self.getVelocity()
            displacement = self.displaceObject(velocityChanged=velocityChanged, initialVelocity=initialVelocity, finalVelocity=finalVelocity, directionChanged=directionChanged, collidableObjects=collidableObjects)
            self.weapon.rect.center = (round(self.weapon.rect.centerx + displacement[0]), self.weapon.rect.centery)
            if directionChanged:
                self.weapon.image = pygame.transform.flip(self.image, True, False) #flip the weapon sprite on the x axis
                if self._velocity.x < 0: #right -> left
                   self.weapon.rect.center = (round(self.weapon.rect.centerx - (self.__offset.x * 2)), self.weapon.rect.centery) #move the weapon center left by 2*offset to swap the side it's attached to
                else: #left -> right
                    self.weapon.rect.center = (round(self.weapon.rect.centerx + (self.__offset.x * 2)), self.weapon.rect.centery)

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())
            screen.blit(self.image, self.rect)

class Weapon(pygame.sprite.Sprite):
    def __init__(self, pID: int, startingPosition: pygame.Vector2):
        super().__init__()
        self.ID = pID
        self.__replaces = "weapon"
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
        self.simulated = True
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
        player.pickupItem(ID=self.ID, replaces=self.__replaces)
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
