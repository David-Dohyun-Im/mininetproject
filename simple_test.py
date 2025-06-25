#\!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel
import os
import time

class SimpleTopology(Topo):
    def build(self):
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        s1 = self.addSwitch('s1')
        
        # Simple direct connection
        self.addLink(h1, s1)
        self.addLink(h2, s1)

def test():
    setLogLevel('info')
    topo = SimpleTopology()
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, controller=None)
    
    print("Starting simple test network...")
    net.start()
    time.sleep(2)
    
    # Check ports
    print("\ns1 ports:")
    result = os.popen('ovs-ofctl show s1').read()
    print(result)
    
    # Clear flows and add simple rules
    os.system('ovs-ofctl del-flows s1')
    os.system('ovs-ofctl add-flow s1 "dl_type=0x0806,actions=flood"')  # ARP
    os.system('ovs-ofctl add-flow s1 "in_port=1,actions=output:2"')   # h1 to h2
    os.system('ovs-ofctl add-flow s1 "in_port=2,actions=output:1"')   # h2 to h1
    
    print("\nTesting ping...")
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    result = net.ping([h1, h2])
    if result == 0:
        print("✓ Simple test PASSED!")
    else:
        print("✗ Simple test FAILED")
        print("Flow table:")
        flows = os.popen('ovs-ofctl dump-flows s1').read()
        print(flows)
    
    net.stop()

if __name__ == '__main__':
    test()
