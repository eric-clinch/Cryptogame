from tkinter import *
import random, string, time, math, threading, socket
from queue import Queue

#taken from http://www.cs.cmu.edu/~112/notes/notes-graphics.html
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

###############################################################################
# HOSTING CODE
###############################################################################

def getCharactersString(data):
    characterStrings = [str(char) for char in data.characters]
    return "^".join(characterStrings)

def startHosting(data):
    host = data.hostIP
    port = data.hostPort
    BACKLOG = 4
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data.server = server
    server.bind((host,port))
    server.listen(BACKLOG)
    print("looking for connection")

    data.clientele = {}
    data.currID = 0
    data.serverChannel = Queue(100)
    threading.Thread(target = serverThread, args = (data,)).start()

    while (data.acceptNewUsers):
        client, address = server.accept()
        print(data.currID)
        
        sendMsg = "UpdateBoard_" + getCharactersString(data)
        client.send(sendMsg.encode())
        data.clientele[data.currID] = client
        print("connection recieved")
        threading.Thread(target = handleClient, 
                    args = (client, data.currID, data)).start()
        data.currID += 1

def getSendMsg(data, msg):
    if(msg == "SendUpdateBoard"): return "UpdateBoard_" + getCharactersString(data)
    if(msg == "SendGiveUp"): return "GiveUp"
    if(msg == "SendReset"): return "Reset"
    if(msg.startswith("Replace")): return msg

def serverThread(data):
    while True:
        msg = data.serverChannel.get(True)
        handleMsg(data, msg)
        sendMsg = getSendMsg(data, msg)
        if(sendMsg):
            for cID in data.clientele:
                data.clientele[cID].send(sendMsg.encode())
        data.serverChannel.task_done()

def handleClient(client, cID, data):
    client.setblocking(1)
    msg = ""
    while True:
        try:
            msg += client.recv(5000).decode("UTF-8")
            print(msg)
            command = msg.split("\n")
            while (len(command) > 0):
                print("Command: ", command)
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                data.serverChannel.put(readyMsg)
                command = msg.split("\n")
                if(command == ['']): command = []
        except:
            data.clientele.pop(cID)
            break

###############################################################################
# CLIENT CODE
###############################################################################

def talkWithServer(data):
    host = data.hostIP
    port = data.hostPort
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data.server = server

    server.connect((host,port))
    print("connected to server")
    server.setblocking(1)
    msg = ""
    command = ""
    while (data.talkWithServer):
        msg += server.recv(50000).decode("UTF-8") + "\n"
        command = msg.split("\n")
        while(len(command) > 1):
            readyMsg = command[0]
            print(readyMsg)
            msg = "\n".join(command[1:])
            data.serverMsg.put(readyMsg)
            command = msg.split("\n")

###############################################################################
# HOST MODE
###############################################################################

def enterHostMode(data):
    data.MODE = "HOST"
    data.userType = "HOST"
    data.acceptNewUsers = True

def HostMultiplayerCryptogram(data):
    data.hostIP = data.HostIPEntry.get()
    data.hostPort = int(data.HostPortEntry.get())
    threading.Thread(target = startHosting, args = (data,)).start()
    enterCryptogramMode(data)

def initHost(data):
    data.HostFont = "Arial 14 bold"
    data.HostLabelY = 25
    data.HostIPEntry = Entry(data.root, width = 50)
    data.HostIPEntryY = 200
    data.HostPortEntry = Entry(data.root, width = 50)
    data.HostPortEntryY = 300

    data.HostEnterGameButtonY = 400
    data.HostEnterGameButtonWidth = 200
    data.HostEnterGameButton = Button(data.root, text = "ENTER GAME",
        font = data.ButtonFont, 
        command = lambda: HostMultiplayerCryptogram(data))

