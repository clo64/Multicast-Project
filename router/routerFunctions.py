import sys
sys.path.append('../')
import idMap
import time
from socket import *
import struct
import select
import random
import asyncore
import threading
import json
import os
import globalConfig
import subprocess
import re

#Get ID from the command line
#No error checking, so don't screw it up. 
def getID(argv):
    for i, arg in enumerate(argv):
        if(arg=="-id"):
            return argv[i+1]

def getIpFromRoute():
    ipAddresses = []
    routeString = subprocess.check_output("route -n", shell=True).decode()
    ipPattern = re.compile(r'[1][9][2][.]\d\d\d[.]\d[.][0-9][0-9][0-9]')
    matches = ipPattern.finditer(routeString)
    for match in matches:
        ipAddresses.append(match.group())
    
    return ipAddresses


#logic for sending Link State packets here
def sendLinkState(myID):
    ipAddresses = getIpFromRoute()
    length = len(ipAddresses)

    try:

        with open(myID + '.json') as f:
            routeTable = json.load(f)
            # print(routeTable)

    except:

        print("No routing table")
        return

    linkStatePacket = createLinkStatePacket(routeTable, myID)

    for i in range(length):
        my_socket = socket(AF_INET, SOCK_DGRAM)
        my_socket.sendto(linkStatePacket, (ipAddresses[i], 8888))
        my_socket.close()
        print("Sent packet to the destination: " + ipAddresses[i])
        time.sleep(1)
        #continuously call the function in thread 
    
    threading.Timer(10, sendLinkState, [myID]).start()

def receive_packet(my_addr, port_num):
    # """
    # Listens at an IP:port
    # """
    my_socket = socket(AF_INET, SOCK_DGRAM)
    my_socket.bind((my_addr, port_num))

    while True:
        data, addr = my_socket.recvfrom(1024)
        #print("Received packet", data, "from source", addr)
        break

    return data

def read_hello(pkt):
	#Change the bytes to account for network encapsulations
    header = pkt[0:36]
    #pktFormat = "BLBBL"
    #pktSize = struct.calcsize(pktFormat)
    pkttype, seq, src = struct.unpack("BBB", header)

    return pkttype, seq, src

def sendHelloACK(dst):
    helloACKType = 0x04
    helloACKDST = dst
    helloACK = struct.pack('BB', helloACKType, helloACKDST)

    time.sleep(2)
    my_socket = socket(AF_INET, SOCK_DGRAM)
    my_socket.sendto(helloACK, (idMap.code_to_IP(dst), 8888))
    my_socket.close()
    print("Sent Hello ACK: " + idMap.code_to_IP(dst))

    return 0

def decodePktType(pkt):
    pktType = pkt[0:1]
    pkttype = struct.unpack('B', pktType)

    return pkttype 

def writeHostJsonFile(helloSrc, myID):
    localHost = {"destination": [ {
                'name': helloSrc,
                'path': helloSrc,
                'cost': 1
            } ] }

    with open(myID + '.json', 'w') as f:
        json.dump(localHost, f)

def createLinkStatePacket(routeTable, myID):
    #seq number that runs to infinity
    globalConfig.linkStateCounter += 1
    pktType = 2

    #don't think seq is important?
    seq = globalConfig.linkStateCounter
    length = 1
    src = int(myID)

    #convert json data to string for packing
    data = json.dumps(routeTable)
    print(routeTable)
    pkt = struct.pack('BBBBp', pktType, seq, length, src, data)

    return pkt

def checkForRoutingTable(myID):
    try:

        with open(myID + '.json') as f:
            routeTable = json.load(f)
            # print(routeTable)
        return 1

    except:

        return 0

def createFirstRoutingTable(myID):
    localHost = {"destination": [ {
                'name': myID,
                'path': myID,
                'cost': 1
            } ] }

    with open(myID + '.json', 'w') as f:
        json.dump(localHost, f)

    
