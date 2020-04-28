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
import subprocess
import re

SEQCOUNT = 1
 
def getID(argv):
    """Returns the first command line argument after the -id flag

    Arguments:
        argv {string} -- command line vector

    Returns:
        argv[i+1]  -- The next command line item after -id, device ID
    """
    for i, arg in enumerate(argv):
        if(arg=="-id"):
            return argv[i+1]

def getIpFromRoute():
    """Issues route -n to the linux CLI for particular device. 
    Stores the results into the ipPattern variable, and parses 
    using regular expressions. Parsed IP addresses represent adjacent
    devices.

    Returns:
        ipAddresses -- Python list of adjacent IP addresses
    """
    ipAddresses = []
    routeString = subprocess.check_output("route -n", shell=True).decode()
    ipPattern = re.compile(r'[1][9][2][.]\d\d\d[.]\d[.][0-9][0-9][0-9]')
    matches = ipPattern.finditer(routeString)
    for match in matches:
        ipAddresses.append(match.group())
    
    return ipAddresses


#logic for sending Link State packets here
def sendLinkState(myID):
    """Background process to send link state packets to adjacent devices
    every ten seconds. Each timed call to function gets current adjacent IPs,
    opens, stores and creates link state packet from devices routing table JSON file, 
    and iterates through adjacent IPs to send link state packet.

    Arguments:
        myID {int} -- Integer representing device's ID
    """
    global SEQCOUNT
    SEQCOUNT += 1
    print(SEQCOUNT)

    ipAddresses = getIpFromRoute()
    length = len(ipAddresses)

    try:
        with open(myID + '.json') as f:
            routeTable = json.load(f)
            # print(routeTable)

    except:
        print("No routing table")
        return

    linkStatePacket = createLinkStatePacket(SEQCOUNT, routeTable, myID)

    for i in range(length):
        my_socket = socket(AF_INET, SOCK_DGRAM)
        my_socket.sendto(linkStatePacket, (ipAddresses[i], 8888))
        my_socket.close()
        print("Sent packet to the destination: " + ipAddresses[i])
        time.sleep(1)
        #continuously call the function in thread 
    
    threading.Timer(10, sendLinkState, [myID]).start()

def receive_packet(my_addr, port_num):
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
    """Send an acknowledgement packet to joining host device.

    Arguments:
        dst {int} -- Integer representing the host device requesting to joing network.

    Returns:
        0 -- Unused boolean return value.
    """
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
    """Reads the first byte of any incoming packet and returns
    its value.

    Arguments:
        pkt {packed struct} -- pkt is the raw packed struct received via UDP

    Returns:
        pkttype -- integer representation of received packet type
    """
    pktType = pkt[0:1]
    pkttype = struct.unpack('B', pktType)

    return pkttype 

def decodeLinkStatePkt(pkt):

    pktHeader = pkt[:4]

    print(len(pktHeader))

    pktType, seq, length, src = struct.unpack('BBBB', pktHeader)
    data = pkt[4:]

    return seq, length, src, data

def writeHostJsonFile(helloSrc, myID):
    """
    Must be fundamentally changed to add data
    to routing table, rather than create a table.
    Latest version of router creates table on startup
    """
    localHost = {"destination": [ {
                'name': helloSrc,
                'path': helloSrc,
                'cost': 1
            } ] }

    with open(myID + '.json', 'w') as f:
        json.dump(localHost, f)

def createLinkStatePacket(SEQCOUNT, routeTable, myID):
    """Composes link state packet by reading json routing table
    and packing struct. Note that the data is not "packed" into 
    the struct, but rather appended to the end of it.

    Arguments:
        SEQCOUNT {int} -- Global incrimenting sequence counter for LSP
        routeTable {JSON} -- JSON routing table
        myID {int} -- Devices ID

    Returns:
        pkt -- Packet ready to be sent to all adjacent routers
    """
    pktType = 2
    length = 1
    src = int(myID)

    data = json.dumps(routeTable)
    data = bytes(data).encode('utf-8')
    pkt = struct.pack('BBBB', pktType, SEQCOUNT, len(data), src)+data

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

    