def redrawAllHost(canvas, data):
    canvas.create_text(data.width//2, data.HostIPEntryY - data.HostLabelY,
                font = data.HostFont, text = "Your IP Address (IPv4 Address)")
    canvas.create_window(data.width//2, data.HostIPEntryY, 
                         window = data.HostIPEntry)

    canvas.create_text(data.width//2, data.HostPortEntryY - data.HostLabelY,
                font = data.HostFont, text = "Port of Choice")
    canvas.create_window(data.width//2, data.HostPortEntryY,
                         window = data.HostPortEntry)

    canvas.create_window(data.width//2, data.HostEnterGameButtonY,
        width = data.HostEnterGameButtonWidth,window = data.HostEnterGameButton)

###############################################################################
# JOIN MODE
###############################################################################

def enterJoinMode(data):
    data.MODE = "JOIN"
    data.userType = "JOIN"

def JoinMultiplayerCryptogram(data):
    data.talkWithServer = True
    data.hostIP = data.JoinIPEntry.get()
    data.hostPort = int(data.JoinPortEntry.get())
    data.serverMsg = Queue(100)
    threading.Thread(target = talkWithServer, args = (data,)).start()
    enterCryptogramMode(data)

def initJoin(data):
    data.JoinFont = "Arial 14 bold"
    data.JoinLabelY = 25
    data.JoinIPEntry = Entry(data.root, width = 50)
    data.JoinIPEntryY = 200
    data.JoinPortEntry = Entry(data.root, width = 50)
    data.JoinPortEntryY = 300

    data.JoinEnterGameButtonY = 400
    data.JoinEnterGameButtonWidth = 200
    data.JoinEnterGameButton = Button(data.root, text = "ENTER GAME",
        font = data.ButtonFont,
        command = lambda: JoinMultiplayerCryptogram(data))

def redrawAllJoin(canvas, data):
    canvas.create_text(data.width//2, data.JoinIPEntryY - data.JoinLabelY,
                font = data.JoinFont, text = "Host's IP Address")
    canvas.create_window(data.width//2, data.JoinIPEntryY, 
                         window = data.JoinIPEntry)

    canvas.create_text(data.width//2, data.JoinPortEntryY - data.JoinLabelY,
                font = data.JoinFont, text = "Host's Port")
    canvas.create_window(data.width//2, data.JoinPortEntryY,
                         window = data.JoinPortEntry)

    canvas.create_window(data.width//2, data.JoinEnterGameButtonY,
        width = data.JoinEnterGameButtonWidth,window = data.JoinEnterGameButton)

###############################################################################
# CRYPTOGRAM MODE
###############################################################################

class LetterBox(object):
    filledLetterFont = "Arial 12 bold"
    cryptoLetterFont = "Arial 12"
    def __init__(self, x, y, width, height, letter, filledLetter = None):
        self.filledLetter = filledLetter
        self.cryptoLetter = letter
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.left = x - width//2
        self.right = self.left + width
        self.top = y - height//2
        self.bot = self.top + height
        self.cryptoLetterY = self.bot + height//2
        self.isSelected = False

    def isInside(self, x, y):
        return (self.left <= x <= self.right and self.top <= y <= self.bot)

    def __repr__(self):
        return "LetterBox %s %s %s %s %s %s" % (self.x, self.y, self.width,
                            self.height, self.cryptoLetter, self.filledLetter)

    def draw(self, canvas):
        fill = "yellow" if self.isSelected else None
        canvas.create_rectangle(self.left, self.top, self.right, self.bot, 
                                fill = fill)
        if(self.filledLetter != None):
            canvas.create_text(self.x, self.y, text = self.filledLetter,
                               font = self.filledLetterFont)
        canvas.create_text(self.x, self.cryptoLetterY, text = self.cryptoLetter,
                           font = self.cryptoLetterFont)

class Punctuation(object):
    font = "Arial 14 bold"
    def __init__(self, x, y, symbol):
        self.x, self.y = x, y
        self.symbol = symbol

    def draw(self, canvas):
        canvas.create_text(self.x, self.y, text = self.symbol, font = self.font)

    def __repr__(self):
        return "Punctuation %s %s %s" % (self.x, self.y, self.symbol)

