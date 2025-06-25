#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel
import os
import time

class CustomTopology(Topo):
    def build(self):
        # Add hosts with specific MAC addresses
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        
        # Add links to create dual paths
        # Path 1: h1-s1-s2-s4-h2
        self.addLink(h1, s1)
        self.addLink(s1, s2)
        self.addLink(s2, s4)
        self.addLink(s4, h2)
        
        # Path 2: h1-s1-s3-s4-h2 (s1-s3 and s3-s4 links)
        self.addLink(s1, s3)
        self.addLink(s3, s4)

def debug_ports():
    setLogLevel('info')
    
    # Create topology
    topo = CustomTopology()
    
    # Create network with OVS switches and TC links
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, controller=None)
    
    # Start network
    print("Starting network...")
    net.start()
    
    # Wait for network to be ready
    time.sleep(2)
    
    print("\n=== DEBUGGING PORT ASSIGNMENTS ===")
    
    # Check port assignments for each switch
    for switch in ['s1', 's2', 's3', 's4']:
        print(f"\n{switch} ports:")
        result = os.popen(f'ovs-ofctl show {switch}').read()
        print(result)
    
    print("\n=== APPLYING SIMPLE PORT-BASED RULES ===")
    
    # Clear all flows
    for sw in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl del-flows {sw}')
    
    # Add ARP handling
    for sw in ['s1', 's2', 's4']:
        os.system(f'ovs-ofctl add-flow {sw} "dl_type=0x0806,actions=flood"')
    
    # Configure Path 1 based on actual port assignments
    # s1: h1 is port 1, s2 is port 2, s3 is port 3
    os.system('ovs-ofctl add-flow s1 "in_port=1,actions=output:2"')  # h1 to s2
    os.system('ovs-ofctl add-flow s1 "in_port=2,actions=output:1"')  # s2 back to h1
    
    # s2: s1 is port 1, s4 is port 2
    os.system('ovs-ofctl add-flow s2 "in_port=1,actions=output:2"')  # s1 to s4
    os.system('ovs-ofctl add-flow s2 "in_port=2,actions=output:1"')  # s4 back to s1
    
    # s4: s2 is port 1, s3 is port 2, h2 is port 3
    os.system('ovs-ofctl add-flow s4 "in_port=1,actions=output:3"')  # s2 to h2
    os.system('ovs-ofctl add-flow s4 "in_port=3,actions=output:1"')  # h2 back to s2
    
    print("Flow rules applied!")
    
    print("\n=== TESTING CONNECTIVITY ===")
    
    # Test ping
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    result = net.ping([h1, h2])
    if result == 0:
        print("✓ Ping successful!")
    else:
        print("✗ Ping failed")
        
        # Debug: Check flow tables
        print("\nChecking flow tables:")
        for sw in ['s1', 's2', 's4']:
            print(f"\n{sw} flows:")
            flow_result = os.popen(f'ovs-ofctl dump-flows {sw}').read()
            print(flow_result)
    
    print("\nStarting CLI for manual testing...")
    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    debug_ports()