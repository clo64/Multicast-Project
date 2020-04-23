import routerFunctions
import time
import threading
import sys

if __name__ == "__main__":
    #read the router's ID from the command line input -id
    myID = routerFunctions.getID(sys.argv)

    #initializes Link State transmission to occur every 10 seconds
    routerFunctions.sendLinkState()

    while True:
        #listen on all ports logic here
        receivedPkt = routerFunctions.receive_packet('0.0.0.0', 8888)

        #decode
        pkttype, pktlen, dst, src, seq = routerFunctions.read_header(receivedPkt)

        print()