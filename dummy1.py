from random import randrange
from copy import copy
import time

path ='./1'

class Player :
    def __init__(self):
        self.position = '0'
        self.status = 'suspect'

    def update(self, position, status):
        self.position = position
        self.status = status

    def getStatus(self):
        return self.status

class PlayerList :
    def __init__(self):
        self.colorList = ['gris', 'blanc', 'bleu', 'rouge', 'marron', 'noir', 'rose', 'violet']
        for x in self.colorList:
            setattr(self, x, Player())

    def getColorList(self):
        return self.colorList

    def changePlayerInfo(self, color, position, status):
        getattr(self, color).update(position, status)

    def changePlayerPlace(self, color, position):
        player = getattr(self, color)
        player.update(position, player.getStatus())

    def getPlayerInfo(self, color):
        p = getattr(self, color)
        return [p.position, p.status]

class InfoGlobal :
    def __init__(self):
        self.characterPlayed = ""
        self.ghost = ""
        self.tour = 0
        self.score = 0
        self.ombre = 0
        self.bloque = ""
        self.playerList = PlayerList()
        self.lastQuestion = ""
        self.way = [[1,4], [0,2], [1,3], [2, 7], [1, 5, 8], [4, 6], [5, 7], [3, 6, 9], [4, 9], [7,8]]

    def getPlayerList(self):
        return self.playerList

    def getWay(self, room):
        return self.way[room]

    def setLastQuestion(self, question):
        self.lastQuestion = question

    def getLastQuestion(self):
        return self.lastQuestion

    def changeCharacter(self, char):
        self.characterPlayed = char

    def getCharacter(self):
        return self.characterPlayed

    def setGhost(self, color):
        self.ghost = color

    def getGhost(self):
        return self.ghost

    def setInfoTour(self, t, s, o, b):
        self.tour = t
        self.score = s
        self.ombre = o
        self.bloque = b

    def getInfo(self):
        return self.tour + " : " + self.score + " : " + self.ombre + " : " + self.bloque

def sendResponse(str):
    rf = open(path + '/reponses.txt','w')
    rf.write(str)
    rf.close()

def defineInfoTour(line, info):
    array = line.split(':')
    t = array[1].split(',')[0]
    s = array[2].split('/')[0]
    o = array[3].split(',')[0]
    b = array[4]
    info.setInfoTour(t,s,o,b)

def interpretAnswer(answer, info):
    lastQuestion = info.getLastQuestion()
    if "Tuiles disponibles" in lastQuestion:
        info.changeCharacter(answer.split('-')[0])
    elif "positions disponibles" in lastQuestion:
        info.getPlayerList().changePlayerPlace(info.getCharacter(), answer)

def infoParser(lines, info) :
    if (len(lines) > 0):
        lines = lines.strip()
        for line in lines.split('\n') :
            if "Le fantôme est : " in line :
                info.setGhost(line.strip().split(':')[1].strip())
            elif "Tour:" in line:
                defineInfoTour(line.strip(), info)
            elif all(x in line for x in info.playerList.colorList):
                updatePlayerPosition(info, line)
            elif "QUESTION" in line :
                info.setLastQuestion(line[11:].strip())
            elif "REPONSE INTERPRETEE" in line:
                interpretAnswer(line[22:].strip(), info)

    return


def updatePlayerPosition(info, line):
    for x in line.split('  '):
        tmp = x.split('-')
        info.playerList.changePlayerInfo(tmp[0], tmp[1], tmp[2])


def diff(str1, str2) :
    l1 = len(str1)
    l2 = len(str2)
    res = ""
    x = 0
    while x < l2 :
        if (x >= l1 or str2[x] != str1[x]) :
            res = res + str2[x]
        x = x + 1
    return res

def isThisPlayerAlone(array, player):
    for p in array:
        if p[0] != player[0] and int(p[1]) == player[1] :
            return False
    return True

def howManySuspectAreAlone(array):
    res = 0
    for p in array:
        if p[2] == 'suspect' and isThisPlayerAlone(array, p):
            res = res + 1
    return res

def howManySuspect(array):
    res = 0
    for p in array:
        if p[2] == 'suspect' :
            res = res + 1
    return res

def howManyStillSuspect(info):
    playerList = info.getPlayerList()
    array = []
    ghost = info.getGhost()
    for color in playerList.getColorList():
        res = playerList.getPlayerInfo(color)
        res.insert(0, color)
        if res[0] == ghost:
            ghost = res
        array.insert(0, res)
    gAlone = isThisPlayerAlone(array, ghost)
    sAlone = howManySuspectAreAlone(array)
    if (gAlone):
        return sAlone
    else:
        return howManySuspect(array) - sAlone

def calculBestTuileF(info) :
    i = 1
    info = copy(info)
    player = info.getCharacter()
    playerList = info.getPlayerList()
    playerInfo = playerList.getPlayerInfo(player)
    suspect = 0
    bestRoom = 0
    for way in info.getWay(int(playerInfo[0])):
        playerList.changePlayerPlace(player, way)
        tmp = howManyStillSuspect(info)
        if (tmp > suspect):
            suspect = tmp
            bestRoom = way
    return str(bestRoom)


def randomResponseTuiles(array, info) :
    lg = len(array)
    rd = randrange(lg)
    for i in range(0, lg):
        array[i] = array[i].strip()
    response = str(rd)
    sendResponse(response)
    characterPlayed = array[rd].split('-')[0]
    return characterPlayed

def randomResponsePossibility(array, info) :
    lg = len(array)
    #response = array[randrange(lg)].strip()
    response = calculBestTuileF(info)
    sendResponse(response)

def powerResponseRandom(nb) :
    response = str(randrange(nb))
    sendResponse(response)


def extractTuile(string, info):
    question = string.split('[')[1].split(']')[0]
    return randomResponseTuiles(question.split(','), info)

def extractPossibilities(string, info):
    question = string.split('{')[1].split('}')[0]
    randomResponsePossibility(question.split(','), info)

def purpleResponseRandom() :
    pos = ['gris', 'blanc', 'bleu', 'rouge', 'marron', 'noir', 'rose']
    sendResponse(pos[randrange(7)])

def questionParser(question, old_question, info) :
    if question != old_question and len(question) > 0:
        if  question.count('[') > 0:
            info.changeCharacter(extractTuile(question, info))
        elif  question.count('{') > 0:
            extractPossibilities(question, info)
        elif "Voulez-vous activer le pouvoir" in question :
            powerResponseRandom(2)
        elif "obscurcir" in question :
            powerResponseRandom(10)
        elif "bloquer" in question :
            powerResponseRandom(10)
        elif "changer" in question :
            purpleResponseRandom()
        else :
            rf = open(path + '/reponses.txt','w')
            rf.write(str(0))
            rf.close()

def lancer():
    oldLines =""
    fini = False
    old_question = ""

    infoGlobal = InfoGlobal()
    time.sleep(.05)
    while not fini:
        qf = open(path + '/questions.txt','r')
        question = qf.read()
        qf.close()
        questionParser(question, old_question, infoGlobal)
        old_question = question
        infof = open(path + '/infos.txt','r')
        lines = infof.readlines()
        infoParser(diff(oldLines, lines), infoGlobal)
        oldLines = lines
        infof.close()
        if len(lines) > 0:
            fini = "Score final" in lines[-1]
