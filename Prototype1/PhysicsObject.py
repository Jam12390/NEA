import pygame

def normalise(value):
    return value * (-1 if value < 0 else 1) 

class PhysicsObject(pygame.sprite.Sprite):
    def __init__(
            self,
            FPS: int,
            pSize: pygame.Vector2,
            spritePath: str,
            pMass: float,
            startingPosition: pygame.Vector2,
            pVelocityCap: pygame.Vector2,
            startingVelocity: pygame.Vector2 = pygame.Vector2(0, 0),
            pTag: str = "none",
    ):
        super().__init__()
        self.FPS = FPS
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
        #print(f"ResForce{self._resultantForce}")
    
    def getAcceleration(self, accelerationMultiplier: float = 1.0):
        #print(f"Acceleration{(self._resultantForce / self._mass) * accelerationMultiplier}")
        return (self._resultantForce / self._mass) * accelerationMultiplier
    
    def getVelocity(self):
        initialVelocity = self._velocity
        velocityChanged = []

        if initialVelocity.x > self._velocityCap.x:
            xVelocity = initialVelocity.x - 0.5
            xVelocity += self._acceleration.y*(1/self.FPS) if self._acceleration.y <= 0 else 0
        elif initialVelocity.x < self._velocityCap.x*-1:
            xVelocity = initialVelocity.x + 0.5
            xVelocity += self._acceleration.y*(1/self.FPS) if self._acceleration.y >= 0 else 0
        else:
            xVelocity = self._velocity.x + self._acceleration.x*(1/self.FPS)
            xVelocity = max(self._velocityCap.x * -1, min(xVelocity, self._velocityCap.x)) #clamping xVelocity to _velocityCap.x
        
        if initialVelocity.y > self._velocityCap.y:
            yVelocity = initialVelocity.y - 0.5
            yVelocity += self._acceleration.y*(1/self.FPS) if self._acceleration.y <= 0 else 0
        elif initialVelocity.y < self._velocityCap.y*-1:
            yVelocity = initialVelocity.y + 0.5
            yVelocity += self._acceleration.y*(1/self.FPS) if self._acceleration.y >= 0 else 0
        else:
            yVelocity = self._velocity.y + self._acceleration.y*(1/self.FPS)
            yVelocity = max(self._velocityCap.y * -1, min(yVelocity, self._velocityCap.y)) #same with yVelocity

        #print(f"Velocity{xVelocity, yVelocity}")
        
        if xVelocity == initialVelocity.x: #check if either velocity has changed for displaceObject() equation
            velocityChanged.append(False)
        else:
            velocityChanged.append(True)
        
        if yVelocity == initialVelocity.y:
            velocityChanged.append(False)
        else:
            velocityChanged.append(True)
        
        if (initialVelocity.x < 0 and xVelocity >= 0) or (initialVelocity.x > 0 and xVelocity <= 0): #check if the object's weapon needs to change position
            directionChanged = True
        else:
            directionChanged = False
        
        self._velocity = pygame.Vector2(xVelocity, yVelocity)
        
        return directionChanged

    def getVelocityValue(self):
        return self._velocity
    
    def getMass(self):
        return self._mass
    
    def displaceObject(
            self,
            collidableObjects
    ):
        #xDenominator = 1 if self._acceleration.x*2 == 0 else self._acceleration.x*2 #prevent /0 errors
        #yDenominator = 1 if self._acceleration.y*2 == 0 else self._acceleration.y*2

        if False:#velocityChanged[0]: #if the velocity has changed, use s = (v^2 - u^2)/(2*a)
            xDisplacement = (finalVelocity.x**2 - initialVelocity.x**2)/xDenominator
        else:
            xDisplacement = self._velocity.x*5*(1/self.FPS)
        
        if False:#velocityChanged[1]:
            yDisplacement = (finalVelocity.y**2 - initialVelocity.y**2)/yDenominator
        else:
            yDisplacement = self._velocity.y*5*(1/self.FPS) #conversion of 1m -> 5pix?
        
        #print(f"Displacement{xDisplacement, yDisplacement}")

        self.renderCollisions(collidableObjects=collidableObjects, displacement=pygame.Vector2(xDisplacement, yDisplacement)) #update position

        if "l" in self.blockedMotion:
            xDisplacement = 0 #don't move the object
            self._velocity.x = 0 #assume velocity is in the same direction and therefore set it to 0
        
        if "r" in self.blockedMotion:
            xDisplacement = 0
            self._velocity.x = 0
        
        if "d" in self.blockedMotion:
            yDisplacement = 0
            self._velocity.y = 0
        
        if "u" in self.blockedMotion:
            yDisplacement = 0
            self._velocity.y = 0
        
        return pygame.math.Vector2(xDisplacement, yDisplacement) #for use in updating weapon position in Player subclass
    
    def renderCollisions(self, collidableObjects, displacement: pygame.math.Vector2):
        self.blockedMotion = []
        collidingDirections = []

        frictionCoefs = {}

        newRectx = self.rect
        newRectx.center = (round(newRectx.center[0] + displacement.x), newRectx.center[1])

        newRecty = self.rect
        newRecty.center = (newRecty.center[0], round(newRectx.center[1] + displacement.y))

        self.rect.center = (round(self.rect.centerx + displacement.x), round(self.rect.centery + displacement.y))
        for group in collidableObjects:
            for collidable in group:
                if collidable.tag == "item" and self.tag == "player":
                    if pygame.Rect.colliderect(self.rect, collidable.rect):
                        collidable.UIWindow.shown = True
                    else:
                        collidable.UIWindow.shown = False

                if collidable.tag in ["wall", "floor"] and collidable.simulated: #thinking ahead for when objects are de-rendered to improve performance
                    #bottom left corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.bottomleft):
                        xDiff = normalise(self.rect.left - collidable.rect.right)
                        yDiff = normalise(self.rect.bottom - collidable.rect.top)

                        if xDiff < yDiff:
                            self.rect.left = collidable.rect.right
                            collidingDirections.append("l")
                            frictionCoefs["l"] = collidable.frictionCoef
                        else:
                            self.rect.bottom = collidable.rect.top
                            collidingDirections.append("d")
                            frictionCoefs["d"] = collidable.frictionCoef
                            if collidable.tag == "floor":
                                self.isGrounded = True

                    #top left corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.topleft):
                        xDiff = normalise(self.rect.left - collidable.rect.right)
                        yDiff = normalise(self.rect.top - collidable.rect.bottom)

                        if xDiff < yDiff:
                            self.rect.left = collidable.rect.right
                            collidingDirections.append("l")
                            frictionCoefs["l"] = collidable.frictionCoef
                        else:
                            self.rect.top = collidable.rect.bottom
                            collidingDirections.append("u")
                            frictionCoefs["u"] = collidable.frictionCoef

                    #top right corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.topright):
                        xDiff = normalise(self.rect.right - collidable.rect.left)
                        yDiff = normalise(self.rect.top - collidable.rect.bottom)

                        if xDiff < yDiff:
                            self.rect.right = collidable.rect.left
                            collidingDirections.append("r")
                            frictionCoefs["r"] = collidable.frictionCoef
                        else:
                            self.rect.top = collidable.rect.bottom
                            collidingDirections.append("u")
                            frictionCoefs["u"] = collidable.frictionCoef

                    #bottom right corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.bottomright):
                        xDiff = normalise(self.rect.right - collidable.rect.left)
                        yDiff = normalise(self.rect.bottom - collidable.rect.top)

                        if xDiff < yDiff:
                            self.rect.right = collidable.rect.left
                            collidingDirections.append("r")
                            frictionCoefs["r"] = collidable.frictionCoef
                        else:
                            self.rect.bottom = collidable.rect.top
                            collidingDirections.append("d")
                            frictionCoefs["d"] = collidable.frictionCoef
                            if collidable.tag == "floor":
                                self.isGrounded = True
                #if pygame.Rect.colliderect(collidable.rect, newRectx): ADD TO DOC FOR TEST 1
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

        if not "d" in collidingDirections:
            self.isGrounded = False
        for direction in collidingDirections:
            if not direction in self.blockedMotion:
                self.blockedMotion.append(direction)
        self.__updateFriction(coef=frictionCoefs)

    def addForce(
            self,
            axis: str, #python doesn't have a char datatype, so we need data validation to ensure len(axis) = 1
            direction: str,
            ref: str,
            magnitude: float

    ):
        if len(axis) > 0:
            axis = axis[0:1] #data validation to ensure axis is 1 character
        if direction == "l" or direction == "u": #dirEffect is used to ensure magnitude follows PYGAME's convention (-) = left or up, (+) = down or right
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
    
    def __updateFriction(self, coef: dict):
        self.removeForce(axis="x", ref="xFriction")
        self.removeForce(axis="y", ref="yFriction")

        if not(-1 < self._velocity.x and self._velocity.x < 1):
            xFriction = coef["d"]*self._resultantForce.y if "d" in coef.keys() else coef["u"]*self._resultantForce.y if "u" in coef.keys() else 0
            xDirection = "r" if self._velocity.x < 0 else "l"
        else:
            xFriction = 0
        
        if not(-1 < self._velocity.x and self._velocity.x < 1):
            yFriction = coef["l"]*self._resultantForce.y if "l" in coef.keys() else coef["r"]*self._resultantForce.y if "r" in coef.keys() else 0
            yDirection = "d" if self._velocity.y > 0 else "u"
        else:
            yFriction = 0

        if xFriction != 0:
            self.addForce(axis="x", direction=xDirection, ref="xFriction", magnitude=xFriction) #direction will always be bound if friction != 0, so ignore
        if yFriction != 0:
            self.addForce(axis="y", direction=yDirection, ref="yFriction", magnitude=yFriction)


    def killSelf(self):
        self.kill()

    def update(self, collidableObjects):
        if self.simulated:
            self.recalculateResultantForce() #methods are called in dependency order i.e. ResForce is required for getAcceleration() which is required for getVelocity(), etc.
            self._acceleration = self.getAcceleration()
            self.getVelocity()
            self.displaceObject(collidableObjects=collidableObjects)

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())