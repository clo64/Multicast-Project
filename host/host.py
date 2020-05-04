import sys
sys.path.append('../')
import commonFunctions
import hostFunctions
import time
import struct
import os, subprocess

if __name__ == "__main__":

    #read the hosts's ID from the command line input -id
    myID = int(commonFunctions.getID())

    #host maintains and broadcasts it's single link state
    #does not maintain data about the rest of the network
    myLink = {str(myID): []}
    
    #Maybe, need function here to setup particular host as the
    #broadcast node or not

    #create hello packet
    pkttype = 0x01
    src = myID
    #print("src is : ".format(src))
    seq = 0x01
    hello = struct.pack('BBB', pkttype, seq, src)
    #hello = hostFunctions.createHelloPacket()
    #Sends hello on its broadcast IP address
    data, addr, myLink = hostFunctions.sendHelloPacket(commonFunctions.convertID(myID), hello, '192.168.1.255', myLink, myID)
    
    hostFunctions.broadcastLinkState(myID, '192.168.1.255', myLink)

    while True:
        
        data = hostFunctions.receive_packet('0.0.0.0', 8888)

