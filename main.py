#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import threading,_thread
import time,sched
from PIL import ImageTk, Image
import netplay
import re

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.lock = threading.Lock()
        self.walker = 1
        self.peiceColor = 1
        self.gameEnded = False
        self.isNetPlay = False
        self.peiceHolded = False;
        self.initGame()

    def initGame(self):
        self.initBoard()
        self.initPieces()
        self.initControl()

    def startNetPlay(self):
        self.inputFrame = tk.Frame(self)
        self.inputLabel = tk.Label(self.inputFrame, text='请输入开房密码：')
        self.inputBox = tk.Entry(self.inputFrame)
        self.btnOk = tk.Button(self.inputFrame, text='确定', command=self.createOrConnectRoom)
        self.inputBox.focus_set()
        self.inputFrame.place(x=self.centerH, y=self.centerV, anchor=tk.CENTER)
        self.inputLabel.pack()
        self.inputBox.pack()
        self.btnOk.pack()

    def restartNetPlay(self):
        self.btnYes.pack_forget()
        self.btnIgnore.pack_forget()
        self.loadingMsg.pack_forget()
        self.inputBox.focus_set()
        self.inputFrame.place(x=self.centerH, y=self.centerV, anchor=tk.CENTER)
        self.inputLabel.pack()
        self.inputBox.pack()
        self.btnOk.pack()

    def createOrConnectRoom(self):
        self.passwd = self.inputBox.get()
        self.inputBox.pack_forget()
        self.btnOk.pack_forget()
        self.inputLabel.pack_forget()
        self.msgstr = tk.StringVar()
        self.msgstr.set('寻找游戏中...')
        self.loadingMsg = tk.Message(self.inputFrame,
            textvariable=self.msgstr,
            width=200)
        self.inputFrame.place(x=self.centerH,y=self.centerV, anchor=tk.CENTER)
        self.loadingMsg.pack()
        _thread.start_new_thread(self.makeConnection, (self.msgstr,self.passwd))

    def makeConnection(self, msgstr, passwd):
        self.netplay = netplay.NetPlay(12345)
        self.peiceColor = self.netplay.createConnection(passwd, False)
        if self.peiceColor == 0 or self.peiceColor == 1:
            #  msgstr.set('游戏马上开始')
            self.loadingMsg.pack_forget()
            self.inputFrame.place_forget()
            self.createNetGame()
        elif self.peiceColor == -1:
            msgstr.set('寻找游戏失败，请检查网络配置')
        else:
            msgstr.set('是不是输错密码了？')
            self.btnYes = tk.Button(self.inputFrame, text='是的', command=self.restartNetPlay)
            self.btnIgnore = tk.Button(self.inputFrame, text='没有',
                    command=self.makeConnectionExact)
            self.inputFrame.place(x=self.centerH,y=self.centerV, anchor=tk.CENTER)
            self.loadingMsg.pack()
            self.btnYes.pack()
            self.btnIgnore.pack()

    def makeConnectionExact(self):
        self.msgstr.set('寻找游戏中...')
        _thread.start_new_thread(self.placeForget, ('empty',))
        self.peiceColor = self.netplay.createConnection(self.passwd, True)
        if self.peiceColor != -1:
            self.loadingMsg.pack_forget()
            self.inputFrame.place_forget()
            self.createNetGame()
        else:
            self.msgstr.set('寻找游戏失败,请检查网络配置')

    def placeForget(self, empty):
        self.btnYes.pack_forget()
        self.btnIgnore.pack_forget()

    def createNetGame(self):
        self.isNetPlay = True
        self.start()
        _thread.start_new_thread(self.watchEnemy, ('',))

    def showLoadingMsg(self, msgstr):
        self.inputFrame.place(x=self.centerH,y=self.centerV, anchor=tk.CENTER)
        self.loadingMsg.pack()


    def start(self):
        self.createSingleGame()
        self.boardCanv.bind('<Button-1>', self.onClick)
        self.startBtn.config(state=tk.DISABLED)

    def restart(self):
        self.walker = 1
        self.peiceHolded = False
        self.gameEnded = False
        self.continueFlicker = False
        self.clearBoard()
        self.createSingleGame()

    def initControl(self):
        self.panel = tk.Frame(self, width=560,height=100)
        self.startBtn = tk.Button(self.panel,text='开始',command=self.start)
        self.cancelBtn = tk.Button(self.panel,text='重来',command=self.restart)
        self.netPlayBtn =tk.Button(self.panel, text='局域网对战', command=self.startNetPlay)
        self.panel.grid()
        self.startBtn.grid(row=0,column=0, sticky=tk.N+tk.W+tk.S+tk.E)
        self.cancelBtn.grid(row=0,column=1,sticky=tk.N+tk.W+tk.S+tk.E)
        self.netPlayBtn.grid(row=0,column=2, sticky=tk.N+tk.W+tk.S+tk.E)

    def initBoard(self):

        self.boardImg = ImageTk.PhotoImage(image=Image.open('images/board.png'))
        self.boardLineImg = ImageTk.PhotoImage(image=Image.open('images/boardlines.png'))

        self.centerH = self.boardImg.width() / 2
        self.centerV = self.boardImg.height() / 2
        self.cubeH = self.boardLineImg.width() / 8
        self.cubeV = self.boardLineImg.height() / 9
        self.boardCanv = tk.Canvas(self, width=self.boardImg.width(),
                    height=self.boardImg.height())
        self.boardCanv.create_image(0, 0, image=self.boardImg, anchor=tk.NW)
        self.boardCanv.create_image(self.centerH, self.centerV, image=self.boardLineImg)
        self.boardCanv.grid()

    def initPosition(self):
        self.pos = {}
        self.leftTop = (self.centerH - self.boardLineImg.width() / 2 ,
            self.centerV - self.boardLineImg.height() / 2)
        for i in range(10):
            for j in range(9):
                if self.peiceColor == 1:
                    self.pos[(i,j)] = [self.leftTop[0] + self.cubeH * j,
                        self.leftTop[1] + self.cubeV * i, None, None, None]
                else:
                    self.pos[(9-i,8-j)] = [self.leftTop[0] + self.cubeH * j,
                        self.leftTop[1] + self.cubeV * i, None, None, None]


    def initPieces(self):
        self.peicesB = {1:'车', 2:'马', 3:'象', 4:'士', 5:'将', 6:'砲', 7:'卒'}
        self.peicesR = {1:'车', 2:'马', 3:'相', 4:'仕', 5:'帅', 6:'炮', 7:'兵'}
        self.rb = {0:'黑', 1:'红'}
        '''read peices png file'''
        self.heijuImg = ImageTk.PhotoImage(file='images/heiju.png')
        self.heimaImg = ImageTk.PhotoImage(file='images/heima.png')
        self.heixiangImg = ImageTk.PhotoImage(file='images/heixiang.png')
        self.heishiImg = ImageTk.PhotoImage(file='images/heishi.png')
        self.heijiangImg = ImageTk.PhotoImage(file='images/heijiang.png')
        self.heizuImg = ImageTk.PhotoImage(file='images/heizu.png')
        self.heipaoImg = ImageTk.PhotoImage(file='images/heipao.png')

        self.hongjuImg = ImageTk.PhotoImage(file='images/hongju.png')
        self.hongmaImg = ImageTk.PhotoImage(file='images/hongma.png')
        self.hongxiangImg = ImageTk.PhotoImage(file='images/hongxiang.png')
        self.hongshiImg = ImageTk.PhotoImage(file='images/hongshi.png')
        self.hongshuaiImg = ImageTk.PhotoImage(file='images/hongshuai.png')
        self.hongbinImg = ImageTk.PhotoImage(file='images/hongbin.png')
        self.hongpaoImg = ImageTk.PhotoImage(file='images/hongpao.png')

    def createSingleGame(self):
        self.initPosition()
        '''set black peices'''
        self.pos[(0,0)][2] = self.boardCanv.create_image(
            self.pos[(0,0)][0], self.pos[(0,0)][1],
            image=self.heijuImg)
        self.pos[(0,0)][3] = 0
        self.pos[(0,0)][4] = 1
        self.pos[(0,8)][2] = self.boardCanv.create_image(
            self.pos[(0,8)][0], self.pos[(0,8)][1],
            image=self.heijuImg)
        self.pos[(0,8)][3] = 0
        self.pos[(0,8)][4] = 1
        self.pos[(0,1)][2] = self.boardCanv.create_image(
            self.pos[(0,1)][0], self.pos[(0,1)][1],
            image=self.heimaImg)
        self.pos[(0,1)][3] = 0
        self.pos[(0,1)][4] = 2
        self.pos[(0,7)][2] = self.boardCanv.create_image(
            self.pos[(0,7)][0], self.pos[(0,7)][1],
            image=self.heimaImg)
        self.pos[(0,7)][3] = 0
        self.pos[(0,7)][4] = 2
        self.pos[(0,2)][2] = self.boardCanv.create_image(
            self.pos[(0,2)][0], self.pos[(0,2)][1],
            image=self.heixiangImg)
        self.pos[(0,2)][3] = 0
        self.pos[(0,2)][4] = 3
        self.pos[(0,6)][2] = self.boardCanv.create_image(
            self.pos[(0,6)][0], self.pos[(0,6)][1],
            image=self.heixiangImg)
        self.pos[(0,6)][3] = 0
        self.pos[(0,6)][4] = 3
        self.pos[(0,3)][2] = self.boardCanv.create_image(
            self.pos[(0,3)][0], self.pos[(0,3)][1],
            image=self.heishiImg)
        self.pos[(0,3)][3] = 0
        self.pos[(0,3)][4] = 4
        self.pos[(0,5)][2] = self.boardCanv.create_image(
            self.pos[(0,5)][0], self.pos[(0,5)][1],
            image=self.heishiImg)
        self.pos[(0,5)][3] = 0
        self.pos[(0,5)][4] = 4
        self.pos[(0,4)][2] = self.boardCanv.create_image(
            self.pos[(0,4)][0], self.pos[(0,4)][1],
            image=self.heijiangImg)
        self.pos[(0,4)][3] = 0
        self.pos[(0,4)][4] = 5
        self.pos[(2,1)][2] = self.boardCanv.create_image(
            self.pos[(2,1)][0], self.pos[(2,1)][1],
            image=self.heipaoImg)
        self.pos[(2,1)][3] = 0
        self.pos[(2,1)][4] = 6
        self.pos[(2,7)][2] = self.boardCanv.create_image(
            self.pos[(2,7)][0], self.pos[(2,7)][1],
            image=self.heipaoImg)
        self.pos[(2,7)][3] = 0
        self.pos[(2,7)][4] = 6
        self.pos[(3,0)][2] = self.boardCanv.create_image(
            self.pos[(3,0)][0], self.pos[(3,0)][1],
            image=self.heizuImg)
        self.pos[(3,0)][3] = 0
        self.pos[(3,0)][4] = 7
        self.pos[(3,2)][2] = self.boardCanv.create_image(
            self.pos[(3,2)][0], self.pos[(3,2)][1],
            image=self.heizuImg)
        self.pos[(3,2)][3] = 0
        self.pos[(3,2)][4] = 7
        self.pos[(3,4)][2] = self.boardCanv.create_image(
            self.pos[(3,4)][0], self.pos[(3,4)][1],
            image=self.heizuImg)
        self.pos[(3,4)][3] = 0
        self.pos[(3,4)][4] = 7
        self.pos[(3,6)][2] = self.boardCanv.create_image(
            self.pos[(3,6)][0], self.pos[(3,6)][1],
            image=self.heizuImg)
        self.pos[(3,6)][3] = 0
        self.pos[(3,6)][4] = 7
        self.pos[(3,8)][2] = self.boardCanv.create_image(
            self.pos[(3,8)][0], self.pos[(3,8)][1],
            image=self.heizuImg)
        self.pos[(3,8)][3] = 0
        self.pos[(3,8)][4] = 7

        '''set red peices'''
        self.pos[(9,0)][2] = self.boardCanv.create_image(
            self.pos[(9,0)][0], self.pos[(9,0)][1],
            image=self.hongjuImg)
        self.pos[(9,0)][3] = 1
        self.pos[(9,0)][4] = 1
        self.pos[(9,8)][2] = self.boardCanv.create_image(
            self.pos[(9,8)][0], self.pos[(9,8)][1],
            image=self.hongjuImg)
        self.pos[(9,8)][3] = 1
        self.pos[(9,8)][4] = 1
        self.pos[(9,1)][2] = self.boardCanv.create_image(
            self.pos[(9,1)][0], self.pos[(9,1)][1],
            image=self.hongmaImg)
        self.pos[(9,1)][3] = 1
        self.pos[(9,1)][4] = 2
        self.pos[(9,7)][2] = self.boardCanv.create_image(
            self.pos[(9,7)][0], self.pos[(9,7)][1],
            image=self.hongmaImg)
        self.pos[(9,7)][3] = 1
        self.pos[(9,7)][4] = 2
        self.pos[(9,2)][2] = self.boardCanv.create_image(
            self.pos[(9,2)][0], self.pos[(9,2)][1],
            image=self.hongxiangImg)
        self.pos[(9,2)][3] = 1
        self.pos[(9,2)][4] = 3
        self.pos[(9,6)][2] = self.boardCanv.create_image(
            self.pos[(9,6)][0], self.pos[(9,6)][1],
            image=self.hongxiangImg)
        self.pos[(9,6)][3] = 1
        self.pos[(9,6)][4] = 3
        self.pos[(9,3)][2] = self.boardCanv.create_image(
            self.pos[(9,3)][0], self.pos[(9,3)][1],
            image=self.hongshiImg)
        self.pos[(9,3)][3] = 1
        self.pos[(9,3)][4] = 4
        self.pos[(9,5)][2] = self.boardCanv.create_image(
            self.pos[(9,5)][0], self.pos[(9,5)][1],
            image=self.hongshiImg)
        self.pos[(9,5)][3] = 1
        self.pos[(9,5)][4] = 4
        self.pos[(9,4)][2] = self.boardCanv.create_image(
            self.pos[(9,4)][0], self.pos[(9,4)][1],
            image=self.hongshuaiImg)
        self.pos[(9,4)][3] = 1
        self.pos[(9,4)][4] = 5
        self.pos[(7,1)][2] = self.boardCanv.create_image(
            self.pos[(7,1)][0], self.pos[(7,1)][1],
            image=self.hongpaoImg)
        self.pos[(7,1)][3] = 1
        self.pos[(7,1)][4] = 6
        self.pos[(7,7)][2] = self.boardCanv.create_image(
            self.pos[(7,7)][0], self.pos[(7,7)][1],
            image=self.hongpaoImg)
        self.pos[(7,7)][3] = 1
        self.pos[(7,7)][4] = 6
        self.pos[(6,0)][2] = self.boardCanv.create_image(
            self.pos[(6,0)][0], self.pos[(6,0)][1],
            image=self.hongbinImg)
        self.pos[(6,0)][3] = 1
        self.pos[(6,0)][4] = 7
        self.pos[(6,2)][2] = self.boardCanv.create_image(
            self.pos[(6,2)][0], self.pos[(6,2)][1],
            image=self.hongbinImg)
        self.pos[(6,2)][3] = 1
        self.pos[(6,2)][4] = 7
        self.pos[(6,4)][2] = self.boardCanv.create_image(
            self.pos[(6,4)][0], self.pos[(6,4)][1],
            image=self.hongbinImg)
        self.pos[(6,4)][3] = 1
        self.pos[(6,4)][4] = 7
        self.pos[(6,6)][2] = self.boardCanv.create_image(
            self.pos[(6,6)][0], self.pos[(6,6)][1],
            image=self.hongbinImg)
        self.pos[(6,6)][3] = 1
        self.pos[(6,6)][4] = 7
        self.pos[(6,8)][2] = self.boardCanv.create_image(
            self.pos[(6,8)][0], self.pos[(6,8)][1],
            image=self.hongbinImg)
        self.pos[(6,8)][3] = 1
        self.pos[(6,8)][4] = 7



    def onClick(self,event):
        row = int(round((event.y - self.leftTop[1]) / self.cubeV))
        col = int(round((event.x - self.leftTop[0]) / self.cubeH))
        if self.peiceColor == 1:
            self.curPeice = (row, col)
        else:
            self.curPeice = (9-row, 8-col)

        if self.isNetPlay and self.walker != self.peiceColor:
            return

        if not self.pos[self.curPeice][2] and not self.peiceHolded:
            return

        if not self.peiceHolded:
            if self.pos[self.curPeice][3] != self.walker:
                return
            self.lastHoldId = self.pos[self.curPeice][2]
            self.holdingId = self.pos[self.curPeice][2]
            self.continueFlicker = True
            self.peiceHolded = True
            self.timer = threading.Timer(0.3, self.flicker)
            self.timer.start()
            self.lastPeice = self.curPeice
        else:
            if self.walker == self.pos[self.curPeice][3]:
                if self.lastPeice == self.curPeice:
                    self.continueFlicker = False
                    self.peiceHolded = False
                else:
                    self.holdingId = self.pos[self.curPeice][2]
                    self.boardCanv.itemconfig(self.lastHoldId, state=tk.NORMAL)
                    self.lastHoldId = self.pos[self.curPeice][2]
                    self.lastPeice = self.curPeice
            else:
                if self.moveSuccess():
                    self.tellTheEnemy()
                    self.whenGameEnded()




    def flicker(self):
        while self.continueFlicker:
            self.boardCanv.itemconfig(self.holdingId, state=tk.HIDDEN)
            time.sleep(0.3)
            self.boardCanv.itemconfig(self.holdingId, state=tk.NORMAL)
            time.sleep(0.3)


    def moveSuccess(self):
        if self.pos[self.lastPeice][4] == 1:#ju
            if self.juMovable():
                self.moveAction()
                return True
            return False
        elif self.pos[self.lastPeice][4] == 2:#ma
            if self.maMovable():
                self.moveAction()
                return True
            return False
        elif self.pos[self.lastPeice][4] == 3: #xiang
            if self.xiangMovable():
                self.moveAction()
                return True
            return False
        elif self.pos[self.lastPeice][4] == 4:#shi
            if self.shiMovable():
                self.moveAction()
                return True
            return False
        elif self.pos[self.lastPeice][4] == 5:#jiang||shuai
            if self.jsMovable():
                self.moveAction()
                return True
            return False
        elif self.pos[self.lastPeice][4] == 6:#pao
            if self.paoMovable():
                self.moveAction()
                return True
            return False
        else:#zu||bin
            if self.bzMovable():
                self.moveAction()
                return True
            return False



    def juMovable(self):
        start = self.lastPeice
        end = self.curPeice
        if start[0] != end[0] and start[1] != end[1]:
            return False
        if start[0] == end[0] and start[1] == end[1]:
            return False
        if start[0] == end[0]:
            row = start[0]
            coll = min(start[1], end[1])
            colr = max(start[1], end[1])
            for i in range(coll+1, colr):
                if self.pos[(row,i)][2]:
                    return False
        else:
            col = start[1]
            rowl = min(start[0], end[0])
            rowr = max(start[0], end[0])
            for i in range(rowl+1, rowr):
                if self.pos[(i,col)][2]:
                    return False
        return True

    def maMovable(self):
        start = self.lastPeice
        end = self.curPeice
        if end[0] - start[0] == -1 and start[1] - end[1] == 2:#up1
            if self.pos[(start[0], start[1] - 1)][2]:
                return False
            return True
        elif end[0] - start[0] == -2 and start[1] - end[1] == 1:#up2
            if self.pos[(start[0]-1, start[1])][2]:
                return False
            return True
        elif end[0] - start[0] == -2 and end[1] - start[1] == 1:#up3
            if self.pos[(start[0]-1, start[1])][2]:
                return False
            return True
        elif end[0] - start[0] == -1 and end[1] - start[1] == 2:#up4
            if self.pos[(start[0], start[1] + 1)][2]:
                return False
            return True
        elif start[0] - end[0] == -1 and start[1] - end[1] == 2:#down1
            if self.pos[(start[0], start[1] - 1)][2]:
                return False
            return True
        elif start[0] - end[0] == -2 and start[1] - end[1] == 1:#down2
            if self.pos[(start[0]+1,start[1])][2]:
                return False
            return True
        elif start[0] - end[0] == -2 and start[1] - end[1] == -1:#down3
            if self.pos[(start[0]+1,start[1])][2]:
                return False
            return True
        elif start[0] - end[0] == -1 and start[1] - end[1] == -2:#down4
            if self.pos[(start[0], start[1]+1)][2]:
                return False
            return True
        else:
            return False


    def xiangMovable(self):
        start = self.lastPeice
        end = self.curPeice
        if self.walker == 0 and end[0] > 4:
            return False
        if self.walker == 1 and end[0] < 5:
            return False

        if end[0] - start[0] == -2 and end[1] - start[1] == -2:#left top
            if self.pos[(start[0]-1, start[1]-1)][2]:
                return False
            return True
        if end[0] - start[0] == -2 and end[1] - start[1] == 2:#right top
            if self.pos[(start[0]-1,start[1]+1)][2]:
                return False
            return True
        if end[0] - start[0] == 2 and end[1] - start[1] == -2:#left bot
            if self.pos[(start[0]+1, start[1]-1)][2]:
                return False
            return True
        if end[0] - start[0] == 2 and end[1] - start[1] == 2:#right bot
            if self.pos[(start[0]+1, start[1]+1)][2]:
                return False
            return True
        return False

    def shiMovable(self):
        start = self.lastPeice
        end = self.curPeice
        if self.walker == 0 and (end[0] > 2 or end[1] < 3 or end[1] > 5 ):
            return False
        if self.walker == 1 and (end[0] < 7 or end[1] < 3 or end[1] > 5 ):
            return False
        if end[0] - start[0] == -1 and end[1] - start[1] == -1:#left top
            return True
        if end[0] - start[0] == -1 and end[1] - start[1] == 1:#right top
            return True
        if end[0] - start[0] == 1 and end[1] - start[1] == -1:#left bot
            return True
        if end[0] - start[0] == 1 and end[1] - start[1] == 1:#right bot
            return True
        return False

    def jsMovable(self):
        start = self.lastPeice
        end = self.curPeice
        if self.walker == 0 and (end[0] > 2 or end[1] < 3 or end[1] > 5 ):
            return False
        if self.walker == 1 and (end[0] < 7 or end[1] < 3 or end[1] > 5 ):
            return False
        if end[0] - start[0] == -1 and end[1] == start[1]:#top
            return True
        if end[0] == start[0] and end[1] - start[1] == -1:#left
            if self.walker == 0:
                for i in range(start[0]+1, 10):
                    if self.pos[(i,end[1])][2]:
                        if self.pos[(i,end[1])][4] == 5:
                            return False
                        else:
                            return True
                if self.walker == 1:
                    for i in range(start[0]-1, -1, -1):
                        if self.pos[(i,end[1])][2]:
                            if self.pos[(i,end[1])][4] == 5:
                                return False
                            else:
                                return True
                return True
        if end[0] - start[0] == 1 and end[1] == start[1]:#bot
            return True
        if end[0] == start[0] and end[1] - start[1] == 1:#right
            if self.walker == 0:
                for i in range(start[0]+1, 10):
                    if self.pos[(i,end[1])][2]:
                        if self.pos[(i,end[1])][4] == 5:
                            return False
                        else:
                            return True
            if self.walker == 1:
                for i in range(start[0]-1, -1, -1):
                    if self.pos[(i,end[1])][2]:
                        if self.pos[(i,end[1])][4] == 5:
                            return False
                        else:
                            return True
            return True
        return False


    def paoMovable(self):
        start = self.lastPeice
        end = self.curPeice
        if start[0] != end[0] and start[1] != end[1]:
            return False
        if start[0] == end[0] and start[1] == end[1]:
            return False
        if start[0] == end[0]:
            row = start[0]
            coll = min(start[1], end[1])
            colr = max(start[1], end[1])
            if not self.pos[end][2]:
                for i in range(coll+1, colr):
                    if self.pos[(row,i)][2]:
                        return False
            else:
                count = 0
                for i in range(coll+1, colr):
                    if self.pos[(row,i)][2]:
                        count+=1
                if count != 1:
                    return False

        else:
                col = start[1]
                rowl = min(start[0], end[0])
                rowr = max(start[0], end[0])
                if not self.pos[end][2]:
                        for i in range(rowl+1, rowr):
                                if self.pos[(i,col)][2]:
                                        return False
                else:
                        count = 0
                        for i in range(rowl+1, rowr):
                                if self.pos[(i,col)][2]:
                                        count+=1
                        if count != 1:
                                return False

        return True

    def bzMovable(self):
        start = self.lastPeice
        end = self.curPeice
        if start[0] != end[0] and start[1] != end[1]:
            return False
        if start[0] == end[0] and start[1] == end[1]:
            return False
        if abs(start[0] - end[0]) > 1 or abs(start[1] - end[1]) > 1:
            return False
        if self.walker == 0 and end[0] <= 4 and start[1] != end[1]:
            return False
        if self.walker == 0 and start[0] > end[0]:
            return False
        if self.walker == 1 and end[0] >= 5 and  start[1] != end[1]:
            return False
        if self.walker == 1 and start[0] < end[0]:
            return False

        return True


    def moveAction(self):
        start = self.lastPeice
        end = self.curPeice
        print(start)
        print(end)
        if self.pos[end][2]:
            self.boardCanv.delete(self.pos[end][2])
        self.boardCanv.move(self.pos[start][2],
            self.pos[end][0] - self.pos[start][0],
            self.pos[end][1] - self.pos[start][1]
            )
        self.printSheet()
        if self.pos[end][4] == 5:
            self.gameEnded = True

        self.pos[end][2] = self.pos[start][2]
        self.pos[end][3] = self.walker
        self.pos[end][4] = self.pos[start][4]
        self.pos[start][2] = None
        self.pos[start][3] = None
        self.pos[start][4] = None

        self.continueFlicker = False
        self.peiceHolded = False
        self.walker = 1 - self.walker


    def clearBoard(self):
        for i in range(10):
            for j in range(9):
                if self.pos[(i,j)][2]:
                    self.boardCanv.delete(self.pos[(i,j)][2])

    def printSheet(self):
        fbt = {-1:'退', 0:'平', 1:'进'}
        start = self.lastPeice
        end = self.curPeice
        rorb = self.pos[start][3]
        stone = self.pos[start][4]
        if rorb == 0:#black
            if end[1] == start[1]:
                step = abs(end[0] - start[0])
            else:
                step = end[1] + 1
            line = start[1] + 1
            if end[0] > start[0]:
                forbt = 1
            elif end[0] ==  start[0]:
                forbt = 0
            else:
                forbt = -1
        else:
            if end[1] == start[1]:
                step = abs(end[0] - start[0])
            else:
                step = 9 - end[1]
            line = 9 - start[1]
            if end[0] > start[0]:
                forbt = -1
            elif end[0] ==  start[0]:
                forbt = 0
            else:
                forbt = 1
        if rorb == 0:
            print ('%s: %s %d %s %d' % (self.rb[rorb],
                self.peicesB[stone],
                line,
                fbt[forbt],
                step
                ))
        else:
            print ('%s: %s %d %s %d' % (self.rb[rorb],
                self.peicesR[stone],
                line,
                fbt[forbt],
                step
                ))
    def watchEnemy(self, emptyStr):
        while not self.gameEnded:
            data = self.netplay.recvMsg()
            if re.match('[0-9][0-8][0-9][0-8]', data):
                print('received data is: '+data)
                self.doEnemysDone(data)

    def doEnemysDone(self, data):
        self.lastPeice = (int(data[0]), int(data[1]))
        self.curPeice = (int(data[2]), int(data[3]))
        self.moveAction()
        self.whenGameEnded()

    def tellTheEnemy(self):
        start = self.lastPeice
        end = self.curPeice
        if self.isNetPlay:
            operateStr = '%d%d%d%d' % (start[0], start[1], end[0], end[1])
            self.netplay.sendMsg(operateStr)

    def whenGameEnded(self):
        if self.gameEnded:
            self.peiceColor = 1 - self.peiceColor
            winner = self.rb[1 - self.walker]
            if messagebox.askyesno('游戏结束',winner+'方胜，继续游戏？'):
                self.restart()
            else:
                self.quit()

app = Application()
app.master.title('中国象棋')
app.mainloop()
