import routerFunctions
import commonFunctions
import time
import threading
import sys
import struct
import json
import os

if __name__ == "__main__":

    #read the router's ID from the command line input -id
    #myID = routerFunctions.getID(sys.argv)
    myID = int(commonFunctions.getIP())
    print("My ID is : {}".format(myID))
    #if device has no routing table, a file and template will be created
    if(routerFunctions.checkForRoutingTable(myID) == 0):
        print("Creating Routing Table")
        routerFunctions.createFirstRoutingTable(myID)

    #initializes Link State transmission to occur every 10 seconds
    routerFunctions.sendLinkState(myID)

    while True:
        #listen on all ports logic here
        receivedPkt = routerFunctions.receive_packet('0.0.0.0', 8888)
        packetType = routerFunctions.decodePktType(receivedPkt)
        
        #if packet type 1, Hello, respond with Hello ACK
        if(packetType[0] == 1):
            helloType, helloSeq, helloSrc = routerFunctions.read_hello(receivedPkt)
            print("HelloSrc is: {}".format(helloSrc))

            #Call a function to DO something with the SRC you got.
            routerFunctions.sendHelloACK(helloSrc)

            #!! This should be an append situation, not a completely new file
            #This is an artifact from testing, should be replaced with an append
            routerFunctions.writeHostJsonFile(helloSrc, myID)

        #if packet type 2, link state packet, how do we respond??
        if(packetType[0] == 2):
            print("got a link state packet")
            seq, length, src, data = routerFunctions.decodeLinkStatePkt(receivedPkt)
            linkStateData = json.loads(data)
            print(linkStateData['destination'])
             #decodeLinkState(receivedPkt)
        #if packet type 3, data, how to we respond?
            
