from random import randrange
from copy import deepcopy
import time

path ='./0'

permanents, deux, avant, apres = {'rose'}, {'rouge','gris','bleu'}, {'violet','marron'}, {'noir','blanc'}
couleurs = avant | permanents | apres | deux
passages = [{1,4},{0,2},{1,3},{2,7},{0,5,8},{4,6},{5,7},{3,6,9},{4,9},{7,8}]
pass_ext = [{1,4},{0,2,5,7},{1,3,6},{2,7},{0,5,8,9},{4,6,1,8},{5,7,2,9},{3,6,9,1},{4,9,5},{7,8,4,6}]

class Player :
    def __init__(self):
        self.position = 0
        self.status = 'suspect'
        self.power = True

    def update(self, position, status, power):
        self.position = position
        self.status = status
        self.power = power

    def tooglePow(self):
        self.power = not self.power
        return self.power

class PlayerList :
    def __init__(self):
        self.colorList = ['gris', 'blanc', 'bleu', 'rouge', 'marron', 'noir', 'rose', 'violet']
        for x in self.colorList:
            setattr(self, x, Player())

    def changePlayerPlace(self, color, position, status, power):
        getattr(self, color).update(int(position), status, power)

    def getPlayerInfo(self, color):
        p = getattr(self, color)
        return [p.position, p.status, p.power]

    def togglePlayerPow(self, color):
        return getattr(self, color).tooglePow()

    def move(self, color, pos):
        p = getattr(self, color)
        p.update(pos, p.status, p.power)

class InfoGlobal :
    def __init__(self):
        self.characterPlayed = ""
        self.ghost = ""
        self.tour = 0
        self.score = 0
        self.ombre = 0
        self.bloque = {1,2}
        self.playerList = PlayerList()
        self.lastQuestion = ""
        self.lastAnswer = ""
        self.toPlay = []

    def changeCharacter(self, char):
        self.characterPlayed = char

    def getCharacter(self):
        return self.characterPlayed

    def setGhost(self, color):
        self.ghost = color

    def getGhost(self):
        return self.ghost

    def setShadow(self, room):
        self.ombre = room

    def setBloque(self, room, way):
        self.bloque = {room, way}

    def setInfoTour(self, t, s, o, b):
        self.tour = t
        self.score = s
        self.ombre = o
        self.bloque = b

    def getInfo(self):
        return self.tour + " : " + self.score + " : " + self.ombre + " : " + self.bloque

    def setQuestion(self, question):
        self.lastQuestion = question

    def setQuestion(self, answer):
        self.lastAnswer = answer

    def getLastQA(self):
        return [self.lastQuestion, self.lastAnswer]

    def setToPlay(self, toPlay):
        self.toPlay = toPlay

def sendResponse(str):
    #print(str)
    rf = open(path + '/reponses.txt','w')
    rf.write(str)
    rf.close()

def defineInfoTour(line, info):
    array = line.split(':')
    t = array[1].split(',')[0]
    s = array[2].split('/')[0]
    o = int(array[3].split(',')[0])
    b = array[4]
    b2 = {int(b[1]), int(b[4])}
    info.setInfoTour(t,s,o,b2)

def info_parser(lines, info) :
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
        info.playerList.changePlayerPlace(tmp[0], tmp[1], tmp[2], True)


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


def isThisPlayerAlone(array, player, ombre):
    if player[1] == ombre:
        return True
    for p in array:
        if p[0] != player[0] and int(p[1]) == player[1] :
            return False
    return True

def howManySuspectAreAlone(array, ombre):
    res = 0
    for p in array:
        if p[2] == 'suspect' and isThisPlayerAlone(array, p, ombre):
            res = res + 1
    return res

def howManySuspect(array):
    res = 0
    for p in array:
        if p[2] == 'suspect' :
            res = res + 1
    return res

