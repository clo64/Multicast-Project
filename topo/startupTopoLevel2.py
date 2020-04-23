
import sys
sys.path.append('../')
import idMap
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class NetworkTopo( Topo ):

      def build( self, **_opts ):
          
          #h1 r0 relationship
          r0 = self.addNode( 'r0', cls=LinuxRouter, ip=idMap.code_to_IP(200) )
          h1 = self.addHost( 'h1', ip=idMap.code_to_IP(100), defaultRoute='via ' + idMap.code_to_IP(200) )
          self.addLink( h1, r0, intfName2='r0-eth1', params2={ 'ip' : idMap.code_to_IP(200) + '/24' } )

def run():
    
    topo = NetworkTopo()
    net = Mininet( topo=topo, controller=None )
    net.start()

    info( '*** Routing Table on Router:\n' )
    print net[ 'r0' ].cmd( 'route' )
    #print net[ 'r0' ].cmd('ip route add 192.168.3.0/24 dev r0-eth0')

    CLI( net )

    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()