#!/usr/bin/env python3

import netifaces as ni

def getip():
    try:
        iflist = [x for x in ni.interfaces() if 2 in ni.ifaddresses(x) and
                ni.ifaddresses(x)[2][0]['addr'] != '127.0.0.1' and
                'broadcast' in ni.ifaddresses(x)[2][0]]
        return ni.ifaddresses(iflist[0])[2][0]['addr']
    except Exception:
        return '127.0.0.1'