def evalFant(tuiles, idx, info):
    if len(tuiles) == 3:
        tuiles_c = deepcopy(tuiles)
        del tuiles_c[idx]
        return selectTuileFant(tuiles_c, deepcopy(info))
    elif len(tuiles) == 2:
        tuiles_c = deepcopy(tuiles)
        del tuiles_c[idx]
        return selectTuileInsp(tuiles_c, deepcopy(info))
    else:
        playerList = info.playerList
        array = []
        for color in playerList.colorList:
            res = playerList.getPlayerInfo(color)
            res.insert(0, color)
            array.insert(0, res)
        before = howManySuspect(array)
        nohit = howManySuspectAreAlone(array, info.ombre)
        hit = before - nohit
        return hit * 2 - 1 if hit <= nohit else nohit * 2 #basic pondaration if hits and by remaining suspect

def selectPowOpt2Fant(tuiles, idx, info):
    color = tuiles[idx].strip().split('-')[0]
    info.playerList.togglePlayerPow(color)

    if color == "rouge":
        return evalFant(tuiles, idx, info) - 1.5
    # if color == "noir":
    #     for q in party.personnages:
    #         if q.position in {x for x in passages[p.position] if x not in party.bloque or q.position not in party.bloque} :
    #             q.position = p.position
    #             informer("NOUVEAU PLACEMENT : "+str(q))
    # if color == "blanc":
    #     for q in party.personnages:
    #         if q.position == p.position and p != q:
    #             dispo = {x for x in passages[p.position] if x not in party.bloque or q.position not in party.bloque}
    #             w = demander(str(q) + ", positions disponibles : " + str(dispo) + ", choisir la valeur",self)
    #             x = int(w) if w.isnumeric() and int(w) in dispo else dispo.pop()
    #             informer("REPONSE INTERPRETEE : "+str(x))
    #             q.position = x
    #             informer("NOUVEAU PLACEMENT : "+str(q))
    # if color == "violet":
    #     informer("Rappel des positions :\n" + str(party))
    #     co = demander("Avec quelle couleur échanger (pas violet!) ?",self)
    #     if co not in couleurs:
    #         co = "rose"
    #     informer("REPONSE INTERPRETEE : "+co)
    #     q = [x for x in party.personnages if x.couleur == co][0]
    #     p.position, q.position = q.position, p.position
    #     informer("NOUVEAU PLACEMENT : "+str(p))
    # if color == "marron":
    #     return [q for q in party.personnages if p.position == q.position]
    # if color == "gris":
    #
    #     for value in variable:
    #         pass
    #     w = demander("Quelle salle obscurcir ? (0-9)",self)
    #     party.shadow = int(w) if w.isnumeric() and int(w) in range(10) else (0)
    #     informer("REPONSE INTERPRETEE : "+str(party.shadow))
    # if color == "bleu":
    #     w = demander("Quelle salle bloquer ? (0-9)",self)
    #     x = int(w) if w.isnumeric() and int(w) in range(10) else 0
    #     w = demander("Quelle sortie ? Chosir parmi : "+str(passages[x]),self)
    #     y = int(w) if w.isnumeric() and int(w) in passages[x] else passages[x].deepcopy().pop()
    #     informer("REPONSE INTERPRETEE : "+str({x,y}))
    #     party.bloque = {x,y}
    return evalFant(tuiles, idx, info)

def selectPow2Fant(tuiles, idx, info):
    color = tuiles[idx].strip().split('-')[0]
    if color in apres|deux and not info.playerList.getPlayerInfo(color)[2]:
        info2 = deepcopy(info)
        nopow_eval = evalFant(tuiles, idx, info)
        pow_eval = selectPowOpt2Fant(tuiles, idx, info2)
        if pow_eval < nopow_eval:
            return pow_eval
        return nopow_eval
    return evalFant(tuiles, idx, info)

def selectMoveFant(tuiles, idx, info):
    color = tuiles[idx].strip().split('-')[0]
    if color in avant and info.playerList.getPlayerInfo(color)[2]:
        return evalFant(tuiles, idx, info)
    pass_act = pass_ext if color == 'rose' else passages
    plinfo = info.playerList.getPlayerInfo(color)
    position = plinfo[0]
    disp = [x for x in pass_act[position] if position not in info.bloque or x not in info.bloque]

    info_cp = deepcopy(info)
    info_cp.playerList.changePlayerPlace(color, disp[0], plinfo[1], plinfo[2])
    max_scr = selectPow2Fant(tuiles, idx, info_cp)
    max_idx = 0
    for i in range(1, len(disp)):
        info_cp2 = deepcopy(info)
        info_cp2.playerList.changePlayerPlace(color, disp[i], plinfo[1], plinfo[2])
        scr = selectPow2Fant(tuiles, idx, info_cp2)
        if (scr < max_scr):
            max_scr = scr
            max_idx = i
            info_cp = info_cp2
    return max_scr