def replaceBoard(data, newCharactersStr):
    newCharactersStr = newCharactersStr.split("^")
    characters = []
    for char in newCharactersStr:
        attributes = char.split(" ")
        if(attributes[0] == "LetterBox"):
            x = int(float(attributes[1]))
            y = int(float(attributes[2]))
            width = float(attributes[3])
            height = float(attributes[4])
            cryptoLetter = attributes[5]
            filledLetter = attributes[6]
            if(filledLetter == "None"): filledLetter = None
            newLetterBox = LetterBox(x, y, width, height, cryptoLetter, 
                                     filledLetter)
            characters.append(newLetterBox)

        elif(attributes[0] == "Punctuation"):
            x = int(float(attributes[1]))
            y = int(float(attributes[2]))
            symbol = attributes[3] if(len(attributes) > 3) else " "
            newPunctuation = Punctuation(x, y, symbol)
            characters.append(newPunctuation)

        else: print("something went wrong")
    data.characters = characters

def replaceCharacter(data, str):
    encryptedLetter = str[0]
    newLetter = str[1]
    if(newLetter == "0"): newLetter = None

    placeLetter(data, newLetter, encryptedLetter)

def getLetter(n):
    return chr(ord('A') + n)

def getTranslator():
    translator = dict()
    alphabet = string.ascii_uppercase
    lettersUsed = set()
    for letter in string.ascii_uppercase:
        n = random.randint(0, len(alphabet) - 1)
        translatedLetter = getLetter(n)
        while(translatedLetter in lettersUsed):
            n = random.randint(0, len(alphabet) - 1)
            translatedLetter = getLetter(n)
        lettersUsed.add(translatedLetter)
        translator[letter] = translatedLetter
    return translator

def getCryptogram(data):
    s = data.sentence
    s = s.lower()
    translator = getTranslator()
    data.translator = translator
    for letter in translator:
        s = s.replace(letter.lower(), translator[letter])
    return s

def getLines(data):
    words = data.cryptogram.split(" ")
    lines = 1
    x = data.leftMargin
    for word in words:
        wordLength = (len(word)-1)*data.boxSeparation + 2*data.boxWidth
        x += wordLength
        if(x > data.rightMargin):
            lines += 1
            x = data.leftMargin + wordLength
    return lines

def getCharacters(data):
    characters = []
    words = data.cryptogram.split(" ")
    yc = data.height//2
    y = yc - (data.lines/2)*data.lineHeight
    x = data.leftMargin

    for word in words:
        wordLength = (len(word)-1)*data.boxSeparation + 2*data.boxWidth
        if(x + wordLength > data.rightMargin):
            y += data.lineHeight
            x = data.leftMargin
        for char in word:
            if(char in data.punctuation):
                P = Punctuation(x,y,char)
                characters.append(P)
            elif(char in string.ascii_letters):
                L  = LetterBox(x, y, data.boxWidth, data.boxHeight, char)
                characters.append(L)
            x += data.boxSeparation
        if(word != words[-1]):
            space = Punctuation(x,y," ")
            characters.append(space)
            x += data.boxSeparation
    return characters

def selectAllLetter(data, selected):
    for character in data.characters:
        if (isinstance(character, LetterBox)):
            character.isSelected = selected == character.cryptoLetter

def placeLetterAndCommunicate(data, letter, cryptoLetter):
    placeLetter(data, letter, cryptoLetter)

    if(letter == None): letter = "0"
    msg = cryptoLetter + letter
    msg = "Replace_" + msg

    if(data.userType == "HOST"):
        data.serverChannel.put(msg)

    if(data.userType == "JOIN"):
        data.server.send(msg.encode())

