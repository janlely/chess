#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import situation as sit
import threading
import rule
import time
import sheetPrinter
import _thread
import netplay
import re
import sys
import iputil

class MainWindow(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.initConstants()
        self.drawBoard()
        self.initPeices()
        self.initButtons()

    def drawBoard(self):
        self.boardImg = ImageTk.PhotoImage(image=Image.open('images/board.png'))
        self.boardLineImg = ImageTk.PhotoImage(image=Image.open('images/boardlines.png'))
        self.centerH = self.boardImg.width() / 2
        self.centerV = self.boardImg.height() / 2
        self.boardCanv = tk.Canvas(self, width=self.boardImg.width(),
                    height=self.boardImg.height())
        self.boardCanv.create_image(0, 0, image=self.boardImg, anchor=tk.NW)
        self.boardCanv.create_image(self.centerH, self.centerV, image=self.boardLineImg)
        self.boardCanv.grid()

    def initPeices(self):
        self.red = []
        self.black = []
        self.black.append(ImageTk.PhotoImage(file='images/heiju.png'))
        self.black.append(ImageTk.PhotoImage(file='images/heima.png'))
        self.black.append(ImageTk.PhotoImage(file='images/heixiang.png'))
        self.black.append(ImageTk.PhotoImage(file='images/heishi.png'))
        self.black.append(ImageTk.PhotoImage(file='images/heijiang.png'))
        self.black.append(ImageTk.PhotoImage(file='images/heipao.png'))
        self.black.append(ImageTk.PhotoImage(file='images/heizu.png'))
        self.red.append(ImageTk.PhotoImage(file='images/hongju.png'))
        self.red.append(ImageTk.PhotoImage(file='images/hongma.png'))
        self.red.append(ImageTk.PhotoImage(file='images/hongxiang.png'))
        self.red.append(ImageTk.PhotoImage(file='images/hongshi.png'))
        self.red.append(ImageTk.PhotoImage(file='images/hongshuai.png'))
        self.red.append(ImageTk.PhotoImage(file='images/hongpao.png'))
        self.red.append(ImageTk.PhotoImage(file='images/hongbin.png'))

    def initButtons(self):
        self.panel = tk.Frame(self, width=560,height=100)
        self.startBtn = tk.Button(self.panel,text='开始',command=self.startSingle)
        self.cancelBtn = tk.Button(self.panel,text='重来',command=self.restart)
        self.giveUpBtn = tk.Button(self.panel,text='认输', command=self.surrender)
        self.netPlayBtn1 =tk.Button(self.panel, text='同网段对战', command=self.createNetGame)
        self.netPlayBtn2 =tk.Button(self.panel, text='跨网段对战', command=self.createNetGame2)
        self.panel.grid()
        self.startBtn.grid(row=0,column=0, sticky=tk.N+tk.W+tk.S+tk.E)
        self.cancelBtn.grid(row=0,column=1,sticky=tk.N+tk.W+tk.S+tk.E)
        self.giveUpBtn.grid(row=0,column=2,sticky=tk.N+tk.W+tk.S+tk.E)
        self.netPlayBtn1.grid(row=0,column=3, sticky=tk.N+tk.W+tk.S+tk.E)
        self.netPlayBtn2.grid(row=0,column=4, sticky=tk.N+tk.W+tk.S+tk.E)

    def surrender(self):
        self.surrenderFrame = tk.Frame(self)
        self.surrenderLabel = tk.Label(self.surrenderFrame, text='Are you sure?')
        self.btnSure = tk.Button(self.surrenderFrame, text='I\'m sure',
                command=self.doSurrender)
        self.btnNo = tk.Button(self.surrenderFrame, text='Not now',
                command=self.noSurrender)
        self.surrenderFrame.place(x=self.centerH, y=self.centerV, anchor=tk.CENTER)
        self.surrenderLabel.pack()
        self.btnSure.pack(side=tk.LEFT)
        self.btnNo.pack(side=tk.LEFT)

    def doSurrender(self):
        params = (self.btnSure, self.btnNo, self.surrenderLabel, self.surrenderFrame)
        _thread.start_new_thread(self.placeForget, (params,))
        if self.playMode == self.NETPLAY:
            self.netplay.sendMsg('surrender')
        self.restart()

    def noSurrender(self):
        params = (self.btnSure, self.btnNo, self.surrenderLabel, self.surrenderFrame)
        _thread.start_new_thread(self.placeForget, (params,))

    def initGame(self):
        self.peiceChoosed = False#has chooesd a peice
        if self.playMode == self.SINGLE:
            self.color = self.RED
        self.situation = sit.Situation()
        self.drawPeices(self.color)

    def startSingle(self):
        self.playMode = self.SINGLE
        self.initGame()
        self.startGame()

    def startGame(self):
        self.boardCanv.bind('<Button-1>', self.onBoardClick)
        self.startBtn.config(state=tk.DISABLED)

    def onBoardClick(self, event):
        print('clicked')
        row = int(round((event.y - self.leftTop[1]) / self.cubeV))
        col = int(round((event.x - self.leftTop[0]) / self.cubeH))
        self.curPlace = (row, col) if self.color == self.RED else (9-row, 8-col)
        #  net play and not your turn
        if self.playMode == self.NETPLAY and self.color != self.situation.getThinker():
            return
        #  no peice choosed when click on space
        if not self.peiceChoosed and not self.matrix[self.curPlace][2]:
            return
        #  choose a peice
        if not self.peiceChoosed:
            #  choose a wrong peice
            if self.situation.get(self.curPlace)[0] != self.situation.getThinker():
                return
            self.curHolding = self.lastHolding = self.matrix[self.curPlace][2]
            self.flickering = True
            self.peiceChoosed = True
            timer = threading.Timer(0.3, self.flicker)
            timer.start()
            self.lastPlace = self.curPlace
        else:
            #  choose the same peice to stop flickering
            if self.curPlace == self.lastPlace:
                self.flickering = False
                self.peiceChoosed = False
            #  choose another peice
            elif self.situation.get(self.curPlace)[0] == self.situation.getThinker():
                self.curHolding = self.matrix[self.curPlace][2]
                self.boardCanv.itemconfig(self.lastHolding, state=tk.NORMAL)
                self.lastHolding = self.curHolding
                self.lastPlace = self.curPlace
            #  move or eat
            else:
                if rule.movable(self.situation, self.lastPlace, self.curPlace):
                    self.makeMovement()
                    self.flickering = False
                    self.peiceChoosed = False
                    if self.playMode == self.NETPLAY:
                        self.tellTheEnemy()
                    #  check if game ended
                    self.whenGameEnd()



    def tellTheEnemy(self):
        start = self.lastPlace
        end = self.curPlace
        if self.playMode == self.NETPLAY:
            operateStr = '%d%d%d%d' % (start[0], start[1], end[0], end[1])
            self.netplay.sendMsg(operateStr)

    def whenGameEnd(self):
        if self.situation.isEnd():
            self.color = 1 - self.color
            winner = self.situation.getWinner()
            if messagebox.askyesno('game over',
                    'winner is ' + 'red' if winner == 1 else + 'next round?'):
                self.restart()
            else:
                self.quit()



    def makeMovement(self):
        start = self.lastPlace
        end = self.curPlace
        #  eating
        if self.matrix[end][2]:
            #  remove from borad
            self.boardCanv.delete(self.matrix[end][2])
        self.boardCanv.move(self.matrix[self.lastPlace][2],
                self.matrix[end][0] - self.matrix[start][0],
                self.matrix[end][1] - self.matrix[start][1])
        self.matrix[end][2] = self.matrix[start][2]
        self.matrix[start][2] = None
        sheetPrinter.printSheet(self.situation, self.lastPlace, self.curPlace)
        self.situation.change(self.lastPlace, self.curPlace)


    def flicker(self):
        while self.flickering:
            self.boardCanv.itemconfig(self.curHolding, state=tk.HIDDEN)
            time.sleep(0.3)
            self.boardCanv.itemconfig(self.curHolding, state=tk.NORMAL)
            time.sleep(0.3)

    def restart(self):
        self.peiceChoosed = False
        self.flickering = False
        self.clearBoard()
        self.initGame()
        self.startGame()

    def createNetGame(self):
        self.inputFrame = tk.Frame(self)
        self.inputLabel = tk.Label(self.inputFrame, text='Enter room password:')
        self.inputBox = tk.Entry(self.inputFrame)
        self.btnOk = tk.Button(self.inputFrame, text='Find Macth', command=self.createOrConnectRoom)
        self.inputBox.focus_set()
        self.inputFrame.place(x=self.centerH, y=self.centerV, anchor=tk.CENTER)
        self.inputLabel.pack()
        self.inputBox.pack()
        self.btnOk.pack()

    def createNetGame2(self):
        self.selectFrarme = tk.Frame(self)
        self.selectLabel = tk.Label(self.selectFrarme, text='As server or client?')
        self.btnServer = tk.Button(self.selectFrarme, text='server', command=self.createRoom)
        self.btnClient = tk.Button(self.selectFrarme, text='client', command=self.connectServer)
        self.selectFrarme.place(x=self.centerH, y=self.centerV, anchor=tk.CENTER)
        self.selectLabel.pack()
        self.btnServer.pack(side=tk.LEFT)
        self.btnClient.pack(side=tk.LEFT)

    def connectServer(self):
        params = (self.btnServer, self.btnClient, self.selectLabel, self.selectFrarme)
        _thread.start_new_thread(self.placeForget, (params,))
        self.inputFrame = tk.Frame(self)
        self.inputLabel = tk.Label(self.inputFrame,
                text='please input IP:port')
        self.inputBox = tk.Entry(self.inputFrame)
        self.btnOk = tk.Button(self.inputFrame, text='Connect',
                command=self.startConnecting)
        self.inputBox.focus_set()
        self.inputFrame.place(x=self.centerH, y=self.centerV, anchor=tk.CENTER)
        self.inputLabel.pack()
        self.inputBox.pack()
        self.btnOk.pack()

    def startConnecting(self):
        addr = self.inputBox.get()
        self.netplay = netplay.NetPlay(int(addr[addr.index(':')+1:]))
        self.color = self.netplay.joinRoomExact(addr[0:addr.index(':')])
        if self.color != 0:
            if messagebox.askyesno('error',
                    'net work error,check your net work configuration'):
                self.quit()
            else:
                self.quit()
        else:
            self.placeForget((self.inputLabel, self.inputBox, self.btnOk, self.inputFrame))
            self.startNetPlay()


    def createRoom(self):
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        else:
            port = 12345
        params = (self.btnServer, self.btnClient, self.selectLabel, self.selectFrarme)
        _thread.start_new_thread(self.placeForget, (params,))
        self.waitFrame = tk.Frame(self)
        self.waitLabel = tk.Label(self.waitFrame, text='waiting for player....')
        self.ipLabel = tk.Label(self.waitFrame,
                text='you ip is: %s port is %s' %(iputil.getip(), port))
        self.waitFrame.place(x=self.centerH,y=self.centerV, anchor=tk.CENTER)
        self.waitLabel.pack()
        self.ipLabel.pack()
        _thread.start_new_thread(self.startServer,())

    def startServer(self):
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        else:
            port = 12345
        self.netplay = netplay.NetPlay(port)
        self.color = self.netplay.createRoomExact()
        if self.color != 1:
            if messagebox.askyesno('error',
                    'net work error,check your net work configuration'):
                self.quit()
            else:
                self.quit()
        else:
            self.placeForget((self.waitLabel, self.ipLabel, self.waitFrame))
            self.startNetPlay()

    def createOrConnectRoom(self):
        self.passwd = self.inputBox.get()
        self.inputBox.pack_forget()
        self.btnOk.pack_forget()
        self.inputLabel.pack_forget()
        self.msgstr = tk.StringVar()
        self.msgstr.set('search for players...')
        self.loadingMsg = tk.Message(self.inputFrame,
            textvariable=self.msgstr,
            width=200)
        self.inputFrame.place(x=self.centerH,y=self.centerV, anchor=tk.CENTER)
        self.loadingMsg.pack()
        _thread.start_new_thread(self.makeConnection, (self.msgstr,self.passwd))

    def makeConnection(self, msgstr, passwd):
        self.netplay = netplay.NetPlay(12345)
        self.color = self.netplay.createConnection(passwd, False)
        if self.color == 0 or self.color == 1:
            #  game will be started soon
            self.loadingMsg.pack_forget()
            self.inputFrame.place_forget()
            self.startNetPlay()
        elif self.color == -1:
            msgstr.set('error find match, check your network config')
        else:
            msgstr.set('')
            self.btnYes = tk.Button(self.inputFrame, text='yes', command=self.recreateNetGame)
            self.btnIgnore = tk.Button(self.inputFrame, text='no',
                    command=self.makeConnectionExact)
            self.inputFrame.place(x=self.centerH,y=self.centerV, anchor=tk.CENTER)
            self.loadingMsg.pack()
            self.btnYes.pack()
            self.btnIgnore.pack()

    def makeConnectionExact(self):
        self.msgstr.set('search for players...')
        params = (self.btnYes, self.btnIgnore)
        _thread.start_new_thread(self.placeForget, (params,))
        self.peiceColor = self.netplay.createConnection(self.passwd, True)
        if self.peiceColor != -1:
            self.loadingMsg.pack_forget()
            self.inputFrame.place_forget()
            self.startNetPlay()
        else:
            self.msgstr.set('error find match, check your network config')

    def startNetPlay(self):
        self.playMode = self.NETPLAY
        self.cancelBtn.config(state=tk.DISABLED)
        self.initGame()
        self.startGame()
        _thread.start_new_thread(self.watchEnemy, ('',))

    def watchEnemy(self, emptyr):
        while not self.situation.isEnd():
            data = self.netplay.recvMsg()
            if re.match('[0-9][0-8][0-9][0-8]', data):
                self.doEnemysDone(data)
            elif data == 'surrender':
                self.enemySurrendered()

    def enemySurrendered(self):
        self.surrenderFrame = tk.Frame(self)
        self.surrenderLabel = tk.Label(self.surrenderFrame, text='The enemy surrendered')
        self.btnGood = tk.Button(self.surrenderFrame, text='Nice',
                command=self.acceptSurrender)
        self.surrenderFrame.place(x=self.centerH, y=self.centerV, anchor=tk.CENTER)
        self.surrenderLabel.pack()
        self.btnGood.pack()

    def acceptSurrender(self):
        params = (self.btnGood, self.surrenderLabel, self.surrenderFrame)
        _thread.start_new_thread(self.placeForget, (params,))
        self.restart()

    def doEnemysDone(self, data):
        self.lastPlace = (int(data[0]), int(data[1]))
        self.curPlace = (int(data[2]), int(data[3]))
        self.makeMovement()
        self.whenGameEnd()

    def placeForget(self, widgets):
        for w in widgets:
            w.place_forget()

    def initConstants(self):
        self.SINGLE = 0
        self.NETPLAY = 1
        self.RED = 1
        self.BLACK = 0

    def drawPeices(self, color):
        self.matrix = {}
        self.leftTop = (self.centerH - self.boardLineImg.width() / 2 ,
            self.centerV - self.boardLineImg.height() / 2)
        self.cubeH = self.boardLineImg.width() / 8
        self.cubeV = self.boardLineImg.height() / 9
        #  init board matrix
        for i in range(10):
            for j in range(9):
                x = self.leftTop[0] + self.cubeH * j
                y = self.leftTop[1] + self.cubeV * i
                self.matrix[(i,j) if color == self.RED else (9-i,8-j)] = [x,y,None]
        for i in range(10):
            for j in range(9):
                x = self.matrix[(i,j)][0]
                y = self.matrix[(i,j)][1]
                if i == 0:
                    self.matrix[(i,j)][2] = self.boardCanv.create_image(x,y,
                            image=self.black[j if j < 5 else 8-j])
                elif i == 9:
                    self.matrix[(i,j)][2] = self.boardCanv.create_image(x,y,
                            image=self.red[j if j < 5 else 8-j])
                elif i == 2 and j in [1,7]:
                    self.matrix[(i,j)][2] = self.boardCanv.create_image(x,y,
                            image=self.black[5])
                elif i == 7 and j in [1,7]:
                    self.matrix[(i,j)][2] = self.boardCanv.create_image(x,y,
                            image=self.red[5])
                elif i == 3 and j in [0,2,4,6,8]:
                    self.matrix[(i,j)][2] = self.boardCanv.create_image(x,y,
                            image=self.black[6])
                elif i == 6 and j in [0,2,4,6,8]:
                    self.matrix[(i,j)][2] = self.boardCanv.create_image(x,y,
                            image=self.red[6])
                else:
                    self.matrix[(i,j)][2] = None


    def clearBoard(self):
        for i in range(10):
            for j in range(9):
                if self.matrix[(i,j)][2]:
                    self.boardCanv.delete(self.matrix[(i,j)][2])



app = MainWindow()
app.master.title('中国象棋')
app.mainloop()
