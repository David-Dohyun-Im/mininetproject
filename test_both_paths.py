#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel
import os
import time

class CustomTopology(Topo):
    def build(self):
        # Add hosts with specific IPs
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
        
        # Path 2: h1-s1-s3-s4-h2
        self.addLink(s1, s3)
        self.addLink(s3, s4)

def test_path_1():
    """Test Path 1: h1 → s1 → s2 → s4 → h2"""
    print("=== TESTING PATH 1: h1 → s1 → s2 → s4 → h2 ===")
    
    # Clear all flows
    for sw in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl del-flows {sw}')
    
    # Add ARP handling for Path 1 switches
    for sw in ['s1', 's2', 's4']:
        os.system(f'ovs-ofctl add-flow {sw} "dl_type=0x0806,actions=flood"')
    
    # Configure Path 1 flow rules
    # s1: in_port=1 → out_port=2, in_port=2 → out_port=1
    os.system('ovs-ofctl add-flow s1 "in_port=1,actions=output:2"')
    os.system('ovs-ofctl add-flow s1 "in_port=2,actions=output:1"')
    
    # s2: in_port=1 → out_port=2, in_port=2 → out_port=1
    os.system('ovs-ofctl add-flow s2 "in_port=1,actions=output:2"')
    os.system('ovs-ofctl add-flow s2 "in_port=2,actions=output:1"')
    
    # s4: in_port=1 → out_port=3, in_port=3 → out_port=1
    os.system('ovs-ofctl add-flow s4 "in_port=1,actions=output:3"')
    os.system('ovs-ofctl add-flow s4 "in_port=3,actions=output:1"')
    
    print("✓ Path 1 flow rules configured")

def test_path_2():
    """Test Path 2: h1 → s1 → s3 → s4 → h2"""
    print("=== TESTING PATH 2: h1 → s1 → s3 → s4 → h2 ===")
    
    # Clear all flows
    for sw in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl del-flows {sw}')
    
    # Add ARP handling for Path 2 switches
    for sw in ['s1', 's3', 's4']:
        os.system(f'ovs-ofctl add-flow {sw} "dl_type=0x0806,actions=flood"')
    
    # Configure Path 2 flow rules
    # s1: in_port=1 → out_port=3, in_port=3 → out_port=1
    os.system('ovs-ofctl add-flow s1 "in_port=1,actions=output:3"')
    os.system('ovs-ofctl add-flow s1 "in_port=3,actions=output:1"')
    
    # s3: in_port=1 → out_port=2, in_port=2 → out_port=1
    os.system('ovs-ofctl add-flow s3 "in_port=1,actions=output:2"')
    os.system('ovs-ofctl add-flow s3 "in_port=2,actions=output:1"')
    
    # s4: in_port=2 → out_port=3, in_port=3 → out_port=2
    os.system('ovs-ofctl add-flow s4 "in_port=2,actions=output:3"')
    os.system('ovs-ofctl add-flow s4 "in_port=3,actions=output:2"')
    
    print("✓ Path 2 flow rules configured")

def main():
    setLogLevel('info')
    
    print("MININET DUAL-PATH MANUAL FLOW DEMONSTRATION")
    print("=" * 50)
    
    # Create topology
    topo = CustomTopology()
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, controller=None)
    
    print("Starting network...")
    net.start()
    time.sleep(2)
    
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # Test Path 1
    test_path_1()
    time.sleep(1)
    result1 = net.ping([h1, h2])
    if result1 == 0:
        print("✓ PATH 1 SUCCESS: h1 → s1 → s2 → s4 → h2")
    else:
        print("✗ PATH 1 FAILED")
    
    print()
    
    # Test Path 2
    test_path_2()
    time.sleep(1)
    result2 = net.ping([h1, h2])
    if result2 == 0:
        print("✓ PATH 2 SUCCESS: h1 → s1 → s3 → s4 → h2")
    else:
        print("✗ PATH 2 FAILED")
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Path 1 (h1 → s1 → s2 → s4 → h2): {'PASS' if result1 == 0 else 'FAIL'}")
    print(f"Path 2 (h1 → s1 → s3 → s4 → h2): {'PASS' if result2 == 0 else 'FAIL'}")
    
    if result1 == 0 and result2 == 0:
        print("🎉 BOTH PATHS WORKING - MANUAL FLOW FORWARDING VERIFIED!")
    
    net.stop()

if __name__ == '__main__':
    main()