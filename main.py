import pygame
from sys import exit
from pygame.locals import *
from enum import Enum
from pathlib import Path
from os import path, system
from random import randint


class Menus(Enum):
    Main = 1
    Settings = 2
    Game = 3


class Difficulties(Enum):
    Easy = 1
    Medium = 2
    Hard = 3


class Button():
    def __init__(self,
                 surface,
                 position=(10, 10),
                 resolution=(75, 50),
                 function=lambda: print("Hello world!"),
                 text="Button",
                 visibility=True,
                 lightColour=(227, 119, 61),
                 mainColour=(189, 72, 68),
                 darkColour=(133, 53, 80),
                 cooldown=0):

        self.surface = surface
        self.pos = position
        self.res = resolution
        self.width = self.res[0]
        self.height = self.res[1]

        self.function = function
        self.text = text

        self.fontObj = pygame.font.Font(
            path.join(Path(__file__).parent, r"graphic\UI\Pixeltype.ttf"), 50)
        self.rect = pygame.Rect((self.pos), (self.width, self.height))
        self.visibility = visibility
        self.lightCol = lightColour
        self.mainCol = mainColour
        self.darkCol = darkColour

        self.cooldownAnchor = cooldown
        self.cooldownProgress = cooldown
        self.waitForRelease = False

    def update(self, surface, buttonPressed):
        self.rect = pygame.Rect((self.pos), (self.width, self.height))
        if self.cooldownProgress != self.cooldownAnchor:
            self.cooldownProgress += 1

        if buttonPressed == True:
            if self.visibility == True:
                pygame.draw.rect(surface, self.darkCol, self.rect)
            self.waitForRelease = True

        if self.waitForRelease == True and buttonPressed == False:
            self.waitForRelease = False
            if self.cooldownProgress == self.cooldownAnchor:
                self.function()
                self.cooldownProgress = 0

        if self.visibility == True:
            if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                pygame.draw.rect(surface, self.darkCol, self.rect)

            elif self.isHovered == True:
                pygame.draw.rect(surface, self.lightCol, self.rect)
            else:
                pygame.draw.rect(surface, self.mainCol, self.rect)

        if self.visibility == True:
            self.textSurface = self.fontObj.render(self.text, True, (0, 0, 0))
            self.textRect = self.textSurface.get_rect(
                center=((self.width / 2) + self.pos[0], (self.height / 2) + self.pos[1]))
            surface.blit(self.textSurface, self.textRect)


class Ring():
    def __init__(self, visibility, location, angle, torque):
        self.visibility = visibility
        self.location = location
        self.angle = angle
        self.torque = torque
        self.image = pygame.image.load(path.join(
            Path(__file__).parent, r"graphic\UI\selectionRing.png")).convert_alpha()
        self.image = pygame.transform.scale(
            self.image, (self.image.get_width() * 5, self.image.get_height() * 5))
        self.image = pygame.transform.rotate(self.image, angle)

    def animate(self, surf):
        self.angle += self.torque
        rotatedImage = pygame.transform.rotate(self.image, self.angle)
        newRect = rotatedImage.get_rect(
            center=self.image.get_rect(topleft=self.location).center)

        surf.blit(rotatedImage, newRect)


class Selection():
    def __init__(self, surface):
        self.visibility = True
        self.location = (0, 0)
        self.surface = surface

        self.ring = Ring(self.visibility, self.location, 0, 1)
        self.antiRing = Ring(self.visibility, self.location, 180, -1)

    def move(self, coords):
        self.location = coords
        self.ring.location = coords
        self.antiRing.location = coords

    def animate(self):
        if self.visibility == True:
            self.ring.animate(self.surface)
            self.antiRing.animate(self.surface)


