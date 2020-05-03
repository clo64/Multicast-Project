import routerFunctions
import commonFunctions
import time
import threading
import sys
import struct
import json
import os
from socket import *

if __name__ == "__main__":

    #read the router's ID from the command line input -id
    myID = int(commonFunctions.getIP())
    print("My ID is : {}".format(myID))

    nodeGraph = {str(myID): []}
    print(nodeGraph)

    #Data structure to keep track of sequence number of received 
    #link state packets
    linkStateSeqNumber = {}

    #if device has no routing table, a file and template will be created
    if(routerFunctions.checkForRoutingTable(myID) == 0):
        print("Creating Routing Table")
        routerFunctions.createFirstRoutingTable(myID)

    #prepare hello packet
    pkttype = 0x05
    src = myID
    #print("src is : ".format(src))
    seq = 0x01
    helloACKCounter = 0
    length = len(routerFunctions.getIpFromRoute())
    routerHelloPacket = struct.pack('BBB', pkttype, seq, src)

    ipAddresses = routerFunctions.getIpFromRoute()
    localStoreIPAddresses = ipAddresses
    
    """
    Router "Hello" logic. The router spins a new thread every iteration of the loop. The thread
    loops through the ipAddresses array and sends a router hello packet. If the logic succesfully 
    receives an ACK, the ip address for that ACK is removed from the ipAddresses array. 
    """
    while(helloACKCounter != length):
        routerHelloThread = threading.Thread(target = routerFunctions.sendRouterHello, args=(myID, routerHelloPacket, ipAddresses))
        routerHelloThread.start()
        temp, nodeGraph, ipOfACK = routerFunctions.receiveRouterHello(myID, nodeGraph)
        if(ipOfACK is not None):
            try:
                localStoreIPAddresses.remove(ipOfACK)
            except:
                print("No such IP")
        helloACKCounter = helloACKCounter + temp
        routerHelloThread.join()
        ipAddresses = localStoreIPAddresses
        print("Node Graph Updated")
        print(nodeGraph)
    
    #initializes Link State transmission to occur every 10 seconds
    routerFunctions.sendLinkState(myID, nodeGraph)

    while True:
        #listen on all ports logic here
        receivedPkt, addr = routerFunctions.receive_packet('0.0.0.0', 8888)
        packetType = routerFunctions.decodePktType(receivedPkt)
        
        #if packet type 1, Hello, respond with Hello ACK
        if(packetType[0] == 1):
            helloType, helloSeq, helloSrc = routerFunctions.read_hello(receivedPkt)
            print("HelloSrc is: {}".format(helloSrc))

            #Call a function to DO something with the SRC you got.
            routerFunctions.sendHelloACK(helloSrc)

            #!! This should be an append situation, not a completely new file
            #This is an artifact from testing, should be replaced with an append
            #routerFunctions.writeHostJsonFile(helloSrc, myID)
            routerFunctions.addHostToGraph(helloSrc, myID, nodeGraph)
            print("Graph updated with host")
            print(nodeGraph)

        #if packet type 2, link state packet, how do we respond??
        if(packetType[0] == 2):
            print("got a link state packet")
            seq, length, src, data = routerFunctions.decodeLinkStatePkt(receivedPkt)
            """
            print("Here's the src value")
            print(src)
            print("Here the data")
            print(data)
            print(linkStateSeqNumber)
            """
            if(src != myID):
                if(src > 150):
                    ipAddresses = routerFunctions.getIpFromRoute()
                    ipAddresses.remove(addr[0])
                linkStateForwardThread = threading.Thread(target=routerFunctions.forwardLinkState, args=(ipAddresses, receivedPkt))
                linkStateForwardThread.start()
                nodeGraph = routerFunctions.updateGraph(seq, src, linkStateSeqNumber, data, nodeGraph)
            #spin new thread to forward link state on all nodes except the node it
            #came in on!!

            #inkStateData = json.loads(data)
            #print(linkStateData['201'])
            #decodeLinkState(receivedPkt)
        #if packet type 3, data, how to we respond?

        #In the event a router hello packet was previously missed
        if(packetType[0] == 5):
            helloACKpkt = struct.pack('BBB', 0x04, 0x01, myID)
            pkttype, seq, srcVal = struct.unpack('BBB', receivedPkt)
            my_socket = socket(AF_INET, SOCK_DGRAM)
            my_socket.sendto(helloACKpkt, (commonFunctions.convertID(srcVal), 8888))
            my_socket.close()
            print("Got a hello message!")
