import routerFunctions
import commonFunctions
import selectRP
import time
import threading
import sys
import struct
import json
import os
import itertools
from socket import *

if __name__ == "__main__":

    #read the router's ID from the command line input -id
    myID = int(commonFunctions.getID())
    print("My ID is : {}".format(myID))

    nodeGraph = {str(myID): []}
    #print(nodeGraph)

    #Data structure to keep track of sequence number of received 
    #link state packets
    linkStateSeqNumber = {}

    #if device has no routing table, a file and template will be created
    if(routerFunctions.checkForRoutingTable(myID) == 0):
        print("Creating Routing Table")
        routerFunctions.createFirstRoutingTable(myID)

    #TESTING
    #selectRP.bestkn(2,3,myID,101)
    #selectRP.selectRP(3,3,myID,101)
    #quit()

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

        if(packetType[0] == 7):
            print("Recveied Data Packet")
            seq, src, ndest, rdest, dest1, dest2, dest3, data = commonFunctions.decodeDataPkt(receivedPkt)
            pktType = 0x07
            #Determine Core router runctionality or RP router functionality
            if (dest1 & dest2 & dest3 == 0):
                #Assume Core Router functionality
                #If ndest is 1 unicast message to dest1
                n = 3
                srcID = src
                selectedRP, selectedDests = selectRP.selectRP(ndest,n,myID,srcID)
                dests = [0] * 3
                dests[0:len(selectedDests)] = selectedDests
                
                if ndest == 1:
                    #send datapkt to dest1
                    selectedRP = 0
                    datapkt = commonFunctions.createDataPacket(pktType, seq, src, ndest, selectedRP, dests[0], dests[1], dests[2], data)
                    nextHop = commonFunctions.getNextHop(myID,dests[0])
                    sendData(nextHop, datapkt)
                else:
                    #If ndest > 1 then need to send information to RP
                    #Send pkt to selectedRP
                    datapkt = commonFunctions.createDataPacket(pktType, seq, src, ndest, selectedRP, dests[0], dests[1], dests[2], data)
                    nextHop = commonFunctions.getNextHop(myID,rdest)
                    sendData(nextHop, datapkt)
            elif rdest != 0:
                #Forward packet along to RP
                datapkt = receivedPkt
                nextHop = commonFunctions.getNextHop(myID,rdest)
                sendData(nextHop, datapkt)
            elif ndest == 1:
                #Forward packet to dest1
                datapkt = receivedPkt
                nextHop = commonFunctions.getNextHop(myID,dest1)
                sendData(nextHop, datapkt)
            else:
                #Assume RP functionality
                dests = [dest1, dest2, dest3]
                destPath = [0] * 3
                #Get paths for destinations
                eleDelete = []
                for ii in range(len(dests)):
                    if dests[ii] != 0:
                        destPath[ii] = routerFunctions.getPath(myID,dests[ii])
                    else:
                        eleDelete.append(ii)
                        #destPath.pop(ii)
                #Delete elements for unavailable destinations
                for ele in eleDelete
                    destPath.pop(ele)
            
                #Check combinations of paths to see if next hop is the same
                lookaheadFlag = []
                index=range(len(destPath))
                for a, b in itertools.combinations(index, 2):
                    if destPath[a][0] == destPath[b][0]:
                        lookaheadFlag.append([a,b])
                    #print("DestPathA {}: {} DestPathB {}: {}".format(a,destPath[a][0], b, destPath[b][0]))

                #Determine how to send packets based on if other destinations
                #have the same next hop
                if len(lookaheadFlag) == len(destPath):
                    #All messages going to same next hop
                else:
                    #just send dests[lookaheadFlag[0][0]] and dests[lookaheadFlag[0][1]] to gether but
                    #not the other value
                    #if this condition is hit there will only be one entry in the lookaheadFlag
                    #send(dests[lookaheadFlag[0][0]] and dests[lookaheadFlag[0][1]])
                    if len(destPath) == 3:
                        dests.pop(lookaheadFlag[0])
                        dests.pop(lookaheadFlag[1])
                        #send(dests)


                #eventually zero out rdest as rdest has processed the information
"""
#Just some test code
destPath = [[1,2,3],[1,5,6],[1,7,8]]
lookaheadFlag = []
index=range(len(destPath))
for a, b in itertools.combinations(index, 2):
    if destPath[a][0] == destPath[b][0]:
        lookaheadFlag.append([a,b])
print(lookaheadFlag)
"""