import sys
sys.path.append('../')
import idMap
import hostFunctions
import commonFunctions
import time
import struct
import os, subprocess

if __name__ == "__main__":
    #read the hosts's ID from the command line input -id
    #myID = hostFunctions.getID(sys.argv)
    #myID = int(myID)
    myID = int(commonFunctions.getIP())
    #print("My IP is: {}".format(hostFunctions.convertID(myID)))
    
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
    #data, addr = hostFunctions.sendHelloPacket(idMap.code_to_IP(myID), hello, '192.168.1.255')
    data, addr = hostFunctions.sendHelloPacket(commonFunctions.convertID(myID), hello, '192.168.1.255')

    while True:
        
        data = hostFunctions.receive_packet('0.0.0.0', 8888)

