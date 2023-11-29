# Module Imports
import pygame
import random
import socket
import threading

HOST = 'localhost'
PORT = 12345
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)
# Module Initialization
pygame.init()

# Game Assets and Objects
class Ship:
    def __init__(self, name, img, pos, size, numGuns=0, gunPath=None, gunsize = None,  gunCoordsOffset=None):
        self.name = name
        self.pos = pos
        # Carregar a imagem Vertical
        self.vImage = loadImage(img, size)
        self.vImageWidth = self.vImage.get_width()
        self.vImageHeight = self.vImage.get_height()
        self.vImageRect = self.vImage.get_rect()
        self.vImageRect.topleft = pos
        # Carregar a imagem Horizontal
        self.hImage = pygame.transform.rotate(self.vImage, -90)
        self.hImageWidth = self.hImage.get_width()
        self.hImageHeight = self.hImage.get_height()
        self.hImageRect = self.hImage.get_rect()
        self.hImageRect.topleft = pos
        # Imagem e Rectangle
        self.image = self.vImage
        self.rect = self.vImageRect
        self.rotation = False
        # Navio esta selecionado
        self.active = False
        # Carregar a imagem das armas
        self.gunlist = []
        if numGuns > 0:
            self.gunCoordsOffset = gunCoordsOffset
            for num in range(numGuns):
                self.gunlist.append(
                    Guns(gunPath,
                         self.rect.center,
                         (size[0] * gunsize[0],
                          size[1] * gunsize[1]),
                         self.gunCoordsOffset[num])
                    
                )
        
    def selectShipAndMove(self):
        """Seleciona os barcos e move de acordo com a posição do mouse"""
        while self.active == True:
            self.rect.center= pygame.mouse.get_pos()
            updateGameScreen(GAMESCREEN)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                #if not self.checkForCollisions(pFleet): #por causa dessa linha de código o meu jogo fecha do nada
                    if event.button == 1:
                        self.hImageRect.center = self.vImageRect.center = self.rect.center
                        self.active = False
                    if event.button == 3:#gira
                        self.rotateShip()

    def rotateShip(self, doRotation=False):
        '''Vira o navio vertical e horizontal'''
        if self.active or doRotation == True:
            if self.rotation == False:
                self.rotation = True
            else:
                self.rotation = False
            self.switchImageAndRect()

    def switchImageAndRect(self):
        '''Vira o navio vertical e horizontal sla'''
        if self.rotation == True:
            self.image = self.hImage
            self.rect = self.hImageRect
        else:
            self.image = self.vImage
            self.rect = self.vImageRect
        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def checkForCollisions(self, shiplist):
        '''para conferir que os navios não estão colidindo entre si'''
        slist = shiplist.copy()
        slist.remove(self)
        for item in slist:
            if self.rect.colliderect(item.rect):
                return True
        return False

    def checkForRotateCollision(self, shiplist):
        '''para ter certeza de que o navio não vai colidir com outros quando virar'''
        slist = shiplist.copy()
        slist.remove(self)
        for ship in shiplist:
            if self.rotation == True:
                if self.vImageRect.colliderect(ship.rect):
                    return True
            else:
                if self.hImageRect.colliderect(ship.rect):
                    return True
                
        return False

    def returnToDefaultPosition(self):
        '''Faz o navio voltar pra posição padrão'''
        if self.rotation == True:
            self.rotateShip(True) #meio que desvira o barco fora do grid
        
        self.rect.topleft = self.pos
        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def snapToGridEdge(self, gridCoords):
        if self.rect.topleft != self.pos:
            #check para verificar se a posição do navio está fora do grid
            if self.rect.left > gridCoords[0][-1][0] + 50 or \
                self.rect.right < gridCoords[0][0][0] or \
                self.rect.top > gridCoords[-1][0][1] + 50 or \
                self.rect.bottom < gridCoords[0][0][1]:
                self.returnToDefaultPosition()
            
            elif self.rect.right > gridCoords[0][-1][0]+50:
                self.rect.right = gridCoords[0][-1][0] + 50
            elif self.rect.left < gridCoords[0][0][0]:
                self.rect.left = gridCoords[0][0][0]
            elif self.rect.top < gridCoords[0][0][1]:
                self.rect.top = gridCoords[0][0][1]
            elif self.rect.bottom > gridCoords[-1][0][1] + 50:
                self.rect.bottom = gridCoords[-1][0][1] + 50
            self.vImageRect.center = self.hImageRect.center = self.rect.center

    def snapToGrid(self, gridCoords):
        for rowX in gridCoords:
            for cell in rowX:
                if self.rect.left >= cell[0] and self.rect.left < cell[0] + CELLSIZE \
                    and self.rect.top >= cell[1] and self.rect.top < cell[1] + CELLSIZE:
                    if self.rotation == False:
                        self.rect.topleft = (cell[0] + (CELLSIZE - self.image.get_width())//2, cell[1])
                    else:
                        self.rect.topleft = (cell[0], cell[1] + (CELLSIZE - self.image.get_height())//2)

        self.hImageRect.center = self.vImageRect.center = self.rect.center

    def draw(self, window):
        """Desenha o navio na tela"""
        window.blit(self.image, self.rect)
        pygame.draw.rect(window, (255, 0, 0), self.rect, 1) #cobtorno vermelho
        for guns in self.gunlist:
            guns.draw(window, self)

class Guns:
    def __init__(self, imgPath, pos, size, offset):
        self.orig_image = loadImage(imgPath, size, True)
        self.image = self.orig_image
        self.offset = offset
        self.rect = self.image.get_rect(center=pos)
        
    def update(self, ship):
        """Atualizando a Posição das Armas no barco"""
        self.rotateGuns(ship)
        
        if ship.rotation == False:
            self.rect.center = (ship.rect.centerx, ship.rect.centery + (ship.image.get_height()//2 * self.offset))
        else:
            self.rect.center = (ship.rect.centerx + (ship.image.get_width()//2 * -self.offset), ship.rect.centery)

    def _update_image(self, angle):
        self.image = pygame.transform.rotate(self.orig_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)


    def rotateGuns(self, ship):
        """rotaciona a arma em relação a direção do mouse"""
        direction = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.rect.center)
        radius, angle = direction.as_polar()
        if not ship.rotation:
            if self.rect.centery <= ship.vImageRect.centery and angle <= 0:
                self._update_image(angle)
            if self.rect.centery >= ship.vImageRect.centery and angle > 0:
                self._update_image(angle)
        else:
            if self.rect.centerx <= ship.hImageRect.centerx and (angle <= -90 or angle >= 90):
                self._update_image(angle)
            if self.rect.centerx >= ship.hImageRect.centerx and (angle >= -90 and angle <= 90):
                self._update_image(angle)


    def draw(self, window, ship):
        '''Desenha a arma na tela'''
        self.update(ship)
        window.blit(self.image, self.rect)

class Button:
    def __init__(self, image, size, pos, msg):
        self.name = msg
        self.image = image
        self.imageLarger = self.image
        self.imageLarger = pygame.transform.scale(self.imageLarger, (size[0] + 10, size[1] + 10))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.radarUsed = 0
        self.active = False

        self.msg = self.addText(msg)
        self.msgRect = self.msg.get_rect(center=self.rect.center)
        
    def addText(self, msg):
        """Adicionando a fonte para a imagem do botão"""
        font = pygame.font.SysFont('Stencil', 22)
        message = font.render(msg, 1, (255,255,255))
        return message
     
    def focusOnButton(self, window):
        """Trazendo atenção ao botão que está em foco"""
        if self.active:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                window.blit(self.imageLarger, (self.rect[0] - 5, self.rect[1] - 5, self.rect[2], self.rect[3]))
            else:
                window.blit(self.image, self.rect)
                
    
                
    def actionOnPress(self):
        """Quais ações são tomadas de acordo com o botão pressionado"""
        if self.active:
            if self.name == 'Randomize':
                self.randomizeShipPositions(pFleet, pGameGrid)
                self.randomizeShipPositions(p2Fleet, p2GameGrid)
            elif self.name == 'Reset':
                self.resetShips(pFleet)
            elif self.name == 'Deploy':
                self.deploymentPhase()
            elif self.name == 'Quit':
                pass
            elif self.name == 'Redeploy':
                self.restartTheGame()
    
    def randomizeShipPositions(self, shiplist, gameGrid):
        """Chama a função de randomizar os navios"""
        if DEPLOYMENT == True:
            randomizeShipPositions(shiplist, gameGrid)
        
    def resetShips(self, shiplist):
        """Reseta os navios para suas posições inicias"""
        if DEPLOYMENT == True:
            for ship in shiplist:
                ship.returnToDefaultPosition()
                
    def deploymentPhase(self):
        pass

    def restartTheGame(self):
        TOKENS.clear()
        self.resetShips(pFleet)
        self.randomizeShipPositions(p2Fleet, p2GameGrid)
        updateGameLogic(p2GameGrid, p2Fleet, p2GameLogic)
        updateGameLogic(pGameGrid, pFleet, pGameLogic)
        
    def updateButtons(self, Gametatus):
        """Atualiza os botoes por estagio do jogo"""
        if self.name == 'Deploy' and Gametatus == False:
            self.name = 'Redeploy'
        elif self.name == 'Redeploy' and Gametatus == True:
            self.name = 'Deploy'
        if self.name == 'Reset' and Gametatus == False:
            self.name = 'Radar Scan'
        elif self.name == 'Radar Scan' and Gametatus == True:
            self.name = 'Reset'
        if self.name == 'Randomize' and Gametatus == False:
            self.name = 'Quit'
        elif self.name == 'Quit' and Gametatus == True:
            self.name = 'Randomize'
        self.msg = self.addText(self.name)
        self.msgRect = self.msg.get_rect(center=self.rect.center)
    
    def draw(self, window):
        self.updateButtons(DEPLOYMENT)
        self.focusOnButton(window)
        window.blit(self.msg, self.msgRect)

class Player:
    def __init__(self):
        self.turn = True
        
    def makeAttack(self, grid, logicgrid):
        """Quando é a vez do jogador, ele deve fazer uma seleção de ataque dentro do grid do outro jogador"""
        posX, posY = pygame.mouse.get_pos()
        if posX >= grid[0][0][0] and posX <= grid[0][-1][0] + 50 and posY >= grid[0][0][1] and posY <= grid[-1][0][1] + 50:
            for i, rowX in enumerate(grid):
                for j, colX in enumerate(rowX):
                    if posX >= colX[0] and posX < colX[0] + 50 and posY >= colX[1] and posY <= colX[1] + 50:
                        if logicgrid[i][j] != ' ':
                            if logicgrid[i][j] == 'O':
                                TOKENS.append(Tokens(REDTOKEN, grid[i][j], 'Hit', None, None, None))
                                logicgrid[i][j] = 'T'
                                SHOTSOUND.play()
                                HITSOUND.play()
                                self.turn = False
                        else:
                            logicgrid[i][j] = 'X'
                            SHOTSOUND.play()
                            MISSSOUND.play()
                            TOKENS.append(Tokens(GREENTOKEN, grid[i][j], 'Miss', None, None, None))
                            self.turn = False

class EasyComputer:
    def __init__(self):
        self.turn = False
        self.status = self.computerStatus('Thinking')
        self.name = 'Easy Computer'


    def computerStatus(self, msg):
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message


    def makeAttack(self, gamelogic):
        COMPTURNTIMER = pygame.time.get_ticks()
        if COMPTURNTIMER - TURNTIMER >= 3000:
            validChoice = False
            while not validChoice:
                rowX = random.randint(0, 9)
                colX = random.randint(0, 9)

                if gamelogic[rowX][colX] == ' ' or gamelogic[rowX][colX] == 'O':
                    validChoice = True

            if gamelogic[rowX][colX] == 'O':
                TOKENS.append(Tokens(REDTOKEN, pGameGrid[rowX][colX], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                gamelogic[rowX][colX] = 'T'
                SHOTSOUND.play()
                HITSOUND.play()
                self.turn = False
            else:
                gamelogic[rowX][colX] = 'X'
                TOKENS.append(Tokens(BLUETOKEN, pGameGrid[rowX][colX], 'Miss', None, None, None))
                SHOTSOUND.play()
                MISSSOUND.play()
                self.turn = False
        return self.turn


    def draw(self, window):
        if self.turn:
            window.blit(self.status, (p2GameGrid[0][0][0] - CELLSIZE, p2GameGrid[-1][-1][1] + CELLSIZE))

class Tokens:
    def __init__(self, image, pos, action, imageList=None, explosionList=None, soundFile=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        self.imageList = imageList
        self.explosionList = explosionList
        self.action = action
        self.soundFile = soundFile
        self.timer = pygame.time.get_ticks()
        self.imageIndex = 0
        self.explosionIndex = 0
        self.explosion = False
        
    def animate_Explosion(self):
        """Animando a sequencia de explosoes"""
        self.explosionIndex += 1
        if self.explosionIndex < len(self.explosionList):
            return self.explosionList[self.explosionIndex]
        else:
            return self.animate_fire()
        
    def animate_fire(self):
        """Animando a sequencia de fogos"""
        if pygame.time.get_ticks() - self.timer >= 100:
            self.timer = pygame.time.get_ticks()
            self.imageIndex += 1
        if self.imageIndex < len(self.imageList):
            return self.imageList[self.imageIndex]
        else:
            self.imageIndex = 0
            return self.imageList[self.imageIndex]
        
    def draw(self, window):
        """Desenhando os tokens na tela"""
        if not self.imageList:
            window.blit(self.image, self.rect)
        else:
            self.image = self.animate_Explosion()
            self.rect = self.image.get_rect(topleft=self.pos)
            self.rect[1] = self.pos[1] - 10
            window.blit(self.image, self.rect)

# Game Utility Functions
def createGameGrid(rows, cols, cellsize, position):
    """Criar o grid do jogo com as coordenadas de cada célula"""
    startX = position[0]
    startY = position[1]
    coordGrid = []
    for rows in range(rows):
        rowX = []
        for col in range (cols):
            rowX.append((startX, startY))
            startX += cellsize
        coordGrid.append(rowX)
        startX = position[0]
        startY += cellsize
    return coordGrid

def createGameLogic(rows , cols):
    """Atualizando o grid do jogo """
    gamelogic = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append(' ')
        gamelogic.append(rowX)
    return gamelogic

def updateGameLogic(coordGrid, shiplist, gamelogic):
    """Atualizando o grid do jogo com a posição dos navios"""
    for i, rowX in enumerate(coordGrid):
        for j, colX in enumerate(rowX):
            if gamelogic[i][j] == 'T' or gamelogic[i][j] == 'X':
                continue
            else:
                gamelogic[i][j] = ' '
                for ship in shiplist:
                    if pygame.rect.Rect(colX[0], colX[1], CELLSIZE, CELLSIZE).colliderect(ship.rect):
                        gamelogic[i][j] = 'O'

def showGridOnScreen(window, cellsize, playerGrid, player2Grid):
    """Desenhar o grid do player 1 e do player 2 na tela"""
    gamegrids = [playerGrid, player2Grid]
    for grid in gamegrids:
        for row in grid:
            for col in row:
                pygame.draw.rect(window, (255, 255, 255), (col[0], col[1], cellsize, cellsize), 1)

def printGameLogic():
    """Print para o terminal a logica do jogo"""
    print('Player Grid'.center(50, '#'))
    for _ in pGameLogic:
        print(_)
    print('Player2 Grid'.center(50, '#'))
    for _ in p2GameLogic:
        print(_)
 
def loadImage(path, size, rotate=False):
    """Uma função para importar as imagens"""
    img = pygame.image.load(path).convert_alpha() # Carrega a imagem a partir do caminho fornecido
    img = pygame.transform.scale(img, size) # Redimensiona a imagem para o tamanho desejado
    if rotate == True:
        img = pygame.transform.rotate(img, -90)
    return img

def loadAnimationImages(path, aniNum, size):
    """Carregando um número estipulado de imagens a sua memoria"""
    imageList = []
    for num in range(aniNum):
        if num < 10:
            imageList.append(loadImage(f'{path}00{num}.png', size))
        elif num < 100:
            imageList.append(loadImage(f'{path}0{num}.png', size))
        else:
            imageList.append(loadImage(f'{path}{num}.png', size))
    return imageList

def loadSpriteSheetImages(spriteSheet, rows, cols, newSize, size):
    image = pygame.Surface((128, 128))
    image.blit(spriteSheet, (0, 0), (rows * size[0], cols * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, (newSize[0], newSize[1]))
    image.set_colorkey((0, 0, 0))
    return image

def increaseAnimationImage(imageList, ind):
    return imageList[ind]

def createFleet():
    """Criando a embarcação de navios"""
    fleet = []
    for name in FLEET.keys():
        fleet.append(
            Ship(name,
                 FLEET[name][1],
                 FLEET[name][2],
                 FLEET[name][3],
                 FLEET[name][4],
                 FLEET[name][5],
                 FLEET[name][6],
                 FLEET[name][7])
        )
    return fleet
    
def sortFleet(ship, shiplist):
        '''reorganiza a lista de navios'''        
        shiplist.remove(ship)
        shiplist.append(ship)    
    
def randomizeShipPositions(shiplist, gamegrid):
    """Selecionar localizações aleatorias no grid"""
    placedShips = []
    for i, ship in enumerate(shiplist):
        validPosition = False
        while validPosition == False:
            ship.returnToDefaultPosition()
            rotateShip = random.choice([True, False])
            if rotateShip == True:
                yAxis = random.randint(0, 9)
                xAxis = random.randint(0, 9 - (ship.hImage.get_width()//50))
                ship.rotateShip(True)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            else:
                yAxis = random.randint(0, 9 - (ship.vImage.get_height()//50))
                xAxis = random.randint(0, 9)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            if len(placedShips) > 0:
                for item in placedShips:
                    if ship.rect.colliderect(item.rect):
                        validPosition = False
                        break
                    else:
                        validPosition = True
            else:
                validPosition = True
        placedShips.append(ship)

def deploymentPhase(deployment):
    if deployment == True:
        return False
    else:
        return True

def pick_random_ship_location(gameLogic):
    validChoice = False
    while not validChoice:
        posX = random.randint(0, 9)
        posY = random.randint(0, 9)
        if gameLogic[posX][posY] == 'O':
            validChoice = True

    return (posX, posY)

def displayRadarScanner(imagelist, indnum, SCANNER):
    if SCANNER == True and indnum <= 359:
        image = increaseAnimationImage(imagelist, indnum)
        return image
    else:
        return False

def displayRadarBlip(num, position):
    if SCANNER:
        image = None
        if position[0] >= 5 and position[1] >= 5:
            if num >= 0 and num <= 90:
                image = increaseAnimationImage(RADARBLIPIMAGES, num // 10)
        elif position[0] < 5 and position[1] >= 5:
            if num > 270 and num <= 360:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 4) // 10)
        elif position[0] < 5 and position[1] < 5:
            if num > 180 and num <= 270:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 3) // 10)
        elif position[0] >= 5 and position[1] < 5:
            if num > 90 and num <= 180:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 2) // 10)
        return image

def takeTurns(p1, p2):
    if p1.turn == True:
        p2.turn = False
    else:
        p2.turn = True
        if not p2.makeAttack(pGameLogic):
            p1.turn = True

def checkForWinners(grid):
    validGame = True
    for row in grid:
        if 'O' in row:
            validGame = False
    return validGame

def shipLabelMaker(msg):
    """Faz com que as etiquetas do navio sejam exibidas na tela"""
    textMessage = pygame.font.SysFont('Stencil', 22)
    textMessage = textMessage.render(msg, 1, (0, 17, 167))
    textMessage = pygame.transform.rotate(textMessage, 90)
    return textMessage

def displayShipNames(window):
    """Exibindo as etiquetas do navio na tela nas posições corretas"""
    shipLabels = []
    for ship in ['carrier', 'battleship', 'cruiser', 'destroyer', 'submarine', 'patrol boat', 'rescue boat']:
        shipLabels.append(shipLabelMaker(ship))
    startPos = 25
    for item in shipLabels:
        window.blit(item, (startPos, 600))
        startPos += 75

def mainMenuScreen(window):
    window.fill((0, 0, 0))
    window.blit(MAINMENUIMAGE, (0, 0))

    for button in BUTTONS:
        if button.name in ['Jogar']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

def deploymentScreen(window):
    window.fill((0, 0, 0))

    window.blit(BACKGROUND, (0, 0))
    window.blit(PGAMEGRIDIMG, (0, 0))
    window.blit(p2GameGridIMG, (p2GameGrid[0][0][0] - 50, p2GameGrid[0][0][1] - 50))

    #  Desenha os grids dos jogadores na tela
    # showGridOnScreen(window, CELLSIZE, pGameGrid, p2GameGrid)

    #  Desenha os navios na tela
    for ship in pFleet:
        ship.draw(window)
        ship.snapToGridEdge(pGameGrid)
        ship.snapToGrid(pGameGrid)

    displayShipNames(window)

    for ship in p2Fleet:
        # ship.draw(window)
        ship.snapToGridEdge(p2GameGrid)
        ship.snapToGrid(p2GameGrid)

    for button in BUTTONS:
        if button.name in ['Randomize', 'Reset', 'Deploy', 'Quit', 'Radar Scan', 'Redeploy']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

    player2.draw(window)

    radarScan = displayRadarScanner(RADARGRIDIMAGES, INDNUM, SCANNER)
    if not radarScan:
        pass
    else:
        window.blit(radarScan, (p2GameGrid[0][0][0], p2GameGrid[0][-1][1]))
        window.blit(RADARGRID, (p2GameGrid[0][0][0], p2GameGrid[0][-1][1]))

    RBlip = displayRadarBlip(INDNUM, BLIPPOSITION)
    if RBlip:
        window.blit(RBlip, (p2GameGrid[BLIPPOSITION[0]][BLIPPOSITION[1]][0],
                            p2GameGrid[BLIPPOSITION[0]][BLIPPOSITION[1]][1]))

    for token in TOKENS:
        token.draw(window)

    updateGameLogic(pGameGrid, pFleet, pGameLogic)
    updateGameLogic(p2GameGrid, p2Fleet, p2GameLogic)

def endScreen(window):
    window.fill((0, 0, 0))

    window.blit(ENDSCREENIMAGE, (0, 0))

    for button in BUTTONS:
        if button.name in ['Jogar','Quit']:
            button.active = True
            button.draw(window)
        else:
            button.active = False

def updateGameScreen(window, GAMESTATE):
    if GAMESTATE == 'Main Menu':
        mainMenuScreen(window)
    elif GAMESTATE == 'Deployment':
        deploymentScreen(window)
    elif GAMESTATE == 'Game Over':
        endScreen(window)

    pygame.display.update()

# Game Settings and Variables
SCREENWIDTH = 1260 # definir largura
SCREENHEIGHT = 960 # definir altura
ROWS = 10 # definir linhas
COLS = 10 # definir colunas
CELLSIZE = 50 # definir tamanha das células
DEPLOYMENT = True
SCANNER = False
INDNUM = 0
BLIPPOSITION = None
TURNTIMER = pygame.time.get_ticks()
GAMESTATE = 'Main Menu'

# Colors

# Pygame Display Initialization
GAMESCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) # inicializando o display
pygame.display.set_caption('Battle Ship') # definindo um nome

# Game Lists/Dictionaries
FLEET = {
    'battleship': ['battleship', 'assets/images/ships/battleship/battleship.png', (125, 600), (40, 195),
                   4, 'assets/images/ships/battleship/battleshipgun.png', (0.4, 0.125), [-0.525, -0.34, 0.67, 0.49]],
    'cruiser': ['cruiser', 'assets/images/ships/cruiser/cruiser.png', (200, 600), (40, 195),
                2, 'assets/images/ships/cruiser/cruisergun.png', (0.4, 0.125), [-0.36, 0.64]],
    'destroyer': ['destroyer', 'assets/images/ships/destroyer/destroyer.png', (275, 600), (30, 145),
                  2, 'assets/images/ships/destroyer/destroyergun.png', (0.5, 0.15), [-0.52, 0.71]],
    'patrol boat': ['patrol boat', 'assets/images/ships/patrol boat/patrol boat.png', (425, 600), (20, 95),
                    0, '', None, None],
    'submarine': ['submarine', 'assets/images/ships/submarine/submarine.png', (350, 600), (30, 145),
                  1, 'assets/images/ships/submarine/submarinegun.png', (0.25, 0.125), [-0.45]],
    'carrier': ['carrier', 'assets/images/ships/carrier/carrier.png', (50, 600), (45, 245),
                0, '', None, None],
    'rescue ship': ['rescue ship', 'assets/images/ships/rescue ship/rescue ship.png', (500, 600), (20, 95),
                    0, '', None, None]
}
STAGE = ['Main Menu', 'Deployment', 'Game Over']
# Loading Game Variables
pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (50, 50)) # Cria a grade de jogos para o jogador 1 (linhas e colunas, tamanho das células, cor de fundo)
pGameLogic = createGameLogic(ROWS, COLS) # Atualiza a lógica do jogo para o jogador 1
pFleet = createFleet()

p2GameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE), 50)) # Cria a grade de jogos para o jogador 2 (linhas e colunas, tamanho das células, cor de fundo)
p2GameLogic = createGameLogic(ROWS, COLS) # Atualiza a lógica do jogo para o jogador 2
p2Fleet = createFleet()
randomizeShipPositions(p2Fleet, p2GameGrid)

printGameLogic()

# Loading Game Sounds and Images
MAINMENUIMAGE = loadImage('assets/images/background/Battleship.jpg', (SCREENWIDTH // 3 * 2, SCREENHEIGHT))
ENDSCREENIMAGE = loadImage('assets/images/background/Carrier.jpg', (SCREENWIDTH, SCREENHEIGHT))
BACKGROUND = loadImage('assets/images/background/gamebg.png', (SCREENWIDTH, SCREENHEIGHT))
PGAMEGRIDIMG = loadImage('assets/images/grids/player_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
p2GameGridIMG = loadImage('assets/images/grids/comp_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
BUTTONIMAGE = loadImage('assets/images/buttons/button.png', (150, 50))
BUTTONIMAGE1 = loadImage('assets/images/buttons/button.png', (250, 100))
BUTTONS = [
    Button(BUTTONIMAGE, (150, 50), (25, 900), 'Randomize'),
    Button(BUTTONIMAGE, (150, 50), (200, 900), 'Reset'),
    Button(BUTTONIMAGE, (150, 50), (375, 900), 'Deploy'),
    Button(BUTTONIMAGE1, (250, 100), (900, SCREENHEIGHT // 2 - 150), 'Jogar'),
]
REDTOKEN = loadImage('assets/images/tokens/redtoken.png', (CELLSIZE, CELLSIZE))
GREENTOKEN = loadImage('assets/images/tokens/greentoken.png', (CELLSIZE, CELLSIZE))
BLUETOKEN = loadImage('assets/images/tokens/bluetoken.png', (CELLSIZE, CELLSIZE))
FIRETOKENIMAGELIST = loadAnimationImages('assets/images/tokens/fireloop/fire1_ ', 13, (CELLSIZE, CELLSIZE))
EXPLOSIONSPRITESHEET = pygame.image.load('assets/images/tokens/explosion/explosion.png').convert_alpha()
EXPLOSIONIMAGELIST = []
for row in range(8):
    for col in range(8):
        EXPLOSIONIMAGELIST.append(loadSpriteSheetImages(EXPLOSIONSPRITESHEET, col, row, (CELLSIZE, CELLSIZE), (128, 128)))
TOKENS = []
RADARGRIDIMAGES = loadAnimationImages('assets/images/radar_base/radar_anim', 360, (ROWS * CELLSIZE, COLS * CELLSIZE))
RADARBLIPIMAGES = loadAnimationImages('assets/images/radar_blip/Blip_', 11, (50, 50))
RADARGRID = loadImage('assets/images/grids/grid_faint.png', ((ROWS) * CELLSIZE, (COLS) * CELLSIZE))
HITSOUND = pygame.mixer.Sound('assets/sounds/explosion.wav')
HITSOUND.set_volume(0.05)
SHOTSOUND = pygame.mixer.Sound('assets/sounds/gunshot.wav')
SHOTSOUND.set_volume(0.05)
MISSSOUND = pygame.mixer.Sound('assets/sounds/splash.wav')
MISSSOUND.set_volume(0.05)

# Initialise Players
player1 = Player()
player2 = EasyComputer()

# Main Game Loop
RUNGAME = True
while RUNGAME:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNGAME = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if DEPLOYMENT == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()):
                            ship.active = True
                            sortFleet(ship, pFleet)
                            ship.selectShipAndMove()

                else:
                    if player1.turn == True:
                        player1.makeAttack(p2GameGrid, p2GameLogic)
                        if player1.turn == False:
                            TURNTIMER = pygame.time.get_ticks()

                for button in BUTTONS:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        if button.name == 'Deploy' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        elif button.name == 'Redeploy' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        elif button.name == 'Quit' and button.active == True:
                            RUNGAME = False
                        elif button.name == 'Radar Scan' and button.active == True:
                            SCANNER = True
                            INDNUM = 0
                            BLIPPOSITION = pick_random_ship_location(p2GameLogic)
                        elif button.name == 'Jogar'  and button.active == True:
                            if button.name == 'Jogar':
                                computer = EasyComputer()
                            if GAMESTATE == 'Game Over':
                                TOKENS.clear()
                                for ship in pFleet:
                                    ship.returnToDefaultPosition()
                                randomizeShipPositions(p2Fleet, p2GameGrid)
                                pGameLogic = createGameLogic(ROWS, COLS)
                                updateGameLogic(pGameGrid, pFleet, pGameLogic)
                                p2GameLogic = createGameLogic(ROWS, COLS)
                                updateGameLogic(p2GameGrid, p2Fleet, p2GameLogic)
                                status = deploymentPhase(DEPLOYMENT)
                                DEPLOYMENT = status
                            GAMESTATE = STAGE[1]
                        button.actionOnPress()


            elif event.button == 2:
                printGameLogic()


            elif event.button == 3:
                if DEPLOYMENT == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()) and not ship.checkForRotateCollisions(pFleet):
                            ship.rotateShip(True)

    updateGameScreen(GAMESCREEN, GAMESTATE)
    if SCANNER == True:
        INDNUM += 1

    if GAMESTATE == 'Deployment' and DEPLOYMENT != True:
        player1Wins = checkForWinners(p2GameLogic)
        player2Wins = checkForWinners(pGameLogic)
        if player1Wins == True or player2Wins == True:
            GAMESTATE = STAGE[2]



    takeTurns(player1, player2)

pygame.quit() # função para sair