class Game():
    def __init__(self, configDict, surface, resolution):
        self.codeLength = configDict["codeLength"]
        self.colourSpectrum = configDict["colourSpectrum"]
        self.gameAttempts = configDict["gameAttempts"]
        self.res = (self.codeLength * 50, self.gameAttempts * 50)
        self.startPos = getCenter(self.res, canvasRes=(resolution))
        self.tile = scaleBy5(loadFile(r"graphic\UI\tile.png"))
        self.grid = [["Blank" for _ in range(
            self.codeLength)] for _ in range(self.gameAttempts)]
        self.selectedRow = self.gameAttempts - 1
        self.fontObj = pygame.font.Font(
            path.join(Path(__file__).parent, r"graphic\UI\Pixeltype.ttf"), 30)

        self.buttons = [_ for _ in range(0, self.codeLength)]
        for i, button in enumerate(self.buttons):
            self.buttons[button] = Button(surface=surface, position=(
                self.startPos[0] + i*50, self.startPos[1] + self.res[1] - 50), resolution=(50, 50), visibility=True, function=lambda i=i: self.mutatePin((i, self.selectedRow), "next"))
        self.tickButton = Button(surface=surface, position=(self.startPos[0] + (self.codeLength * 50) + 25, self.startPos[1] + (
            self.selectedRow * 50)), resolution=(50, 50), visibility=False, function=lambda: self.confirm())

        self.grayPin = scaleBy5(loadFile(r"graphic\UI\grayPin.png"))
        self.redPin = scaleBy5(loadFile(r"graphic\UI\redPin.png"))
        self.greenPin = scaleBy5(loadFile(r"graphic\UI\greenPin.png"))
        self.bluePin = scaleBy5(loadFile(r"graphic\UI\bluePin.png"))
        self.purplePin = scaleBy5(loadFile(r"graphic\UI\purplePin.png"))
        self.tick = scaleBy5(loadFile(r"graphic\UI\tick.png"))

        self.colourOrder = ["Blank", "Red", "Blue",
                            "Green", "Gray", "Purple"][:self.colourSpectrum + 1]
        self.pins = {"Blank": "", "Red": self.redPin, "Gray": self.grayPin,
                     "Green": self.greenPin, "Blue": self.bluePin, "Purple": self.purplePin}

        self.code = [self.colourOrder[1:][randint(
            0, len(self.colourOrder)-2)] for _ in range(self.codeLength)]

        self.Win = False
        self.Loss = False
        self.winText = self.fontObj.render("You won!", True, (105,148,52))
        self.winRect = self.winText.get_rect(center = (resolution[0] - 45, resolution[1] - 80))
        self.lossText = self.fontObj.render("You lost!", True, (227,119,61))
        self.lossRect = self.lossText.get_rect(center = (resolution[0] - 45, resolution[1] - 80))

        print(self.code)

    def confirm(self):
        attempt = self.grid[self.selectedRow]
        if attempt == self.code:
            self.Win = True        
        elif self.selectedRow == 0:
            self.Loss = True
        else:
            self.nextRow()

    def getHints(self, row):
        mutualColours = 0
        matchingColours = 0
        data = [colour for colour in self.grid[row]]
        tempCode = [colour for colour in self.code]
        for index, colour in enumerate(data):
            if colour == tempCode[index]:
                matchingColours += 1
                tempCode[index] = ""
                data[index] = "Blank"
        for index, colour in enumerate(data):
            if colour in tempCode:
                mutualColours += 1
                tempCode[index] = ""

        return (matchingColours, mutualColours)

            
    def mutatePin(self, pos, colour):
        if colour == "next":
            formerColour = self.grid[pos[1]][pos[0]]
            for index, pin in enumerate(self.colourOrder):
                if pin == formerColour:
                    try:
                        self.grid[pos[1]][pos[0]] = self.colourOrder[index + 1]
                    except:
                        self.grid[pos[1]][pos[0]] = self.colourOrder[0]
        else:
            self.grid[pos[1]][pos[0]] = colour

    def update(self, screen, event):
        guiPageUpdate(
            screen, [button for button in self.buttons], event)
        guiPageUpdate(
            screen, [self.tickButton], event)
        
        screen.blit(self.tick, (self.startPos[0] + (
            self.codeLength * 50) + 25, self.startPos[1] + (self.selectedRow * 50)))
        
    def nextRow(self):
        for button in self.buttons:
            button.pos = (button.pos[0], button.pos[1] - 50)
        self.selectedRow -= 1
        self.tickButton.pos = (self.startPos[0] + (self.codeLength * 50) + 25, self.startPos[1] + (
            self.selectedRow * 50))

    def draw(self, display):
        for j in range(self.startPos[1], self.res[1] + self.startPos[1], self.tile.get_height()):
            for i in range(self.startPos[0], self.res[0] + self.startPos[0], self.tile.get_width()):
                display.blit(self.tile, (i, j))
        for j, y in enumerate(self.grid):
            if j > self.selectedRow or self.Loss == True:
                matchingStat, mutualStat = self.getHints(j)
                matchingText = self.fontObj.render("Matching: "+str(matchingStat), True, (105,148,52))
                matchingRect = matchingText.get_rect(topleft = (0, self.startPos[1] + (j*50) + 10))
                mutualText = self.fontObj.render("Mutual: "+str(mutualStat), True, (227,119,61))
                mutualRect = matchingText.get_rect(topleft = (0, self.startPos[1] + (j*50) + 30))
                display.blit(matchingText, matchingRect)
                display.blit(mutualText, mutualRect)
            for i, x in enumerate(self.grid[j]):
                if self.grid[j][i] != "Blank":
                    display.blit(self.pins[self.grid[j][i]], (self.startPos[0] + (i*50) + 15, self.startPos[1] + (j*50) + 15))
            if self.Win == True:
                display.blit(self.winText, self.winRect)
            if self.Loss == True:
                display.blit(self.lossText, self.lossRect)


