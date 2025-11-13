import pygame

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
        self._yForces = {"gravity": pMass*9.81*15}
        self._resultantForce = pygame.Vector2(0,0)
        self._velocity = startingVelocity
        self._velocityCap = pVelocityCap
        self._baseVCap = pVelocityCap
        self._acceleration = pygame.Vector2(0,0)
        self.blockedMotion = []
        self.isGrounded = False
    
    def recalculateResultantForce(self, forceMult: float = 1, includedForces: list = []):
        resXForce = 0
        resYForce = 0

        xForces, xForceKeys = [force for force in self._xForces.values()], [key for key in self._xForces.keys()]
        yForces, yForceKeys = [force for force in self._yForces.values()], [key for key in self._yForces.keys()]

        for index in range(0, len(xForces)): #sum of horizontal forces
            resXForce += xForces[index] if xForceKeys[index] not in includedForces else xForces[index] * forceMult
        for index in range(0, len(yForces)): #sum of vertical forces
            resYForce += yForces[index] if yForceKeys[index] not in includedForces else yForces[index] * forceMult
        return pygame.Vector2(resXForce, resYForce) #store as vector2 (easier for later operations)
    
    def getAcceleration(self):
        return (self._resultantForce / self._mass) #a = F/m
    
    def getVelocity(self):
        initialVelocity = self._velocity

        overflowReductionRate = 2

        if initialVelocity.x > self._velocityCap.x:
            xVelocity = initialVelocity.x - overflowReductionRate
            xVelocity += min(self._acceleration.y*(1/self.FPS), 0)
        elif initialVelocity.x < self._velocityCap.x*-1:
            xVelocity = initialVelocity.x + overflowReductionRate
            xVelocity += max(self._acceleration.y*(1/self.FPS), 0)
        else:
            xVelocity = self._velocity.x + self._acceleration.x*(1/self.FPS)
            xVelocity = max(self._velocityCap.x * -1, min(xVelocity, self._velocityCap.x)) #clamping xVelocity to _velocityCap.x
        
        if initialVelocity.y > self._velocityCap.y:
            yVelocity = initialVelocity.y - overflowReductionRate
            yVelocity += self._acceleration.y*(1/self.FPS) if self._acceleration.y <= 0 else 0
        elif initialVelocity.y < self._velocityCap.y*-1:
            yVelocity = initialVelocity.y + overflowReductionRate
            yVelocity += self._acceleration.y*(1/self.FPS) if self._acceleration.y >= 0 else 0
        else:
            yVelocity = self._velocity.y + self._acceleration.y*(1/self.FPS)
            yVelocity = max(self._velocityCap.y * -1, min(yVelocity, self._velocityCap.y)) #same with yVelocity
        
        self._velocity = pygame.Vector2(xVelocity, yVelocity)

    def getVelocityValue(self):
        return self._velocity
    
    def getMass(self):
        return self._mass
    
    def displaceObject(
            self,
            collidableObjects
    ):
        
        xDisplacement = self._velocity.x*5*(1/self.FPS)
        yDisplacement = self._velocity.y*5*(1/self.FPS) #conversion of 1m -> 5pix

        self.renderCollisions(collidableObjects=collidableObjects, displacement=pygame.Vector2(xDisplacement, yDisplacement)) #update position

        if "l" in self.blockedMotion:
            self._velocity.x = 0 #assume velocity is in the same direction and therefore set it to 0
        
        if "r" in self.blockedMotion:
            self._velocity.x = 0
        
        if "d" in self.blockedMotion:
            self._velocity.y = 0
        
        if "u" in self.blockedMotion:
            self._velocity.y = 0
        
        return pygame.math.Vector2(xDisplacement, yDisplacement)
    
    def renderCollisions(self, collidableObjects, displacement: pygame.math.Vector2):
        self.blockedMotion = []
        collidingDirections = []

        frictionCoefs = {}

        self.rect.center = (round(self.rect.centerx + displacement.x), round(self.rect.centery + displacement.y))

        for group in collidableObjects:
            for collidable in group:
                if collidable.tag == "item" and self.tag == "player":
                    if pygame.Rect.colliderect(self.rect, collidable.rect): #collidable is an item in the scene
                        collidable.UIWindow.shown = True
                    else:
                        collidable.UIWindow.shown = False

                if collidable.tag in ["wall", "floor"] and collidable.simulated: #thinking ahead for when objects are de-rendered to improve performance
                    #bottom left corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.bottomleft):
                        xDiff = abs(self.rect.left - collidable.rect.right)
                        yDiff = abs(self.rect.bottom - collidable.rect.top)

                        if xDiff < yDiff and self._velocity.x < 0:
                            self.rect.left = collidable.rect.right
                            collidingDirections.append("l")
                            frictionCoefs["l"] = collidable.frictionCoef
                        elif xDiff > yDiff and self._velocity.y > 0:
                            self.rect.bottom = collidable.rect.top
                            collidingDirections.append("d")
                            frictionCoefs["d"] = collidable.frictionCoef

                    #top left corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.topleft):
                        xDiff = abs(self.rect.left - collidable.rect.right)
                        yDiff = abs(self.rect.top - collidable.rect.bottom)

                        if xDiff < yDiff and self._velocity.x < 0:
                            self.rect.left = collidable.rect.right
                            collidingDirections.append("l")
                            frictionCoefs["l"] = collidable.frictionCoef
                        elif xDiff > yDiff and self._velocity.y < 0:
                            self.rect.top = collidable.rect.bottom
                            collidingDirections.append("u")
                            frictionCoefs["u"] = collidable.frictionCoef

                    #top right corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.topright):
                        xDiff = abs(self.rect.right - collidable.rect.left)
                        yDiff = abs(self.rect.top - collidable.rect.bottom)

                        if xDiff < yDiff and self._velocity.x > 0:
                            self.rect.right = collidable.rect.left
                            collidingDirections.append("r")
                            frictionCoefs["r"] = collidable.frictionCoef
                        elif xDiff > yDiff and self._velocity.y < 0:
                            self.rect.top = collidable.rect.bottom
                            collidingDirections.append("u")
                            frictionCoefs["u"] = collidable.frictionCoef

                    #bottom right corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.bottomright):
                        xDiff = abs(self.rect.right - collidable.rect.left)
                        yDiff = abs(self.rect.bottom - collidable.rect.top)

                        if xDiff < yDiff and self._velocity.x > 0:
                            self.rect.right = collidable.rect.left
                            collidingDirections.append("r")
                            frictionCoefs["r"] = collidable.frictionCoef
                        elif xDiff > yDiff and self._velocity.y > 0:
                            self.rect.bottom = collidable.rect.top
                            collidingDirections.append("d")
                            frictionCoefs["d"] = collidable.frictionCoef
                    
                    groundedTolerance = self.rect.bottom + 5
                    '''
                    pygame.Rect.collidepoint doesn't return true if points are bordering on a rect
                    due to this, for frame 1 after floor collision, although the object is technically grounded, renderCollision doesn't return true since the points are "bordering"
                    this causes inaccuracies when calculating friction since friction = resForce.axis in the opposite direction and if the player isn't grounded, UserInputDown can be applied.
                    to solve this, we add a tolerance to the bottom of the rect to check if the object is close enough to be grounded without editing its actual position
                    '''
                    if pygame.Rect.collidepoint(collidable.rect, (self.rect.left, groundedTolerance)) or pygame.Rect.collidepoint(collidable.rect, (self.rect.right, groundedTolerance)):
                        self.isGrounded = True
                        self.removeForce(axis="y", ref="UserInputDown")
                    else:
                        self.isGrounded = False

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
        self.removeForce(axis="x", ref="xAirResistance")
        self.removeForce(axis="y", ref="yAirResistance")

        xAirResistance = 0
        yAirResistance = 0
        xFriction = 0
        yFriction = 0

        airResistanceCoef = 0.01

        strippedResForce = self.recalculateResultantForce()

        if not(-2.75 < self._velocity.x and self._velocity.x < 2.75):
            if not ("l" in coef.keys() or "r" in coef.keys()):
                xAirResistance = abs(airResistanceCoef * self._velocity.x * self.FPS)
            
            xFriction = coef["d"]*strippedResForce.y if "d" in coef.keys() else coef["u"]*strippedResForce.y if "u" in coef.keys() else 0
            if strippedResForce.x != 0:
                xFriction = min(abs(strippedResForce.x), abs(xFriction))
            xDirection = "r" if self._velocity.x < 0 else "l"
        else:
            xFriction = 0

        if not(-2.75 < self._velocity.y and self._velocity.y < 2.75):
            if not ("d" in coef.keys() or "u" in coef.keys()):
                yAirResistance = abs(airResistanceCoef * self._velocity.y * self.FPS)

            yFriction = coef["l"]*strippedResForce.y if "l" in coef.keys() else coef["r"]*strippedResForce.y if "r" in coef.keys() else 0
            if strippedResForce.y != 0:
                yFriction = min(abs(strippedResForce.y), abs(yFriction))
            yDirection = "u" if self._velocity.y > 0 else "d"
        else:
            yFriction = 0

        if xFriction != 0:
            self.addForce(axis="x", direction=xDirection, ref="xFriction", magnitude=xFriction) #direction will always be bound if friction != 0, so ignore #type: ignore
        if yFriction != 0:
            self.addForce(axis="y", direction=yDirection, ref="yFriction", magnitude=yFriction) #type: ignore
        if xAirResistance != 0 and ((xFriction != strippedResForce.x and xFriction != 0) or not self.isGrounded):
            self.addForce(axis="x", direction="l" if self._velocity.x > 0 else "r", ref="xAirResistance", magnitude=xAirResistance)
        if yAirResistance != 0 and yFriction != strippedResForce.y:
            self.addForce(axis="y", direction="u" if self._velocity.y < 0 else "d", ref="yAirResistance", magnitude=yAirResistance)


    def killSelf(self):
        self.kill()

    def update(self, collidableObjects):
        if self.simulated:
            self._resultantForce = self.recalculateResultantForce() #methods are called in dependency order i.e. ResForce is required for getAcceleration() which is required for getVelocity(), etc.
            self._acceleration = self.getAcceleration()
            self.getVelocity()
            self.displaceObject(collidableObjects=collidableObjects)

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())