from random import randrange

def sendResponse(str):
    rf = open('./1/reponses.txt','w')
    rf.write(str)
    rf.close()

def info(str) :
    if (len(str) > 0) :
        print("/#################/")

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
    response = str(randrange(lg))
    sendResponse(response)

def randomResponsePossibility(array) :
    lg = len(array)
    response = array[randrange(lg)].strip()
    sendResponse(response)

def powerResponseRandom(nb) :
    response = str(randrange(nb))
    sendResponse(response)


def extractTuile(string):
    question = string.split('[')[1].split(']')[0]
    randomResponseTuiles(question.split(','))

def extractPossibilities(string):
    question = string.split('{')[1].split('}')[0]
    randomResponsePossibility(question.split(','))


def questionParser(question, old_question) :
    if question != old_question and len(question) > 0:
        # print(question)
        if  question.count('[') > 0:
            extractTuile(question)
        elif  question.count('{') > 0:
            extractPossibilities(question)
        elif "Voulez-vous activer le pouvoir" in question :
            powerResponseRandom(2)
        elif "obscurcir" in question :
            powerResponseRandom(10)
        elif "bloquer" in question :
            powerResponseRandom(10)
        else :
            rf = open('./1/reponses.txt','w')
            rf.write(str(0))
            rf.close()

def lancer():
    oldLines =""
    fini = False
    old_question = ""
    tmp = []
    while not fini:
        qf = open('./1/questions.txt','r')
        question = qf.read()
        qf.close()
        questionParser(question, old_question)
        old_question = question
        infof = open('./1/infos.txt','r')
        lines = infof.readlines()
        info(diff(oldLines, lines))
        oldLines = lines
        infof.close()
        if len(lines) > 0:
            fini = "Score final" in lines[-1]