def placeLetter(data, letter, cryptoLetter):
    data.letterMatches[cryptoLetter] = letter
    for character in data.characters:
        if(isinstance(character, LetterBox)):
            if(character.cryptoLetter == cryptoLetter):
                character.filledLetter = letter

    if(attemptedSolution(data) == data.correctLetters):
        gameWon(data)

def gameWon(data):
    data.won = True
    data.canContinue = True

def attemptedSolution(data):
    solution = ""
    for character in data.characters:
        if(isinstance(character, LetterBox)):
            if(character.filledLetter == None):
                return 0 #there are unfilled boxes
            else: solution += character.filledLetter
    return solution

def drawSentence(canvas, data):
    for character in data.characters:
        character.draw(canvas)

def getCorrectLetters(sentence):
    result = ""
    for char in sentence:
        if(char in string.ascii_letters):
            result += char
    return result

def getUnusedLetters(data):
    result = string.ascii_uppercase
    for letter in string.ascii_uppercase:
        matchedLetter = data.letterMatches[letter]
        if(matchedLetter != None):
            result = result.replace(matchedLetter, "")
    return result

def getReverseTranslator(data):
    reverseTranslator  = dict()
    for letter in data.translator:
        reverseTranslator[data.translator[letter]] = letter
    return reverseTranslator

def fillCorrectLettersAndCommunicate(data):
    fillCorrectLetters(data)

    if(data.userType == "HOST"):
        data.serverChannel.put("SendUpdateBoard")
    elif(data.userType == "JOIN"):
        data.server.send("GiveUp".encode())


def fillCorrectLetters(data):
    reverseTranslator = getReverseTranslator(data)

    for char in data.characters:
        if(isinstance(char, LetterBox)):
            char.filledLetter = reverseTranslator[char.cryptoLetter] 
    data.canContinue = True

def resetLettersAndCommunicate(data):
    resetLetters(data)

    if(data.userType == "HOST"):
        data.serverChannel.put("SendUpdateBoard")
    elif(data.userType == "JOIN"):
        data.server.send("Reset".encode())

def resetLetters(data):
    for letter in string.ascii_uppercase:
        placeLetter(data, None, letter)

def getSentencesList():
    sentencesFile = open("quotes.txt", "r")
    sentences = []
    for line in sentencesFile:
        sentences.append(line)
    return sentences

def initSentence(data):
    data.won = False
    data.canContinue = False
    #data.sentence = "this is a test sentence"
    data.sentence = random.choice(data.sentences)
    data.sentence = data.sentence.upper()
    data.correctLetters = getCorrectLetters(data.sentence)
    data.cryptogram = getCryptogram(data)
    data.lines = getLines(data)
    data.characters = getCharacters(data)
    data.letterMatches = dict()
    for letter in string.ascii_uppercase:
        data.letterMatches[letter] = None
    data.selectedLetter = None
    data.decrypted = False
    if(data.userType == "HOST"):
        data.serverChannel.put("SendUpdateBoard")

def initCrypotgram(data):
    data.sentences = getSentencesList()
    data.CryptogramFont = "Arial 16 bold"
    data.punctuation = ";:,.!'()/?\"-=+*1234567890"
    data.boxWidth = 17
    data.boxSeparation = data.boxWidth * 1.25
    data.boxHeight = data.boxWidth * 1.5
    data.lineHeight = data.boxHeight * 2.3
    data.margin = 80
    data.leftMargin = data.margin
    data.rightMargin = data.width - data.margin
    data.resetButtonY = data.height - 50
    data.resetButtonX = data.width//3
    data.resetButton = Button(data.root, text = "RESET", font = data.ButtonFont,
        command = lambda: resetLettersAndCommunicate(data))
    data.giveUpButtonY = data.resetButtonY
    data.giveUpButtonX = 2*data.width//3
    data.giveUpButton = Button(data.root, text = "GIVE UP", 
        font = data.ButtonFont, 
        command = lambda: fillCorrectLettersAndCommunicate(data))
    data.continueButton = Button(data.root, text = "NEXT CRYPTOGRAM", 
        font = data.ButtonFont, 
        command = lambda: initSentence(data))
    data.topMessageY = 50
    initSentence(data)