def selectPowOpt1Fant(tuiles, idx, info):
    return selectMoveFant(tuiles, idx, info)

def selectPow1Fant(tuiles, idx, info):
    color = tuiles[idx].strip().split('-')[0]
    if color in avant|deux:
        info2 = deepcopy(info)
        nopow_eval = selectMoveFant(tuiles, idx, info)
        pow_eval = selectPowOpt1Fant(tuiles, idx, info2)
        if pow_eval < nopow_eval:
            return pow_eval
        return nopow_eval
    return selectMoveFant(tuiles, idx, info)

def selectTuileFant(tuiles, info):
    info_cp = deepcopy(info)
    max_scr = selectPow1Fant(tuiles, 0, info_cp)
    max_idx = 0
    for i in range(1, len(tuiles)):
        info_cp2 = deepcopy(info)
        scr = selectPow1Fant(tuiles, i, info_cp2)
        if (scr < max_scr):
            max_scr = scr
            max_idx = i
            info_cp = info_cp2
    return max_scr

def evalInsp(tuiles, idx, info):
    if len(tuiles) == 4:
        tuiles_c = deepcopy(tuiles)
        del tuiles_c[idx]
        return selectTuileFant(tuiles_c, deepcopy(info))
    elif len(tuiles) == 3:
        tuiles_c = deepcopy(tuiles)
        del tuiles_c[idx]
        return selectTuileInsp(tuiles_c, deepcopy(info))
    elif len(tuiles) == 2:
        tuiles_c = deepcopy(tuiles)
        del tuiles_c[idx]
        return selectTuileFant(tuiles_c, deepcopy(info))
    else:
        playerList = info.playerList
        array = []
        for color in playerList.colorList:
            res = playerList.getPlayerInfo(color)
            res.insert(0, color)
            array.insert(0, res)
        before = howManySuspect(array)
        nohit = howManySuspectAreAlone(array, info.ombre)
        hit = before - nohit
        return hit * 2 - 1 if hit <= nohit else nohit * 2 #basic pondaration if hits and by remaining suspect

