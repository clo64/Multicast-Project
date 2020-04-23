from mininet.net import Mininet
from mininet.log import lg, info, setLogLevel
from mininet.cli import CLI
from mininet.node import Node
from mininet.link import Link, TCLink, TCIntf

net = Mininet()

r1 = net.addHost( 'r1' )
h1 = net.addHost( 'h1' )

net.build()

setLogLevel( 'info' )
CLI(net)