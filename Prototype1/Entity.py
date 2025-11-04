import pygame
from PhysicsObject import PhysicsObject
from dictionaries import allEffects
from main import FPS, screen
import operator

operators = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv
}

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
