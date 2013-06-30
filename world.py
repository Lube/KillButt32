import pygame, random, sys, time, math, os, copy
from pygame.locals import *

RIGHT, UP, LEFT, DOWN = (1,1), (1,-1), (-1,-1), (-1,1)
NE, SE, NO, SO = (0,-1), (1,0), (-1,0), (0,1)

FACINGS = {RIGHT:0, DOWN:1, NE:6, NO:3 ,UP:4 ,SE:5 ,SO:2 ,LEFT:7, (0,0): 0}
 
Key2Dir   = {275: RIGHT, 273:DOWN, 276:LEFT, 274:UP, K_ESCAPE:QUIT}
NONE = (0,0)
FPS = 45
WINDOWWIDTH, WINDOWHEIGHT = 1000, 700
TILEH, TILEW, GAPSIZE = 32, 64, 1
BOARDWIDTH = 15
HALF = WINDOWWIDTH / 2
HTILEH = 0.5 * TILEH
HTILEW = 0.5 * TILEW

#           R,    G,    B
BLACK =     (0  , 0  ,  0  )
WHITE =     (255, 255,  255)
GREEN =     (0  , 160,  50 )


def main():

    global FPSCLOCK, DISPLAYSURF, BASICFONT, aSpriteSheet, unMapa, aCamera, tileList, Commands, aChar, command, Collisionables
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('mapReader 2.0')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 36)
    pygame.display.set_caption('mapReader 2.0')
    
    NR = True
    print NR
    mainWorld = level(True)
   
    unMapa = readMap('pancamera.txt')

    aSpriteSheet = spritesheet(unMapa.tileset)
    bSpriteSheet = spritesheet('swordwalking.png')
    aChar = character()

    for directions in range(8):
            aChar.animations.append(bSpriteSheet.load_strip((0,directions*48,48,48), 8, colorkey=(0, 0, 0)))

    tileList = {}
    
    command = (0,0)   
    Commands = []
    aCamera = Camera('STATIC', aChar)
    
    Collisionables = unMapa.getCollisionables()
        
    while command != QUIT:
        mainWorld.update(NR)

        
def getCommand ():
    for event in pygame.event.get():        
        if event.type == pygame.KEYUP:
            Commands.remove(Key2Dir[event.key])
        elif event.type == pygame.KEYDOWN:   
            Commands.append(Key2Dir[event.key])

    if len(Commands) == 0:
            return (0,0)
    else:
            Acum = (0,0)
            for Command in Commands:
                Acum = Acum[0] + Command[0], Acum[1] + Command[1]
             
            if abs(Acum[0]) > 1:
                if Acum[0] == 2:
                    Acum = 1 , Acum[1]
                else:
                    Acum = -1 , Acum[1]
                    
            if abs(Acum[1]) > 1:
                if Acum[1] == 2:
                    Acum = Acum[0] , 1
                else:
                    Acum = Acum[0] , -1
            return Acum
        

class Camera(object):
    x = 0
    y = 0
    xyTile = 0,0
    mode = ''
    xRange = 0
    yRange = 0
    
    def __init__(self, aMode, aChar):
        self.x = 0
        self.y = 0
        self.xyTile = 0,0
        self.mode = aMode
        
        if self.mode == 'DYNAMIC':
            self.xyTile = copy.copy(aChar.pos)
            self.xRange, self.yRange = 15,15
        else:
            self.xRange, self.yRange = 5,5
            self.xyTile = aChar.pos
            
        
    def update(self, aChar):
        if self.mode == 'DYNAMIC':
            if aChar.pos[0] > (self.xyTile[0] + (self.xRange - 2)):
                self.xyTile[0] += 1
            elif aChar.pos[0] < (self.xyTile[0] - (self.xRange - 1)):
                self.xyTile[0] -= 1
            elif aChar.pos[1] > (self.xyTile[1] + (self.yRange - 2)):
                self.xyTile[1] += 1
            elif aChar.pos[1] < (self.xyTile[1] - (self.yRange - 1)):
                self.xyTile[1] -= 1
        if self.mode == 'STATIC':
                self.xyTile = aChar.pos
                
        self.x = HALF + (self.xyTile[0]*HTILEW) - (self.xyTile[1]*HTILEW)
        self.y =(self.xyTile[0] + self.xyTile[1]) * HTILEH + 32
        #tuple(map(int,getVertsOfTile(aChar.pos[0], aChar.pos[1])))
        self.x, self.y = (self.x - WINDOWWIDTH/2), (self.y - WINDOWHEIGHT/2)
        
class spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error, message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit, message
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image, rect
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

def drawtile(tile, Col, Fila):
    Y = (Col + Fila) * HTILEH + 32 - aCamera.y
    X = HALF + (Col*HTILEW) - (Fila*HTILEW) - aCamera.x

    DISPLAYSURF.blit(tile, (X,Y))

def readMap(filename):
    assert os.path.exists(filename), 'No se puede encontrar el archivo' 
    mapFile = open(filename, 'r')
    # Cada nivel finaliza con una nueva linea
    lineas = mapFile.readlines() + ['\r\n']
    mapFile.close() # Cerramos el Archivo

    mapObj = mapObject() # Objeto mapa
    
    readingLayer, readingData = False, False
    currentLayer = ''
    nRows = -1
    csv = []
    
    for nLinea in lineas:
        # Process each line that was in the level file.
        line = nLinea.rstrip('\r\n')
        
        if ';' in line:
            # Ignore the ; lines, they're comments in the level file.
            line = line[:line.find(';')]
        if line.startswith('width='):
            mapObj.width = int(line[line.find('width='):].lstrip('width='))
        if line.startswith('height='):
            mapObj.height = int(line[line.find('height='):].lstrip('height='))
        if line.startswith('tilewidth='):
            mapObj.tilew = int(line[line.find('tilewidth='):].lstrip('tilewidth='))
        if line.startswith('tileheight='):
            mapObj.tileh = int(line[line.find('tileheight='):].lstrip('tileheight='))
        if 'tileset=' in line:
            tilesetdata = line[line.find('tileset='):].lstrip('tileset=').split(',')
            mapObj.tileset = tilesetdata[0]
            mapObj.tilesetXOffset = int(tilesetdata[3])
            mapObj.tilesetYOffset = int(tilesetdata[4])
            mapObj.tilesetWidth = int(tilesetdata[5])
            mapObj.tilesetHeight = int(tilesetdata[6])
            
        if '[layer]' in line:
            readingLayer = True
            
        if readingLayer and line == '':
            readingLayer = False
            readingData = False

        if 'type=' in line and readingLayer:
            currentLayer = line[line.find('type='):].lstrip('type=')
            mapObj.layers[currentLayer] = []
            nRows = 0
            #mapObj.layers[nLayers][0] = line[line.find('type='):].lstrip('type=')
        
        if 'data=' in line:
            readingData = True
        
        if readingLayer and readingData and 'data=' not in line:
            mapObj.layers[currentLayer].append([])
            csv = line.rstrip(',').split(',')
            for id in csv:
                trueId = int(id)  
                x = ((trueId-1) % (mapObj.tilesetWidth / mapObj.tilew)) * mapObj.tilew
                y = int((trueId-1) / (mapObj.tilesetWidth / mapObj.tilew)) * mapObj.tileh
                mapObj.layers[currentLayer][nRows].append((x,y))
            nRows += 1
                
    return mapObj