def guiPageUpdate(screen, buttons, event):
    for button in buttons:
        if button.rect.collidepoint(pygame.mouse.get_pos()):
            button.isHovered = True
        else:
            button.isHovered = False

        if button.isHovered == True and event.type == pygame.MOUSEBUTTONDOWN:
            button.update(screen, buttonPressed=True)
        else:
            button.update(screen, buttonPressed=False)


def difficultySwitch(difficulty, resolution):
    global selectDifficulty
    xButtonCenter = getCenter((65, 65), resolution)[0]
    if difficulty == "Easy":
        globals().update(currentDifficulty=Difficulties.Easy)
        configDict["codeLength"] = 3
        configDict["colourSpectrum"] = 3
        configDict["gameAttempts"] = 8
        selectDifficulty.move((xButtonCenter - 80, 162.5))
    elif difficulty == "Medium":
        globals().update(currentDifficulty=Difficulties.Medium)
        configDict["codeLength"] = 4
        configDict["colourSpectrum"] = 4
        configDict["gameAttempts"] = 10
        selectDifficulty.move((xButtonCenter, 162.5))
    elif difficulty == "Hard":
        globals().update(currentDifficulty=Difficulties.Hard)
        configDict["codeLength"] = 6
        configDict["colourSpectrum"] = 6
        configDict["gameAttempts"] = 12
        selectDifficulty.move((xButtonCenter + 80, 162.5))


def startGame(configDict, surface, resolution):
    globals().update(currentMenu=Menus.Game)
    global board
    board = Game(surface, configDict, resolution)


