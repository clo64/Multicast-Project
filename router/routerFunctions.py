import sys
sys.path.append('../')
import commonFunctions
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
from collections import defaultdict

SEQCOUNT = 1
#This semaphore is used exclusively for coordinating the link state
#send functions: sendLinkState and forwardLinkState
sem = threading.Semaphore()
#This emaphore used to synchronize receive socket bindings, without it
#system would crach after minute-ish
recHelloSynch = threading.Semaphore()

def getIpFromRoute():
    """
    Issues route -n to the linux CLI for particular device. 
    Stores the results into the ipPattern variable, and parses 
    using regular expressions. Parsed IP addresses represent adjacent
    devices.

    Returns:
        ipAddresses -- Python list of adjacent IP addresses
    """
    ipAddresses = []
    routeString = subprocess.check_output("route -n", shell=True).decode()
    ipPattern = re.compile(r'[1][9][2][.]\d\d\d[.]\d[.][2][0-9][0-9]')
    matches = ipPattern.finditer(routeString)
    for match in matches:
        ipAddresses.append(match.group())
    
    return ipAddresses


#logic for sending Link State packets here
def sendLinkState(myID, nodeGraph):
    """
    Background process to send link state packets to adjacent devices
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
    """
    try:
        with open(str(myID) + '.json') as f:
            routeTable = json.load(f)
            # print(routeTable)

    except:
        print("No routing table")
        return
    """

    linkStatePacket = createLinkStatePacket(SEQCOUNT, nodeGraph, myID)
    sem.acquire()
    for i in range(length):
        my_socket = socket(AF_INET, SOCK_DGRAM)
        my_socket.sendto(linkStatePacket, (ipAddresses[i], 8888))
        my_socket.close()
        print("Sent packet to the destination: " + ipAddresses[i])
        time.sleep(1)
        #continuously call the function in thread 
    sem.release()
    threading.Timer(10, sendLinkState, [myID, nodeGraph]).start()

def forwardLinkState(ipAddresses, linkState):
    #unreliable forward on all ports except the one link state received on
    length = len(ipAddresses)
    sem.acquire()
    try:
        for i in range(length):

            my_socket = socket(AF_INET, SOCK_DGRAM)
            my_socket.sendto(linkState, (ipAddresses[i], 8888))
            my_socket.close()
            print("Forwarded Link State: " + ipAddresses[i])

            time.sleep(1)
        sem.release()
    except:
        print("Send error, trying again")
        sem.release()

def receive_packet(my_addr, port_num):
    #causing error is socket is already bound
    #trying a while True loop to eliminate error
    recHelloSynch.acquire()
    while True:
        try:
            my_socket = socket(AF_INET, SOCK_DGRAM)
            my_socket.bind((my_addr, port_num))
            data, addr = my_socket.recvfrom(1024)
            #print("Received packet", data, "from source", addr)
            recHelloSynch.release()
            break
        except:
            print("Port busy, try again")
            time.sleep(1)
            continue

    return data, addr

def sendRouterHello(myID, routerHelloPacket, ipAddresses):
    length = len(ipAddresses)
    try:
        for i in range(length):

            my_socket = socket(AF_INET, SOCK_DGRAM)
            my_socket.sendto(routerHelloPacket, (ipAddresses[i], 8888))
            my_socket.close()
            print("Sent router hello to: " + ipAddresses[i])

            time.sleep(1)
    except:
        print("Send error, trying again")

def receiveRouterHello(myID, nodeGraph):
    helloACKpkt = struct.pack('BBB', 0x04, 0x01, myID)
    nodeGraphArray = nodeGraph[str(myID)]

    recHelloSynch.acquire()
    my_socket = socket(AF_INET, SOCK_DGRAM)   
    my_socket.settimeout(4)
    my_socket.bind((commonFunctions.convertID(myID), 8888))
    #Hello ACK type set as 4, listening to hear this value

    try:
        print("Listening for Hello ACK")
        data, addr = my_socket.recvfrom(1024)
        pktType = decodePktType(data)
        recHelloSynch.release()

        if (pktType[0] == 4): #Hello ACK
            pkttype, seq, srcVal = struct.unpack('BBB', data)
            nodeGraphArray.append(str(srcVal))
            nodeGraph = {str(myID): nodeGraphArray}
            print("Hello ACK Received")
            ipOfACK = addr[0]
            return 1, nodeGraph, ipOfACK
            
        elif (pktType[0] == 5): #Received Hello Packet
            pkttype, seq, srcVal = struct.unpack('BBB', data)
            my_socket = socket(AF_INET, SOCK_DGRAM)
            my_socket.sendto(helloACKpkt, (commonFunctions.convertID(srcVal), 8888))
            my_socket.close()
            print("Got a hello message!")
            return 0, nodeGraph, None
    except:
        recHelloSynch.release()
        return 0, nodeGraph, None

    recHelloSynch.release()
    return 0, nodeGraph, None
    

def read_hello(pkt):
	#Change the bytes to account for network encapsulations
    header = pkt[0:36]
    #pktFormat = "BLBBL"
    #pktSize = struct.calcsize(pktFormat)
    pkttype, seq, src = struct.unpack("BBB", header)

    return pkttype, seq, src


def sendHelloACK(dst):
    """
    Send an acknowledgement packet to joining host device.

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
    my_socket.sendto(helloACK, (commonFunctions.convertID(dst), 8888))
    my_socket.close()
    print("Sent Hello ACK: " + commonFunctions.convertID(dst))


    return 0