def enterCryptogramMode(data):
    data.MODE = "CRYPTOGRAM"

def enterSingleplayerMode(data):
    data.MODE = "CRYPTOGRAM"
    data.userType = "SINGLE"

def keyPressedCryptogram(event, data):
    if(event.keysym in string.ascii_letters and data.selectedLetter != None):
        placeLetterAndCommunicate(data,event.keysym.upper(),data.selectedLetter)
    if(event.keysym == "BackSpace"):
        placeLetterAndCommunicate(data, None, data.selectedLetter)

    if(event.keysym == "quoteleft"):
        fillCorrectLetters(data)

def redrawAllCryptogram(canvas, data):
    drawSentence(canvas, data)

    if(data.won):
        canvas.create_text(data.width//2, data.topMessageY, 
            font = data.CryptogramFont, text = "YOU WON!")
    else: 
        canvas.create_text(data.width//2, data.topMessageY,
                    font = data.CryptogramFont, text = getUnusedLetters(data))

    if(data.canContinue == False):
        canvas.create_window(data.resetButtonX, data.resetButtonY,
                        window = data.resetButton)
        canvas.create_window(data.giveUpButtonX, data.giveUpButtonY, 
                        window = data.giveUpButton)
    elif(data.userType != "JOIN"):
        canvas.create_window(data.width//2, data.giveUpButtonY, 
                         window = data.continueButton)

def mouseMotionCryptogram(event, data):
    selected = None
    for character in data.characters:
        if(isinstance(character, LetterBox)):
            if(character.isInside(event.x, event.y)):
                selected = character.cryptoLetter
                break
    if(selected != data.selectedLetter):
        selectAllLetter(data, selected)
        data.selectedLetter = selected
        return True
    else: return False

def handleMsg(data, msg):
    if(msg.startswith("Send")): return
    if(msg == "GiveUp"): 
        fillCorrectLettersAndCommunicate(data)
        return
    if(msg == "Reset"):
        resetLettersAndCommunicate(data)
        return

    split = msg.split("_")
    msgType = split[0]
    msg = split[1]

    if(msgType == "UpdateBoard"):
        replaceBoard(data, msg)
    elif(msgType == "Replace"):
        replaceCharacter(data, msg)

def timerFiredCryptogram(data):
    if(data.userType == "JOIN" and data.serverMsg.qsize() > 0):
        msg = data.serverMsg.get(False)
        handleMsg(data, msg)
        data.serverMsg.task_done()

###############################################################################
# HOME PAGE (HOST OR JOIN)
###############################################################################

def enterHostJoinMode(data):
    data.MODE = "HOSTJOIN"

def initHostJoin(data):
    data.HostChoiceButtonY = data.height//2
    data.HostChoiceButtonWidth = 250
    data.HostChoiceButton = Button(data.root, text = "HOST A GAME",
        font = data.ButtonFont, command = lambda: enterHostMode(data))
    data.JoinChoiceButtonY = data.HostChoiceButtonY + 100
    data.JoinChoiceButtonWidth = 250
    data.JoinChoiceButton = Button(data.root, text = "JOIN A GAME",
        font = data.ButtonFont, command = lambda: enterJoinMode(data))

def redrawAllHostJoin(canvas, data):
    canvas.create_window(data.width//2, data.HostChoiceButtonY,
            width = data.HostChoiceButtonWidth, window = data.HostChoiceButton)
    canvas.create_window(data.width//2, data.JoinChoiceButtonY,
            width = data.JoinChoiceButtonWidth, window = data.JoinChoiceButton)

###############################################################################
# HOME PAGE (SINGLE OR MULTIPLAYER)
###############################################################################