def getCenter(objRes, canvasRes): return (
    ((canvasRes[0] - objRes[0]) // 2), ((canvasRes[1] - objRes[1]) // 2))


def getImage(filePath): return path.join(Path(__file__).parent, filePath)


def scaleBy5(image): return pygame.transform.scale(
    image, ((image.get_width() * 5), (image.get_height() * 5)))


def loadFile(filePath): return pygame.image.load(
    getImage(filePath)).convert_alpha()


def main():
    pygame.init()
    pygame.font.init()

    resolution = (650, 650)
    screen = pygame.display.set_mode(resolution)
    clock = pygame.time.Clock()

    xButtonCenter = getCenter((65, 65), resolution)[0]
    global selectDifficulty
    selectDifficulty = Selection(screen)

    # Images
    masterMindTitle = scaleBy5(
        loadFile(r"graphic\UI\mastermind - transparent.png"))

    settingsTitle = scaleBy5(loadFile(r"graphic\UI\settingsTitle.png"))
    easySkull = scaleBy5(loadFile(r"graphic\UI\easySkull.png"))
    easyTitle = scaleBy5(loadFile(r"graphic\UI\easy.png"))
    mediumSkull = scaleBy5(loadFile(r"graphic\UI\mediumSkull.png"))
    mediumTitle = scaleBy5(loadFile(r"graphic\UI\medium.png"))
    hardSkull = scaleBy5(loadFile(r"graphic\UI\hardSkull.png"))
    hardTitle = scaleBy5(loadFile(r"graphic\UI\hard.png"))
    retryArrow = scaleBy5(loadFile(r"graphic\UI\retry.png"))
    backArrow = scaleBy5(loadFile(r"graphic\UI\backArrow.png"))

    # States
    global currentMenu
    global currentDifficulty
    currentMenu = Menus.Main
    currentDifficulty = Difficulties.Easy
    # Config
    global configDict
    configDict = {"codeLength": 1, "colourSpectrum": 1, "gameAttempts": 1}
    difficultySwitch("Easy", resolution)

    # Main menu
    genBoard = Button(screen, position=(getCenter((150,75), resolution)[0], 150),
                      resolution=(150, 75), text="Start", function=lambda: startGame(screen, configDict, resolution))
    openSettings = Button(screen, position=(getCenter((150,75), resolution)[0], 235), resolution=(
        150, 75), text="Settings", function=lambda: (globals().update(currentMenu=Menus.Settings)))
    gameQuit = Button(screen, position=(getCenter((150,75), resolution)[0], 320), resolution=(
        150, 75), text="Quit", function=lambda: (pygame.quit(), exit()))
    # Settings menu
    settingsBack = Button(screen, position=(getCenter((120,60), resolution)[0], 335), resolution=(
        120, 60), text="Back", function=lambda: (globals().update(currentMenu=Menus.Main)))
    easyMode = Button(screen, position=(xButtonCenter-80, 165), resolution=(65, 65),
                      visibility=False, function=lambda: difficultySwitch("Easy", resolution))
    mediumMode = Button(screen, position=(xButtonCenter, 165), resolution=(
        65, 65), visibility=False, function=lambda: difficultySwitch("Medium", resolution))
    hardMode = Button(screen, position=(xButtonCenter+80, 165), resolution=(65, 65),
                      visibility=False, function=lambda: difficultySwitch("Hard", resolution))
    backArrowButton = Button(screen, position=(10, 10), resolution=(
        50, 50), visibility=False, function=lambda: (globals().update(currentMenu=Menus.Main)))
    retryButton = Button(screen, position=(resolution[0] - 70, resolution[1] - 70),
                      resolution=(50, 50), text="", visibility=False, function=lambda: startGame(screen, configDict, resolution))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        pygame.draw.rect(screen, (0, 0, 0), ((0, 0), resolution))  # Refresh

        if currentMenu == Menus.Main:
            screen.blit(masterMindTitle, (getCenter(masterMindTitle.get_size(), resolution)[0], 50))
            guiPageUpdate(screen, [genBoard, openSettings, gameQuit], event)

        if currentMenu == Menus.Settings:
            screen.blit(settingsTitle, (getCenter(settingsTitle.get_size(), resolution)[0], 50))
            xSkullCenter = getCenter(easySkull.get_size(), resolution)[0]
            selectDifficulty.animate()

            guiPageUpdate(screen, [settingsBack, easyMode,
                          mediumMode, hardMode], event)
            screen.blit(easySkull, (xSkullCenter - 80, 170))
            screen.blit(mediumSkull, (xSkullCenter, 170))
            screen.blit(hardSkull, (xSkullCenter + 80, 170))

            if currentDifficulty == Difficulties.Easy:
                xEasy = getCenter(easyTitle.get_size(), resolution)[0]
                screen.blit(easyTitle, (xEasy, 245))

            elif currentDifficulty == Difficulties.Medium:
                xMedium = getCenter(mediumTitle.get_size(), resolution)[0]
                screen.blit(mediumTitle, (xMedium, 245))

            elif currentDifficulty == Difficulties.Hard:
                xHard = getCenter(hardTitle.get_size(), resolution)[0]
                screen.blit(hardTitle, (xHard, 245))

        if currentMenu == Menus.Game:
            screen.blit(backArrow, (15, 15))
            guiPageUpdate(screen, [backArrowButton], event)
            board.update(screen, event)
            board.draw(screen)

            if board.Win == True or board.Loss == True:
                guiPageUpdate(screen, [retryButton], event)
                screen.blit(retryArrow, (resolution[0] - 70, resolution[1] - 70))

        clock.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    main()
