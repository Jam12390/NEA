import pygame
import typing
import operator

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
        self.updateDelay = 5 #frames between physics
        self.framesSinceLastUpdate = 0
        self.size = pSize
        self.image = pygame.transform.smoothscale(pygame.image.load(spritePath), (pSize.x, pSize.y))

        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = startingPosition
        self.simulated = True
        self.tag = pTag
        self._mass = pMass
        self._xForces = {}
        self._yForces = {"gravity": pMass*9.81*15} #gravity ignores mass
        self._resultantForce = pygame.Vector2(0,0)
        self._velocity = startingVelocity
        self._velocityCap = pVelocityCap
        self._baseVCap = pVelocityCap
        self._acceleration = pygame.Vector2(0,0)
        self.blockedMotion = []
        self.isGrounded = False
        self.shouldReturnDisplacement = False

        self.previousCollisionState = {

        }
    
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
        
        if xVelocity*3 in range(-1, 1):
            xVelocity = 0
        if yVelocity*3 in range(-1, 1):
            yVelocity = 0

        self._velocity = pygame.Vector2(xVelocity, yVelocity)

    def getVelocityValue(self):
        return self._velocity
    
    def getMass(self):
        return self._mass
    


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



    def collideCorner(
            self,
            collidable: pygame.sprite.Sprite,
            vertex: tuple[int, int], #(x, y)
            vertexKey: str, #e.g. tl -> top-left corner
            horizontalTags: list[str], #tags to look for during collision
            verticalTags: list[str]
    ) -> typing.Optional[dict[str]]: #str: any
        xKey = vertexKey[1:]
        yKey = vertexKey[:1]

        #print(f"{vertexKey} -> {pygame.Rect.collidepoint(collidable.rect, vertex)}")
        #print(f"{vertex} - {collidable.rect.center - pygame.Vector2(800, -1280/2)}")

        offset = pygame.Vector2(800, -1280/2)
        #collidable.rect.center -= offset
        #vertex -= offset
        #vertex += collidable.absoluteCoordinate

        collisionData = {}
        #print(f"{vertexKey} -> {pygame.Rect.collidepoint(collidable.rect, vertex)}")
        if collidable.rect.center[0] < 1000:
            print(f"{vertex} - {collidable.rect.center}")

        if not pygame.Rect.collidepoint(collidable.rect, vertex):
            a = collidable.rect.center
            return None

        vertex = pygame.Vector2(vertex[0], vertex[1])

        match xKey:
            case "l":
                xVelocityOperator = operator.lt #since this is a generic function, i need a variable operator to use
                collidableX = collidable.rect.right #same with sides
            case "r":
                xVelocityOperator = operator.gt
                collidableX = collidable.rect.left
        
        match yKey:
            case "t":
                yVelocityOperator = operator.lt
                collidableY = collidable.rect.bottom
            case "b":
                yVelocityOperator = operator.gt
                collidableY = collidable.rect.top

        xDiff = abs(vertex.x - collidableX)
        yDiff = abs(vertex.y - collidableY)

        #collidable.rect.center += offset

        
        collisionData["object"] = collidable
        collisionData["frictionCoef"] = collidable.frictionCoef

        if xDiff <= yDiff and xVelocityOperator(self._velocity.x, 0) and len(set(horizontalTags) & set(collidable.tags)) > 0:
            collisionData["side"] = xKey
            collisionData["difference"] = xDiff
        elif xDiff >= yDiff and yVelocityOperator(self._velocity.y, 0) and len(set(verticalTags) & set(collidable.tags)) > 0:
            collisionData["side"] = yKey
            collisionData["difference"] = yDiff
        else:
            return None
        
        return collisionData

    def renderCollisions(
            self,
            collidableObjects: list[pygame.sprite.Group],
            displacement: pygame.Vector2,
            isPlayer: bool = False
    ):
        self.blockedMotion = []

        collidingDirections = []
        collidingObjects = {}
        frictionCoefs = {}
        #potentialRect.center = self.absoluteCoordinate
        #potentialRect.centerx += displacement.x
        #potentialRect.centery += displacement.y

        #self.absoluteCoordinate = pygame.Vector2(self.absoluteCoordinate.x + displacement.x, self.absoluteCoordinate.y + displacement.y)

        originalDisplacement = tuple([displacement.x, displacement.y])
        originalDisplacement = pygame.Vector2(x=originalDisplacement[0], y=originalDisplacement[1])

        for group in collidableObjects:
            for collidable in group:

                if "item" in collidable.tags and self.tag == "player":
                    if pygame.Rect.colliderect(self.rect, collidable.rect): #collidable is an item in the scene
                        collidable.UIWindow.shown = True
                    else:
                        collidable.UIWindow.shown = False
                
            vertices = ["tl", "tr", "bl", "br"]
            
            for key in vertices:
                match key:
                    case "tl":
                        vertex = self.rect.topleft #(self.rect.left + self.absoluteCoordinate[0], self.rect.top + self.absoluteCoordinate[1])
                    case "tr":
                        vertex = self.rect.topright #(self.rect.right + self.absoluteCoordinate[0], self.rect.top + self.absoluteCoordinate[1])
                    case "bl":
                        vertex = self.rect.bottomleft #(self.rect.left + self.absoluteCoordinate[0], self.rect.bottom + self.absoluteCoordinate[1])
                    case "br":
                        vertex = self.rect.bottomright #(self.rect.right + self.absoluteCoordinate[0], self.rect.bottom + self.absoluteCoordinate[1])
                
                collisionData = self.collideCorner(
                    collidable=collidable,
                    vertex=vertex,
                    vertexKey=key,
                    horizontalTags=["wall"],
                    verticalTags=["floor", "lCorner", "rCorner", "roof"]
                )

                if collisionData != None:
                    collidingObjects[collisionData["side"]] = collidable
                    frictionCoefs[key] = collisionData["frictionCoef"]
                    collidingDirections.append(collisionData["side"])
                    match collisionData["side"]:
                        case "l":
                            displacement.x += collisionData["difference"]
                            #potentialRect.x += collisionData["difference"]
                            #potentialRect.move(x=collisionData["difference"])
                        case "r":
                            displacement.x -= collisionData["difference"]
                            #potentialRect.x += collisionData["difference"]
                            #potentialRect.move(x=collisionData["difference"])
                        case "t":
                            displacement.y += collisionData["difference"]
                            #potentialRect.x += collisionData["difference"]
                            #potentialRect.move(y=collisionData["difference"])
                        case "b":
                            displacement.y -= collisionData["difference"]
                            #potentialRect.y += collisionData["difference"]
                            #potentialRect.move(y=collisionData["difference"])
            
            collidingDirections = list(set(collidingDirections))

            if "b" in collidingDirections and len(set(["floor", "lCorner", "rCorner"]) & set(collidingObjects["b"].tags)) > 0:
                self.isGrounded = True
                self._velocity.y = min(self._velocity.y, 0)
                displacement.y = max(0, displacement.y)
                self.removeForce(axis="y", ref="UserInputDown")
            else:
                self.isGrounded = False
            
            #print(collidingDirections)
            
            for direction in collidingDirections:
                match direction:
                    case "l":
                        self._velocity.x = max(0, self._velocity.x)
                        displacement.x = max(0, displacement.x)
                    case "r":
                        self._velocity.x = min(self._velocity.x, 0)
                        displacement.x = min(displacement.x, 0)
                    case "u":
                        self._velocity.y = max(0, self._velocity.y)
                        displacement.y = max(0, displacement.y)
            
            self.__updateFriction(coef=frictionCoefs)

            if not isPlayer:
                #self.rect = displacement
                self.absoluteCoordinate += displacement
            else:
                return displacement
    
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
            
            xFriction = coef["d"][0]*strippedResForce.y if "d" in coef.keys() else coef["u"][0]*strippedResForce.y if "u" in coef.keys() else 0
            if strippedResForce.x != 0:
                xFriction = min(abs(strippedResForce.x), abs(xFriction))
            xDirection = "r" if self._velocity.x < 0 else "l"
        else:
            xFriction = 0

        if not(-2.75 < self._velocity.y and self._velocity.y < 2.75):
            if not ("d" in coef.keys() or "u" in coef.keys()):
                yAirResistance = abs(airResistanceCoef * self._velocity.y * self.FPS)

            yFriction = coef["l"][1]*strippedResForce.y if "l" in coef.keys() else coef["r"][1]*strippedResForce.y if "r" in coef.keys() else 0
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


    def displaceObject(
            self,
            collidableObjects,
            isPlayer=False
    ) -> typing.Optional[pygame.Vector2]:
        
        xDisplacement = self._velocity.x*5*(1/self.FPS)
        yDisplacement = self._velocity.y*5*(1/self.FPS) #conversion of 1m -> 5pix - no

        finalDisplacement = self.renderCollisions(collidableObjects=collidableObjects, displacement=pygame.Vector2(xDisplacement, yDisplacement), isPlayer=isPlayer) #update position - playerMoved
        
        if isPlayer:
            return finalDisplacement #pygame.math.Vector2(xDisplacement, yDisplacement) #finalDisplacement



    def update(self, collidableObjects, playerMoved=(0, 0)):
        if self.simulated and self.framesSinceLastUpdate / self.updateDelay > 1:
            self._resultantForce = self.recalculateResultantForce() #methods are called in dependency order i.e. ResForce is required for getAcceleration() which is required for getVelocity(), etc.
            self._acceleration = self.getAcceleration()
            self.getVelocity()
            self.displaceObject(collidableObjects=collidableObjects, playerMoved=playerMoved)

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())
        else:
            self.framesSinceLastUpdate += 1
            self.displaceObject(collidableObjects=collidableObjects, playerMoved=playerMoved)