class mapObject:
    width = 0
    height = 0
    tilew = 0
    tileh = 0
    tileset = ''
    tilesetXOffset = 0
    tilesetYOffset = 0
    tilesetWidth = 0
    tilesetHeight = 0
    layers = {}
    
    def getCollisionables(self):
        Collisionables = []
        for y, rows in enumerate(self.layers['collision']):
            for x, tile in enumerate(rows):
                    if tile != (960, -32):
                        Collisionables.append(pygame.Rect(x-1, y-1,1,1))
        return Collisionables

    def draw(self, aCamera, aLayer):
            for x, rows in filter((lambda (x,y): x < aCamera.xyTile[1] + aCamera.yRange and x > aCamera.xyTile[1] - aCamera.yRange), enumerate(self.layers[aLayer])):
                for y, tile in filter(lambda (x,y): x < aCamera.xyTile[0] + aCamera.xRange and x > aCamera.xyTile[0] - aCamera.xRange, enumerate(rows)):
                        if tile in tileList:
                            drawtile(tileList[tile][0], y, x)
                        else:
                            tileList[tile] =  aSpriteSheet.image_at((tile[0],tile[1],64,32), colorkey=(0, 0, 0))
                            drawtile(tileList[tile][0], y, x)

class character:
    animations = []
    facing = RIGHT
    pos = [10,10]
    state = 3
    moving = False
    
    def draw(self):
        drawtile(self.animations[FACINGS[self.facing]][self.state][0], self.pos[0], self.pos[1])
        
    def update(self, command, collisionables):
        self.facing = command
        if command == (0,0) or self.willCollision(collisionables):
            self.moving = False
            self.state = 3
        else:
            xVec, yVec = command
            self.moving = True
            self.state = (self.state + 1) % len(self.animations[FACINGS[self.facing]])
            X,Y = self.pos
            self.pos = (X + xVec *0.1, Y-yVec * 0.1)

        
    def willCollision (self, collisionables):
        playerA = (self.pos[0] + (self.facing[0]*0.1))+0.5, (self.pos[1] - (self.facing[1]*0.1))+0.5
        playerB = (self.pos[0] + (self.facing[0]*0.1))-0.5, (self.pos[1] - (self.facing[1]*0.1))-0.2
        playerC = (self.pos[0] + (self.facing[0]*0.1))+0.2, (self.pos[1] - (self.facing[1]*0.1))-0.2
        playerD = (self.pos[0] + (self.facing[0]*0.1))-0.5, (self.pos[1] - (self.facing[1]*0.1))+0.5
        
        for tile in collisionables:
            if  tile.collidepoint(playerA) or tile.collidepoint(playerB)or tile.collidepoint(playerC)or tile.collidepoint(playerD):
                return True
        return False
    
    
def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)

class level():
    room = 'start'
    playable = False
    background = (0,0,0)

    def __init__(self,playable):
        self.playable = playable

    def start(self):
        DISPLAYSURF.fill(self.background)
        START_SURF, START_RECT = makeText('New Game', WHITE, GREEN, WINDOWWIDTH*0.3, WINDOWHEIGHT*0.7)
        EXIT_SURF, EXIT_RECT = makeText('Exit', WHITE, GREEN, WINDOWWIDTH*0.6, WINDOWHEIGHT*0.7)
        DISPLAYSURF.blit(START_SURF, START_RECT)
        DISPLAYSURF.blit(EXIT_SURF, EXIT_RECT)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                if START_RECT.collidepoint(event.pos):
                    self.room = 'world'
                    self.playable = True
                if EXIT_RECT.collidepoint(event.pos):
                    pygame.exit()
                    sys.quit()

    
    def world(self, NR):
        aCamera.update(aChar)            
        #print aChar.pos
        if NR:
                DISPLAYSURF.fill((0,0,0))
                unMapa.draw(aCamera, 'background')
                unMapa.draw(aCamera, 'collision')
                aChar.draw()
                unMapa.draw(aCamera, 'object')

        NR = aChar.moving
        command = getCommand()
        
        aChar.update(command, Collisionables)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

    def update(self, NR):
        if self.room == 'start':
            self.start()
        if self.room == 'world':
            self.world(NR)
            
if __name__ == '__main__':
    main()