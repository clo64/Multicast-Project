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
    #initializes dijkstra to run every 15 seconds
    #routerFunctions.runDijkstra(nodeGraph, myID)

    while True:
        #listen on all ports logic here

        #test send data packet ***** remove before flight *********
        #routerFunctions.sendData(routerHelloPacket, 101, 201)

        receivedPkt, addr = routerFunctions.receive_packet('0.0.0.0', 8888)
        packetType = routerFunctions.decodePktType(receivedPkt)
        
        #if packet type 1, Hello, respond with Hello ACK
        if(packetType == 1):
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
        if(packetType == 2):
            ipAddresses = routerFunctions.getIpFromRoute()
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
                linkStateForwardThread.run()
                nodeGraph = routerFunctions.updateGraph(seq, src, linkStateSeqNumber, data, nodeGraph)
                """
                with open("nodeGraph" + str(myID) + '.json', 'w') as f:
                    json.dump(nodeGraph, f, indent=3)
                """
                #Run dijkstra after updating nodeGraph
                routerFunctions.runDijkstra(nodeGraph, myID)

                
                #Seeing if clearing this slows things down..?
                packetType = 0
                
                
                
                #*****Commented out for testing**** --Chuck
                #routerFunctions.runDijkstra(nodeGraph, myID)
                #*****throwing key error***********
                
            #spin new thread to forward link state on all nodes except the node it
            #came in on!!

            #inkStateData = json.loads(data)
            #print(linkStateData['201'])
            #decodeLinkState(receivedPkt)
        #if packet type 3, data, how to we respond?

        #In the event a router hello packet was previously missed
        if(packetType == 5):
            helloACKpkt = struct.pack('BBB', 0x04, 0x01, myID)
            pkttype, seq, srcVal = struct.unpack('BBB', receivedPkt)
            my_socket = socket(AF_INET, SOCK_DGRAM)
            my_socket.sendto(helloACKpkt, (commonFunctions.convertID(srcVal), 8888))
            my_socket.close()
            print("Got a hello message!")

        if(packetType == 7):
            print("Recveied Data Packet")
            print("Sending dataACK")
            print(addr)
            routerFunctions.sendDataACK(addr[0])
            #send ACK here
            seq, src, ndest, rdest, dest1, dest2, dest3, data = commonFunctions.decodeDataPkt(receivedPkt)
            pktType = 0x07
            n = 3
            srcID = src
            #Determine Core router runctionality or RP router functionality
            if (dest1 & dest2 & dest3 == 0):
                print("Received data packet from hostSender")
                #Assume Core Router functionality
                #If ndest is 1 unicast message to dest1
                #n from k out of n (hardcoded to 3 for this project)
                selectedRP, selectedDests = selectRP.selectRP(ndest,n,myID,srcID)
                dests = [0] * 3
                dests[0:len(selectedDests)] = selectedDests
                
                if ndest == 1:
                    print("ndest was 1, preparing to send unicast to destination")
                    #send datapkt to dest1
                    selectedRP = 0
                    datapkt = commonFunctions.createDataPacket(pktType, seq, src, ndest, selectedRP, int(dests[0]), int(dests[1]), int(dests[2]), data)
                    nextHop = commonFunctions.getNextHop(myID,dests[0])
                    routerFunctions.sendData(datapkt, nextHop, myID)
                    print("Sent Data Packet with information {} {} {} {} {} {} {} {} {}".format(pktType, seq, src, ndest, selectedRP, dests[0], dests[1], dests[2], data))

                else:
                    print("ndest was {}, preparing to send to RP".format(ndest))
                    #If ndest > 1 then need to send information to RP
                    #Send pkt to selectedRP
                    emptyDests = dests.count(0)
                    ndest = n - emptyDests
                    datapkt = commonFunctions.createDataPacket(pktType, seq, src, ndest, selectedRP, dests[0], dests[1], dests[2], data)
                    nextHop = commonFunctions.getNextHop(myID,selectedRP)
                    routerFunctions.sendData(datapkt, nextHop, myID)
                    print("Sent Data Packet with information {} {} {} {} {} {} {} {} {}".format(pktType, seq, src, ndest, selectedRP, dests[0], dests[1], dests[2], data))
            elif rdest != 0:
                print("router along path to RP, preparing to send forward along message")
                #Forward packet along to RP
                datapkt = receivedPkt
                nextHop = commonFunctions.getNextHop(myID,rdest)
                routerFunctions.sendData(datapkt, nextHop, myID)
                print("Sent Data Packet with information {} {} {} {} {} {} {} {} {}".format(pktType, seq, src, ndest, rdest, dest1, dest2, dest3, data))
            elif ndest == 1:
                print("router along path destination, preparing to send forward along message")
                #Forward packet to dest1 (which is the only destination)
                datapkt = receivedPkt
                nextHop = commonFunctions.getNextHop(myID,dest1)
                routerFunctions.sendData(datapkt, nextHop, myID)
                print("Sent Data Packet with information {} {} {} {} {} {} {} {} {}".format(pktType, seq, src, ndest, rdest, dest1, dest2, dest3, data))
            else:
                print("router along path to multiple destinations, checking to see how to forward message along")
                #Assume RP functionality

                #Get paths for 
                dests = []
                destsPath = []
                for id in (dest for dest in [dest1, dest2, dest3] if dest != 0):
                    dests.append(id)
                    destsPath.append(routerFunctions.getPath(myID,id))
            
                #Check combinations of paths to see if next hop is the same
                lookaheadFlag = []
                index=range(len(destsPath))
                for a, b in itertools.combinations(index, 2):
                    if destsPath[a][0] == destsPath[b][0]:
                        lookaheadFlag.append([a,b])
                    #print("DestPathA {}: {} DestPathB {}: {}".format(a,destPath[a][0], b, destPath[b][0]))

                #Determine how to send packets based on if other destinations
                #have the same next hop
                if len(lookaheadFlag) == len(destsPath):
                    print("all destinations have the same next hop, only sending one data packet")
                    #All messages going to same next hop
                    ndest = len(dests)
                    for ii in range(n - ndest):
                        dests.append(0)
                    datapkt = commonFunctions.createDataPacket(pktType, seq, src, ndest, selectedRP, dests[0], dests[1], dests[2], data)
                    nextHop = commonFunctions.getNextHop(myID,dests[0])
                    routerFunctions.sendData(datapkt, nextHop, myID)
                    print("Sent Data Packet with information {} {} {} {} {} {} {} {} {}".format(pktType, seq, src, ndest, selectedRP, dests[0], dests[1], dests[2], data))
                else:
                    print("need to bifurcate, will split and send messages accordingly")
                    #just send dests[lookaheadFlag[0][0]] and dests[lookaheadFlag[0][1]] to gether but
                    #not the other value
                    #if this condition is hit there will only be one entry in the lookaheadFlag
                    #send(dests[lookaheadFlag[0][0]] and dests[lookaheadFlag[0][1]])
                    ndest = 2
                    datapkt = commonFunctions.createDataPacket(pktType, seq, src, ndest, rdest, dests[lookaheadFlag[0][0]], dests[lookaheadFlag[0][1]], 0, data)
                    nextHop = commonFunctions.getNextHop(myID,dests[lookaheadFlag[0][0]])
                    routerFunctions.sendData(datapkt, nextHop, myID)
                    print("Sent Data Packet with information {} {} {} {} {} {} {} {} {}".format(pktType, seq, src, ndest, rdest, dests[lookaheadFlag[0][0]], dests[lookaheadFlag[0][1]], 0, data))
                    if len(destsPath) == 3:
                        dests.pop(lookaheadFlag[0][0])
                        dests.pop(lookaheadFlag[0][1])
                        ndest = 1
                        datapkt = commonFunctions.createDataPacket(pktType, seq, src, ndest, rdest, dests[0], 0, 0, data)
                        nextHop = commonFunctions.getNextHop(myID,dests[0])
                        routerFunctions.sendData(datapkt, nextHop, myID)
                        print("Sent Data Packet with information {} {} {} {} {} {} {} {} {}".format(pktType, seq, src, ndest, rdest, dests[0], 0, 0, data))

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