from random import randrange

path ='./0'

class Player :
    def __init__(self):
        self.position = '0'
        self.status = 'suspect'

    def update(self, position, status):
        self.position = position
        self.status = status

class PlayerList :
    def __init__(self):
        self.colorList = ['gris', 'blanc', 'bleu', 'rouge', 'marron', 'noir', 'rose', 'violet']
        for x in self.colorList:
            setattr(self, x, Player())

    def changePlayerPlace(self, color, position, status):
        getattr(self, color).update(position, status)

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
    #print(str)
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

def info(lines, info) :
    if (len(lines) > 0):
        lines = lines.strip()
        for line in lines.split('\n') :
            if "Le fantôme est : " in line :
                info.setGhost(line.strip().split(':')[1].strip())
            elif "Tour:" in line:
                defineInfoTour(line.strip(), info)
            elif all(x in line for x in info.playerList.colorList):
                updatePlayerPosition(info, line)
    return


def updatePlayerPosition(info, line):
    for x in line.split('  '):
        tmp = x.split('-')
        info.playerList.changePlayerPlace(tmp[0], tmp[1], tmp[2])


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

def randomResponseTuiles(array) :
    lg = len(array)
    rd = randrange(lg)
    response = str(rd)
    sendResponse(response)
    characterPlayed = array[rd].split('-')[0]
    return characterPlayed;

def randomResponsePossibility(array) :
    lg = len(array)
    response = array[randrange(lg)].strip()
    sendResponse(response)

def powerResponseRandom(nb) :
    response = str(randrange(nb))
    sendResponse(response)


def extractTuile(string):
    question = string.split('[')[1].split(']')[0]
    return randomResponseTuiles(question.split(','))

def extractPossibilities(string):
    question = string.split('{')[1].split('}')[0]
    randomResponsePossibility(question.split(','))

def purpleResponseRandom() :
    pos = ['gris', 'blanc', 'bleu', 'rouge', 'marron', 'noir', 'rose']
    sendResponse(pos[randrange(7)])

def questionParser(question, old_question, info) :
    if question != old_question and len(question) > 0:
        if  question.count('[') > 0:
            info.changeCharacter(extractTuile(question))
        elif  question.count('{') > 0:
            extractPossibilities(question)
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
    while not fini:
        qf = open(path + '/questions.txt','r')
        question = qf.read()
        qf.close()
        questionParser(question, old_question, infoGlobal)
        old_question = question
        infof = open(path + '/infos.txt','r')
        lines = infof.readlines()
        info(diff(oldLines, lines), infoGlobal)
        oldLines = lines
        infof.close()
        if len(lines) > 0:
            fini = "Score final" in lines[-1]
