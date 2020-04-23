import routerFunctions
import time
import threading
import sys
import struct

if __name__ == "__main__":
    
    #read the router's ID from the command line input -id
    myID = routerFunctions.getID(sys.argv)

    #initializes Link State transmission to occur every 10 seconds
    routerFunctions.sendLinkState()

    while True:
        #listen on all ports logic here
        receivedPkt = routerFunctions.receive_packet('0.0.0.0', 8888)
        
        #Size 36 bytes, received a hello packet
        #Respond with an ACK
        if(sys.getsizeof(receivedPkt) == 36):
            helloType, helloSeq, helloSrc = routerFunctions.read_hello(receivedPkt)
            #Call a function to DO something with the SRC you got.
            #Send an ACK here.. ??
            routerFunctions.sendHelloACK(helloSrc)
            

        #decode
        #pkttype, pktlen, dst, src, seq = routerFunctions.read_header(receivedPkt)
