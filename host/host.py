import sys
sys.path.append('../')
import idMap
import hostFunctions
import time

if __name__ == "__main__":
    #read the hosts's ID from the command line input -id
    myID = hostFunctions.getID(sys.argv)
    myID = int(myID)

    routerID = hostFunctions.getRouterID(sys.argv)
    routerID = int(routerID)
    
    #need function here to setup particular host as the
    #broadcast node or not

    #blocking call function that will send hello packet
    #until ack received
    hello = b'Hello'
    hostFunctions.sendHelloPacket(idMap.code_to_IP(myID), hello, idMap.code_to_IP(routerID))

    #while True:
        
        #hostFunctions.receive_packet('0.0.0.0', 8888)