def initSingMult(data):
    data.MultiplayerButtonY = data.height//2
    data.MultiplayerButtonWidth = 300
    data.MultiplayerButton = Button(data.root, text = "MULTIPLAYER",
        font = data.ButtonFont, command = lambda: enterHostJoinMode(data))

    data.SingleplayerButtonY = data.MultiplayerButtonY + 100
    data.SingleplayerButtonWidth = 300
    data.SingleplayerButton = Button (data.root, text = "SINGLE PLAYER",
        font = data.ButtonFont, command = lambda: enterSingleplayerMode(data))

    data.optionsButtonY = data.SingleplayerButtonY + 100
    data.optionsButtonWidth = 200
    data.optionsButton = Button(data.root, text = "OPTIONS",
        font = data.ButtonFont, command = lambda: enterOptionsMode(data))

def redrawAllSingMult(canvas, data):
    drawTitle(canvas, data)

    canvas.create_window(data.width//2, data.MultiplayerButtonY,
        width = data.MultiplayerButtonWidth, window = data.MultiplayerButton)
    canvas.create_window(data.width//2, data.SingleplayerButtonY,
        width = data.SingleplayerButtonWidth, window = data.SingleplayerButton)
    canvas.create_window(data.width//2, data.optionsButtonY,
        width = data.optionsButtonWidth, window = data.optionsButton)

###############################################################################
# OPTIONS MODE
###############################################################################

def enterOptionsMode(data):
    data.MODE = "OPTIONS"

def initOptions(data):
    data.userNameEntryY = 50
    data.userNameEntry = Entry(data.root, width = 50)

def redrawAllOptions(canvas,data):
    canvas.create_window(data.width//2, data.userNameEntryY, 
                         window = data.userNameEntry)

###############################################################################
# GENERAL UI CODE
###############################################################################

def drawTitle(canvas, data):
    canvas.create_text(data.width//2, data.titleY, font = data.titleFont,
                         text = data.title)

def init(data):
    data.backgroundColor = rgbString(219, 190, 122)
    data.ButtonFont = "Arial 20"
    data.titleY = 150
    data.title = "CRYPTOGAME"
    data.titleFont = "Arial 26 bold"

    data.MODE = "SINGMULT"
    data.userType = "SINGLE"
    initCrypotgram(data)
    initSingMult(data)
    initHostJoin(data)
    initHost(data)
    initJoin(data)
    initOptions(data)

def mousePressed(event, data):
    # use event.x and event.y
    pass

def mouseMotion(event, data):
    if(data.MODE == "CRYPTOGRAM"): mouseMotionCryptogram(event, data)

def keyPressed(event, data):
    if(event.keysym == "Escape"): data.MODE = "SINGMULT"
    elif(data.MODE == "CRYPTOGRAM"): keyPressedCryptogram(event, data)

def timerFired(data):
    if(data.MODE == "CRYPTOGRAM"): timerFiredCryptogram(data)

def redrawAll(canvas, data):
    canvas.create_rectangle(0,0,data.width + 100, data.height + 100,
                            fill = data.backgroundColor)
    if(data.MODE == "CRYPTOGRAM"): redrawAllCryptogram(canvas, data)
    if(data.MODE == "HOSTJOIN"): redrawAllHostJoin(canvas, data)
    if(data.MODE == "HOST"): redrawAllHost(canvas, data)
    if(data.MODE == "JOIN"): redrawAllJoin(canvas, data)
    if(data.MODE == "SINGMULT"): redrawAllSingMult(canvas, data)
    if(data.MODE == "OPTIONS"): redrawAllOptions(canvas, data)

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def mouseMotionWrapper(event, canvas, data):
    #it would be crazy to redraw everything every time there was a mouse motion
    #so instead, the mouseMotion function will return whether the screen needs
    #to be redrawn or not
        if(mouseMotion(event, data)):
            redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    # create the root and the canvas
    root = Tk()
    data.root = root
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()

    init(data)
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    root.bind("<Motion>", lambda event:
                            mouseMotionWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1200, 700)