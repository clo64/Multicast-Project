import time
import sys
sys.path.append('../')
import idMap
import commonFunctions
from socket import *
import struct
import select
import random
import asyncore
import threading
import subprocess

#Get ID from the command line
def getID(argv):
    for i, arg in enumerate(argv):
        if(arg=="-id"):
            return argv[i+1]

def getRouterID(argv):
    for i, arg in enumerate(argv):
        if(arg=="-rid"):
            return argv[i+1]

def createHelloPacket(pkttype, seq, src):
    """Create a new packet based on given id"""
    # Type(1), SEQ(4), SRCID(1) 
    hello = struct.pack('BBB', pkttype, seq, src)
    return hello

def sendHelloPacket(my_addr, pkt, dst):
    helloAckFlag = False
    my_socket = socket(AF_INET, SOCK_DGRAM)    
    my_socket.settimeout(4)
    print("Socket Timeout Set")

    while (not helloAckFlag):
        my_socket = socket(AF_INET, SOCK_DGRAM)
        my_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) 
        my_socket.sendto(pkt, (dst, 8888))
        my_socket.close()
        print("Sent packet to the destination: " + dst)
        #send_packet(pkt, dst)
        print("Hello Sent, waiting for ACK")
        time.sleep(1)
        #my_socket.bind((my_addr, 8889))
        my_socket = socket(AF_INET, SOCK_DGRAM)   
        my_socket.settimeout(4)
        my_socket.bind((my_addr, 8888))
        #Hello ACK type set as 4, listening to hear this value
        try:
            print("Listening for Hello ACK")
            data, addr = my_socket.recvfrom(1024)
            pktType = decodePktType(data)
            if (pktType[0] == 4):
                print("Hello ACK Received")
                print("Network joined")
                helloAckFlag = True
        except:
            continue
    return data, addr

def send_packet(pkt, dst_addr):
    # """
    # Sends a packet to the dest_addr using the UDP socket
    # """
    my_socket = socket(AF_INET, SOCK_DGRAM)
    my_socket.sendto(pkt, (dst_addr, 8888))
    my_socket.close()
    print("Sent packet to the destination: ", dst_addr)
    return 0

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

def decodePktType(pkt):
    pktType = pkt[0:1]
    pkttype = struct.unpack('B', pktType)
    return pkttype 