def selectPowOpt2Insp(tuiles, idx, info):
    color = tuiles[idx].strip().split('-')[0]
    pos = int(tuiles[idx].strip().split('-')[1])
    info.playerList.togglePlayerPow(color)

    if color == "rouge":
        return evalInsp(tuiles, idx, info) + 1.5

    if color == "noir":
        info_c = deepcopy(info)
        playerList = info_c.playerList
        colorList = info_c.playerList.colorList
        for color_n in colorList:
            info_player = playerList.getPlayerInfo(color_n)
            if info_player[0] in passages[pos]:
                playerList.move(color_n, pos)
        return evalInsp(tuiles, idx, info)

    # if color == "blanc":
    #     for q in party.personnages:
    #         if q.position == p.position and p != q:
    #             dispo = {x for x in passages[p.position] if x not in party.bloque or q.position not in party.bloque}
    #             w = demander(str(q) + ", positions disponibles : " + str(dispo) + ", choisir la valeur",self)
    #             x = int(w) if w.isnumeric() and int(w) in dispo else dispo.pop()
    #             informer("REPONSE INTERPRETEE : "+str(x))
    #             q.position = x
    #             informer("NOUVEAU PLACEMENT : "+str(q))

    if color == 'blanc':
        info_c = deepcopy(info)
        playerList = info_c.playerList
        pos = playerList.getPlayerInfo(color)[0]

    if color == 'violet':
        colorList = info.playerList.colorList
        res = ''
        bEval = evalInsp(tuiles, idx, info)
        for color_n in colorList:
            info_c = deepcopy(info)
            p_info = info_c.playerList.getPlayerInfo(color_n)
            info_c.playerList.move(color_n, pos)
            info_c.playerList.move(color, p_info[0])
            tmp_eval = evalInsp(tuiles, idx, info_c)
            if (tmp_eval > bEval):
                bEval = tmp_eval
                res = color_n
        if (res != ''):
            info.toPlay.append(0)
            info.toPlay.append(res)
        return bEval

    # if color == "marron":
    #     return [q for q in party.personnages if p.position == q.position]
    if color == 'marron':
        bEval = 0
        usePower = 0
        way = -1
        for p in passages[pos]:
            info_c = deepcopy(info)
            playerList = info_c.playerList
            playerList.move(color, p)
            for color_n in playerList.colorList :
                if color_n != color and playerList.getPlayerInfo(color_n)[0] == pos:
                    playerList.move(color_n, p)
            tmp_eval = evalInsp(tuiles, idx, info_c)
            if (tmp_eval > bEval):
                bEval = tmp_eval
                usePower = 1
                way = p
        if (way != -1):
            info.toPlay.append(way)
        info.toPlay.append(usePower)
        return bEval


    if color == 'gris':
        info_c = deepcopy(info)
        bEval = evalInsp(tuiles, idx, info_c)
        bRoom = pos
        for i in range(0,9):
            info_c.setShadow(i)
            if (i != info.ombre):
                tmp_eval = evalInsp(tuiles, idx, info_c)
                if (tmp_eval > bEval):
                    bEval = tmp_eval
                    bRoom = i
        info.toPlay.append(bRoom)
        return bEval

    # if color == "bleu":
    #     w = demander("Quelle salle bloquer ? (0-9)",self)
    #     x = int(w) if w.isnumeric() and int(w) in range(10) else 0
    #     w = demander("Quelle sortie ? Chosir parmi : "+str(passages[x]),self)
    #     y = int(w) if w.isnumeric() and int(w) in passages[x] else passages[x].deepcopy().pop()
    #     informer("REPONSE INTERPRETEE : "+str({x,y}))
    #     party.bloque = {x,y}
    if color == "bleu":
        bEval = -1000
        usePower = 0
        info_c = deepcopy(info)
        room = 0
        way = 0
        for (i, p) in enumerate(passages) :
            for w in p :
                if (i < w):
                    info_c.setBloque(i, w)
                    tmp_eval = evalInsp(tuiles, idx, info_c)
                    if tmp_eval > bEval:
                        bEval = tmp_eval
                        usePower = 1
                        room = i
                        way = w
        info.toPlay.append(room)
        info.toPlay.append(way)

    return evalInsp(tuiles, idx, info)

def selectPow2Insp(tuiles, idx, info):
    color = tuiles[idx].strip().split('-')[0]
    if (color in apres|deux) and (info.playerList.getPlayerInfo(color)[2]):
        info2 = deepcopy(info)
        nopow_eval = evalInsp(tuiles, idx, info)
        pow_eval = selectPowOpt2Insp(tuiles, idx, info2)
        if pow_eval > nopow_eval:
            info.setToPlay(info2.toPlay)
            info.toPlay.append("1")
            return pow_eval
        info.toPlay.append("0")
        return nopow_eval
    return evalInsp(tuiles, idx, info)

def selectMoveInsp(tuiles, idx, info):
    color = tuiles[idx].strip().split('-')[0]
    if color in avant and not info.playerList.getPlayerInfo(color)[2]:
        return evalInsp(tuiles, idx, info)
    pass_act = pass_ext if color == 'rose' else passages
    plinfo = info.playerList.getPlayerInfo(color)
    position = plinfo[0]
    disp = [x for x in pass_act[position] if position not in info.bloque or x not in info.bloque]

    info_cp = deepcopy(info)
    info_cp.playerList.changePlayerPlace(color, disp[0], plinfo[1], plinfo[2])
    max_scr = selectPow2Insp(tuiles, idx, info_cp)
    max_idx = 0
    for i in range(1, len(disp)):
        info_cp2 = deepcopy(info)
        info_cp2.playerList.changePlayerPlace(color, disp[i], plinfo[1], plinfo[2])
        scr = selectPow2Insp(tuiles, idx, info_cp2)
        if (scr > max_scr):
            max_scr = scr
            max_idx = i
            info_cp = info_cp2
    info.setToPlay(info_cp.toPlay)
    info.toPlay.append(disp[max_idx]) ############################################################## CAREFUL, THIS IS THE LABEL, NOT THE ANSWER!!
    return max_scr

