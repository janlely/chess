import socket
import iputil


def broadCastReceiver(port):
    addr = ('', port)
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.bind(addr)
    return udps

def broadCastSender():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return udp

def tcpServerSocket(port):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.bind((iputil.getip(), port))
    except socket.error:
        return None

    return s;

def tcpClientSocket(addr,port):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((addr,port))
    except socket.error:
        return None
    return s
