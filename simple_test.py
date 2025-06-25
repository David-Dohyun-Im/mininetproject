#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import os
import time

class SimpleTopo(Topo):
    def build(self):
        # Add hosts with explicit MAC addresses
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        
        # Add links exactly as described
        self.addLink(h1, s1)  # h1-s1
        self.addLink(s1, s2)  # s1-s2 (path 1)
        self.addLink(s1, s3)  # s1-s3 (path 2)  
        self.addLink(s2, s4)  # s2-s4
        self.addLink(s3, s4)  # s3-s4
        self.addLink(s4, h2)  # s4-h2

def setup_simple_flows():
    """Setup simple learning switch with manual forwarding"""
    print("Setting up simple flows...")
    
    # Clear all flows
    for sw in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl del-flows {sw}')
    
    # Just use normal learning switch behavior
    for sw in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl add-flow {sw} "actions=normal"')
    
    print("Simple flows configured")

def main():
    setLogLevel('info')
    
    topo = SimpleTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, controller=None)
    
    net.start()
    time.sleep(2)
    
    setup_simple_flows() 
    time.sleep(1)
    
    print("\n=== Testing simple connectivity ===")
    h1, h2 = net.get('h1', 'h2')
    
    # Check IPs and MACs
    print(f"h1: IP={h1.IP()}, MAC={h1.cmd('cat /sys/class/net/h1-eth0/address').strip()}")
    print(f"h2: IP={h2.IP()}, MAC={h2.cmd('cat /sys/class/net/h2-eth0/address').strip()}")
    
    # Test ping
    result = h1.cmd('ping -c 3 10.0.0.2')
    print(f"Ping result:\n{result}")
    
    if "0% packet loss" in result:
        print("✅ SUCCESS: Basic connectivity works!")
    else:
        print("❌ FAILED: Still no connectivity")
    
    print("\nStarting CLI for manual testing...")
    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    main()