import time
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import select
import random
import asyncore
import threading

#Get ID from the command line
def getID(argv):
    for i, arg in enumerate(argv):
        if(arg=="-id"):
            return argv[i+1]

def sendHelloPacket(pkt, dstAddr):
    # """
    # Sends a packet to the dest_addr using the UDP socket
    # """
    my_socket = socket(AF_INET, SOCK_DGRAM)
    my_socket.sendto(pkt, (dst_addr, 8889))
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
