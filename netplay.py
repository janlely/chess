import socket, threading
import socketfactory as sf
import iputil
import time
import _thread


class NetPlay:

    def __init__(self, port):
        self.port = port
        self.client = None
        self.conn = None
        self.playerConnected = False
        self.passhead = 'youcanneverguess'

    def createConnection(self, pwd, exact):
        self.passwd = pwd
        '''search room with passwd'''
        if self.roomFound(exact) == 1: # found room with right password
            return self.joinRoom()
        elif self.roomFound(exact) == 0: # no room found
            return self.createRoom()
        else:
            return 2 # found room but  password not match

    #  def roomFound(self, exact):
        #  self.findRoom()
        #  if self.serverFound:
            #  return True
        #  else:
            #  return False

    def roomFound(self, exact):
        self.serverFound = False
        timer = threading.Timer(0, self.findRoomLimit)
        timer.start()
        bcr = sf.broadCastReceiver(self.port)
        bcr.settimeout(2)
        try:
            data,addr = bcr.recvfrom(1024)
            if data and data.decode() == self.passhead + self.passwd:
                self.serverFound = True
                self.serverIp = addr[0]
                return 1#found room with right password
            elif data and data.decode() and self.passhead:
                if exact:
                    return 0#found room with wrong password
                else:
                    return 2

            else:
                return 0
        except Exception:
            self.serverFound = False
            return 0



    def findRoomLimit(self):
        self.timeout = False
        time.sleep(1)
        self.timeout = True



    def joinRoom(self):
        self.client = sf.tcpClientSocket(self.serverIp, self.port)
        if not self.client:
            return -1
        return 0

    def joinRoomExact(self, ip):
        self.client = sf.tcpClientSocket(ip, self.port)
        if not self.client:
            return -1
        return 0

    def createRoom(self):
        _thread.start_new_thread(self.broadcast, (self.passwd,))
        self.server = sf.tcpServerSocket(self.port)
        if not self.server:
            return -1
        self.server.listen(1)
        self.conn, addr = self.server.accept()
        self.playerConnected = True
        return 1

    def createRoomExact(self):
        self.server = sf.tcpServerSocket(self.port)
        if not self.server:
            return -1
        self.server.listen(1)
        self.conn, addr = self.server.accept()
        self.playerConnected = True
        return 1

    def sendMsg(self, msg):
        if self.client:
            self.client.sendall(msg.encode())
        else:
            self.conn.sendall(msg.encode())


    def recvMsg(self):
        if self.client:
            return self.client.recv(1024).decode()
        else:
            return self.conn.recv(1024).decode()

    def broadcast(self, content):
        bcs = sf.broadCastSender()
        while not self.playerConnected:
            bcs.sendto((self.passhead + content).encode(), ('255.255.255.255',self.port))
            time.sleep(0.5)

