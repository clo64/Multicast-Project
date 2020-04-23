import sys
sys.path.append('../')
import idMap
import hostFunctions
import time

if __name__ == "__main__":
    #read the hosts's ID from the command line input -id
    myID = hostFunctions.getID(sys.argv)
    
    #need function here to determine if a host is intended
    #to be a broadcaster or not

    #Wait, then send your hello packet
    
    time.sleep(5)
    #Make hello packet here then it'll send
    #hostFunctions.sendHelloPacket()

    #while True:
        #hostFunctions.receive_packet('0.0.0.0', 8888)