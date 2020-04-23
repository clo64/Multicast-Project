import time
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import select
import random
import asyncore
import threading

#Get ID from the command line
#No error checking, so don't screw it up. 
def getID(argv):
    for i, arg in enumerate(argv):
        if(arg=="-id"):
            return argv[i+1]

#logic for sending Link State packets here
def sendLinkState():
    print("Sending Link State")
    #Actual send link state logic in here now
    threading.Timer(10, sendLinkState).start()

def receive_packet(my_addr, port_num):
    # """
    # Listens at an IP:port
    # """
    my_socket = socket(AF_INET, SOCK_DGRAM)
    my_socket.bind((my_addr, port_num))
    while True:
        data, addr = my_socket.recvfrom(1024)
        #print("Received packet", data, "from source", addr)
        break
    return data
    