def decodePktType(pkt):
    """
    Reads the first byte of any incoming packet and returns
    its value. Device should determine outcome from there.

    Arguments:
        pkt {packed struct} -- pkt is the raw packed struct received via UDP

    Returns:
        pkttype -- integer representation of received packet type
    """
    pktType = pkt[0:1]
    pkttype = struct.unpack('B', pktType)

    return pkttype 

def decodeLinkStatePkt(pkt):
    """
    Decodes Link State Packet as byte, int, int, byte and 
    assumes that data has been concatenaged to the end of the 
    incoming packet

    Arguments:
        pkt {packed struct} -- Data that needs to be unpacked

    Returns:
        seq, length, src, data -- Returns all unpacked data except pktType
    """

    pktHeader = pkt[:13]

    pktType, seq, length, src = struct.unpack('BiiB', pktHeader)
    data = pkt[13:]

    return seq, length, src, data

def updateGraph(seq, src, linkStateSeqNumber, data, nodeGraph):
    #if the sequence number of the received link state packet is > than the old one
    #update linkStateSeqNumber, and add, or update nodeGraph to reflect new key data
    #JSON serialize the data into dict first...
    linkStateData = json.loads(data)
    if (str(src) in nodeGraph) and (seq > int(linkStateSeqNumber[str(src)])):
        nodeGraph.update(linkStateData)
        print("Updated old graph")
        print(nodeGraph)
        return nodeGraph
    else:
        newKeyPair = {str(src): seq}
        linkStateSeqNumber.update(newKeyPair)
        nodeGraph.update(linkStateData)
        print("Added new entry to graph")
        print(nodeGraph)
        return nodeGraph

def writeHostJsonFile(helloSrc, myID):
    """
    Must be fundamentally changed to add data
    to routing table, rather than create a table.
    Latest version of router creates table on startup
    """
    fromHello = {str(helloSrc): {
                    "path": [ helloSrc ],
                    "cost": 1
                } }

    #print(json.dumps(fromHello))

    with open(str(myID) + '.json', 'r') as f:
        routingTable = json.load(f)
        temp = routingTable['destination']
        #print(temp)

    with open(str(myID) + '.json', 'w') as f:
        temp.update(fromHello)
        #print(routingTable)
        json.dump(routingTable, f, indent=3)

def addHostToGraph(helloSrc, myID, nodeGraph):
    #extract array myID's array from nodeGraph
    connectedDevices = nodeGraph[str(myID)]
    if str(helloSrc) in connectedDevices:
        return 0
    else:
        connectedDevices.append(str(helloSrc))
        graphUpdate = {str(myID):connectedDevices}
        nodeGraph.update(graphUpdate)
        return nodeGraph

def createLinkStatePacket(SEQCOUNT, nodeGraph, myID):
    """
    Composes link state packet by reading json routing table
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

    #Use dict comprehensions to pull just my link state data by IP
    linkStateSubset = {str(myID):nodeGraph[str(myID)]}
    data = json.dumps(linkStateSubset)
    data = bytes(data).encode('utf-8')

    pkt = struct.pack('BiiB', pktType, SEQCOUNT, len(data), src)+data

    return pkt

def checkForRoutingTable(myID):
    """
    On device startup, if no routing table exists, this funciton
    creates one that contains only the device itself.

    Arguments:
        myID {int} -- Devices ID

    Returns:
        Boolean int -- 1 if creating file successful, 0 if not
    """
    try:
        open(str(myID) + ".json", 'r')
        print("Initial Table Found")
        return 1
    except IOError:
        print("Did not find inital table")
        return 0

def createFirstRoutingTable(myID):
    
    localHost = {"destination": {
                    str(myID): {
                        "path": [ myID ],
                        "cost": 1
                } } }

    with open(str(myID) + '.json', 'w') as f:
        json.dump(localHost, f)

def getPath(myID, destID):
    
    with open(str(myID) + '.json', 'r') as f:
        routingTable = json.load(f)
    
    return routingTable['destination'][str(destID)][path]