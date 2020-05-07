#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, setLogLevel, info
from mininet.cli import CLI
from mininet.node import Node
from mininet.link import Link, TCLink 
from mininet.util import dumpNodeConnections
import threading
import sys, time

import cleanup
from printer import *
from packet import *
#from topoFinal import topoFinal

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class topoFinal( Topo ):
    #Custom topology Example 1
    #Create a Mininet Environment
    def build( self, **_opts ):

        info( "*** Creating Routers\n" )
        
        routers = [ self.addNode( 'r%d' % n, cls=LinuxRouter, 
                    ip='192.168.1.%d/24' % n ) 
                    for n in range(201,203) ]

        info( "*** Creating Router Links\n" )
        self.addLink( routers[routers.index('r201')], routers[routers.index('r202')],
            intfName1='r201-eth0' )

        info( "*** Creating Hosts\n" )
        hosts = [ self.addHost( 'h%d' % n, 
                    ip='192.168.1.%d/24' % n )
                    for n in range(101,104) ]

        info( "*** Creating Host Links\n" )
        self.addLink( hosts[hosts.index('h101')], routers[routers.index('r201')],
            intfName1='h101-eth0' )    
        self.addLink( hosts[hosts.index('h102')], routers[routers.index('r202')],
            intfName1='h102-eth0' )
        self.addLink( hosts[hosts.index('h103')], routers[routers.index('r202')],
            intfName1='h102-eth0' )
    
def run():
    
    #Setup topo and list information
    topo = topoFinal()
    net = Mininet( topo=topo, controller=None, link=TCLink )
    net.start()

    info( "*** Setup routes on all devices" )
    #Host routes
    net['h101'].cmd( 'route add -net 192.168.1.0/24 gw {}'.format(net['r201'].IP()) ) 
    net['h102'].cmd( 'route add -net 192.168.1.0/24 gw {}'.format(net['r202'].IP()) )
    net['h103'].cmd( 'route add -net 192.168.1.0/24 gw {}'.format(net['r202'].IP()) ) 
   
    #Router r201 routes
    net['r201'].cmd( 'ip route add {}/32 dev r201-eth0'.format(net['r202'].IP()) )
    net['r201'].cmd( 'ip route add {}/32 dev r201-eth1'.format(net['h101'].IP()) )

    #Router r202 routes
    net['r202'].cmd( 'ip route add {}/32 dev r202-eth0'.format(net['r201'].IP()) )
    net['r202'].cmd( 'ip route add {}/32 dev r202-eth1'.format(net['h102'].IP()) ) 
    net['r202'].cmd( 'ip route add {}/32 dev r202-eth2'.format(net['h103'].IP()) )
 
    #DEBUGGING INFO    
    info( "\n\n" )
    info( "*** List host IPs\n" )
    get_host_ips(net)
    #info( "*** List all routes\n" )
    #for node in net.hosts:
	#print(node.cmd('route -n'))
    info( "*** Dumping host connections\n" )
    dumpNodeConnections(net.hosts)
    #info( "*** Pinging all devices\n" )
    #net.pingAll()
    
    CLI( net )
    net.stop()

if __name__ == '__main__':
    cleanup.cleanup()
    setLogLevel( 'info' )  # for CLI output
    run()