def selectPowOpt1Insp(tuiles, idx, info):
    return selectMoveInsp(tuiles, idx, info)

def selectPow1Insp(tuiles, idx, info):
    color = tuiles[idx].strip().split('-')[0]
    if color in avant|deux:
        info2 = deepcopy(info)
        nopow_eval = selectMoveInsp(tuiles, idx, info)
        pow_eval = selectPowOpt1Insp(tuiles, idx, info2)
        if pow_eval > nopow_eval:
            info.setToPlay(info2.toPlay)
            info.toPlay.append("1")
            return pow_eval
        info.toPlay.append("0")
        return nopow_eval
    return selectMoveInsp(tuiles, idx, info)

def selectTuileInsp(tuiles, info):
    info_cp = deepcopy(info)
    max_scr = selectPow1Insp(tuiles, 0, info_cp)
    max_idx = 0
    for i in range(1, len(tuiles)):
        info_cp2 = deepcopy(info)
        scr = selectPow1Insp(tuiles, i, info_cp2)
        if (scr > max_scr):
            max_scr = scr
            max_idx = i
            info_cp = info_cp2
    info.setToPlay(info_cp.toPlay)
    info.toPlay.append(max_idx)
    return max_scr

def randomResponseTuiles(array) :
    evaluated = 0
    infoGlobal.toPlay = []
    lg = len(array)
    selectTuileInsp(array, infoGlobal)
    rd = infoGlobal.toPlay.pop()
    # rd = randrange(lg)
    response = str(rd)
    sendResponse(response)
    characterPlayed = array[rd].split('-')[0]
    return characterPlayed;

def randomResponsePossibility(array) :
    resp = infoGlobal.toPlay.pop()
    # print(array, resp)
    # lg = len(array)
    # response = array[randrange(lg)].strip()
    sendResponse(str(resp))

def powerResponseRandom(question) :
    resp = infoGlobal.toPlay.pop()
    # print(question, resp)
    # response = str(randrange(2))
    sendResponse(str(resp))


def extractTuile(string):
    question = string.split('[')[1].split(']')[0]
    return randomResponseTuiles(question.split(','))

def extractPossibilities(string):
    question = string.split('{')[1].split('}')[0]
    randomResponsePossibility(question.split(','))

def purpleResponseRandom(question) :
    resp = infoGlobal.toPlay.pop()
    # print(question, resp)
    pos = ['gris', 'blanc', 'bleu', 'rouge', 'marron', 'noir', 'rose']
    sendResponse(resp)

def questionParser(question, old_question, info) :
    if question != old_question and len(question) > 0:
        # print(question, infoGlobal.toPlay)
        if  question.count('[') > 0:
            start = time.time()
            play = extractTuile(question)
            info.changeCharacter(play)
            # print(question, play)
            end = time.time()
            print("           ", question, end - start)
        elif  question.count('{') > 0:
            extractPossibilities(question)
        elif "Voulez-vous activer le pouvoir" in question :
            powerResponseRandom(question)
        elif "obscurcir" in question :
            powerResponseRandom(question)
        elif "bloquer" in question :
            powerResponseRandom(question)
        elif "changer" in question :
            purpleResponseRandom(question)
        else :
            # print("Not parsed,", question, infoGlobal.toPlay[-1])
            rf = open(path + '/reponses.txt','w')
            rf.write(str(0))
            rf.close()

infoGlobal = InfoGlobal()
def lancer():
    time.sleep(0.1)
    oldLines =""
    fini = False
    old_question = ""

    while not fini:
        qf = open(path + '/questions.txt','r')
        question = qf.read()
        qf.close()
        questionParser(question, old_question, infoGlobal)
        old_question = question
        infof = open(path + '/infos.txt','r')
        lines = infof.readlines()
        info_parser(diff(oldLines, lines), infoGlobal)
        oldLines = lines
        infof.close()
        if len(lines) > 0:
            fini = "Score final" in lines[-1]
