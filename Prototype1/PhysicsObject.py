import pygame
from main import FPS, screen, playerGroup

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
        self._yForces = {"gravity": pMass*9.81}
        self._resultantForce = pygame.Vector2(0,0)
        self._velocity = startingVelocity
        self._velocityCap = pVelocityCap
        self._acceleration = pygame.Vector2(0,0)
        self.blockedMotion = []
    
    def recalculateResultantForce(self):
        resXForce = 0
        resYForce = 0
        for force in self._xForces.values(): #sum of horizontal forces
            resXForce += force
        for force in self._yForces.values(): #sum of vertical forces
            resYForce += force
        self._resultantForce = pygame.math.Vector2(resXForce, resYForce) #store as vector2 (easier for later operations)
    
    def getAcceleration(self, accelerationMultiplier: float = 1.0):
        return (self._resultantForce / self._mass) * accelerationMultiplier
    
    def getVelocity(self):
        initialVelocity = self._velocity
        velocityChanged = []

        xVelocity = self._velocity.x + self._acceleration.x*(1/FPS)
        xVelocity = max(self._velocityCap.x * -1, min(xVelocity, self._velocityCap.x)) #clamping xVelocity to _velocityCap.x
            
        yVelocity = self._velocity.y + self._acceleration.y*(1/FPS)
        yVelocity = max(self._velocityCap.y * -1, min(yVelocity, self._velocityCap.y)) #same with yVelocity
        
        if xVelocity == initialVelocity.x: #check if either velocity has changed for displaceObject() equation
            velocityChanged[0] = True
        else:
            velocityChanged[0] = False
        
        if yVelocity == initialVelocity.y:
            velocityChanged[1] = True
        else:
            velocityChanged[1] = False
        
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
        if velocityChanged[0]: #if the velocity has changed, use s = (v^2 - u^2)/(2*a)
            xDisplacement = (finalVelocity.x**2 - initialVelocity.x**2)/(self._acceleration.x*2)
        else:
            xDisplacement = self._acceleration.x*(1/FPS)
        
        if velocityChanged[1]:
            yDisplacement = (finalVelocity.y**2 - initialVelocity.y**2)/(self._acceleration.y*2)
        else:
            yDisplacement = self._acceleration.y*(1/FPS)
        
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

        for collidable in collidableObjects:
            if collidable.tag == "wall" and collidable.simulated: #thinking ahead for when objects are de-rendered to improve performance
                if pygame.Rect.colliderect(collidable, newRectx):
                    if velocity[0] >= 0:
                        collidingDirections.append("r")
                        self.rect.center = (collidable.left, self.rect.center[1])
                    else:
                        collidingDirections.append("l")
                        self.rect.center = (collidable.right, self.rect.center[1])
                if pygame.Rect.colliderect(collidable, newRecty):
                    if velocity[1] >= 0:
                        collidingDirections.append("u")
                        self.rect.center = (self.rect.center[0], collidable.bottom)
                    else:
                        collidingDirections.append("d")
                        self.rect.center = (self.rect.center[0], collidable.top)

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
        if direction == "l" or direction == "down": #dirEffect is used to ensure magnitude follows the convention (-) = left or down, (+) = up or right
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