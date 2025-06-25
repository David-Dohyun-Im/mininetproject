#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import os
import time

class DualPathTopo(Topo):
    def build(self):
        # Add hosts with explicit MAC addresses
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        
        # Add links for dual-path topology
        # Path 1: h1 → s1 → s2 → s4 → h2
        # Path 2: h1 → s1 → s3 → s4 → h2
        self.addLink(h1, s1)  # h1-s1 
        self.addLink(s1, s2)  # s1-s2 (path 1)
        self.addLink(s1, s3)  # s1-s3 (path 2)
        self.addLink(s2, s4)  # s2-s4 (path 1 continues)
        self.addLink(s3, s4)  # s3-s4 (path 2 continues)
        self.addLink(s4, h2)  # s4-h2

def configure_path1(net):
    """Configure Path 1: h1 → s1 → s2 → s4 → h2"""
    print("Configuring Path 1: h1 → s1 → s2 → s4 → h2")
    
    # Clear all flows first
    for sw in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl del-flows {sw}')
    
    # Common ARP handling for all switches
    for sw in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl add-flow {sw} "priority=200,dl_type=0x0806,actions=flood"')
        os.system(f'ovs-ofctl add-flow {sw} "priority=0,actions=drop"')
    
    # s1: Forward to s2 (port 2) for path 1
    os.system('ovs-ofctl add-flow s1 "priority=100,in_port=1,dl_dst=00:00:00:00:00:02,actions=output:2"')  # h1 to s2
    os.system('ovs-ofctl add-flow s1 "priority=100,in_port=2,dl_dst=00:00:00:00:00:01,actions=output:1"')  # s2 back to h1
    
    # s2: Forward between s1 and s4
    os.system('ovs-ofctl add-flow s2 "priority=100,in_port=1,dl_dst=00:00:00:00:00:02,actions=output:2"')  # s1 to s4
    os.system('ovs-ofctl add-flow s2 "priority=100,in_port=2,dl_dst=00:00:00:00:00:01,actions=output:1"')  # s4 back to s1
    
    # s4: Forward from s2 to h2, and back
    os.system('ovs-ofctl add-flow s4 "priority=100,in_port=1,dl_dst=00:00:00:00:00:02,actions=output:3"')  # s2 to h2
    os.system('ovs-ofctl add-flow s4 "priority=100,in_port=3,dl_dst=00:00:00:00:00:01,actions=output:1"')  # h2 back to s2
    
    # s3: Not used in path 1, but handle ARP
    print("Path 1 configured: h1 → s1 → s2 → s4 → h2")

def configure_path2(net):
    """Configure Path 2: h1 → s1 → s3 → s4 → h2"""
    print("Configuring Path 2: h1 → s1 → s3 → s4 → h2")
    
    # Clear all flows first
    for sw in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl del-flows {sw}')
    
    # Common ARP handling for all switches
    for sw in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl add-flow {sw} "priority=200,dl_type=0x0806,actions=flood"')
        os.system(f'ovs-ofctl add-flow {sw} "priority=0,actions=drop"')
    
    # s1: Forward to s3 (port 3) for path 2
    os.system('ovs-ofctl add-flow s1 "priority=100,in_port=1,dl_dst=00:00:00:00:00:02,actions=output:3"')  # h1 to s3
    os.system('ovs-ofctl add-flow s1 "priority=100,in_port=3,dl_dst=00:00:00:00:00:01,actions=output:1"')  # s3 back to h1
    
    # s3: Forward between s1 and s4
    os.system('ovs-ofctl add-flow s3 "priority=100,in_port=1,dl_dst=00:00:00:00:00:02,actions=output:2"')  # s1 to s4
    os.system('ovs-ofctl add-flow s3 "priority=100,in_port=2,dl_dst=00:00:00:00:00:01,actions=output:1"')  # s4 back to s1
    
    # s4: Forward from s3 to h2, and back
    os.system('ovs-ofctl add-flow s4 "priority=100,in_port=2,dl_dst=00:00:00:00:00:02,actions=output:3"')  # s3 to h2
    os.system('ovs-ofctl add-flow s4 "priority=100,in_port=3,dl_dst=00:00:00:00:00:01,actions=output:2"')  # h2 back to s3
    
    # s2: Not used in path 2, but handle ARP
    print("Path 2 configured: h1 → s1 → s3 → s4 → h2")

def test_path(net, path_num):  
    """Test connectivity for a specific path"""
    print(f"\n=== Testing Path {path_num} ===")
    h1, h2 = net.get('h1', 'h2')
    
    # Clear ARP tables
    h1.cmd('arp -d 10.0.0.2')
    h2.cmd('arp -d 10.0.0.1')
    
    # Test ping
    result = h1.cmd('ping -c 3 10.0.0.2')
    
    if "0% packet loss" in result:
        print(f"✅ Path {path_num} SUCCESS: Connectivity works!")
        return True
    else:
        print(f"❌ Path {path_num} FAILED")
        print(f"Ping output: {result}")
        return False

def main():
    setLogLevel('info')
    
    topo = DualPathTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, controller=None)
    
    net.start()
    time.sleep(2)
    
    print("Topology created:")
    print("h1 (10.0.0.1) -- s1 -- s2 -- s4 -- h2 (10.0.0.2)")
    print("                 |           |")
    print("                 s3 ---------")
    print("\nAvailable paths:")
    print("Path 1: h1 → s1 → s2 → s4 → h2")
    print("Path 2: h1 → s1 → s3 → s4 → h2")
    
    # Test Path 1
    configure_path1(net)
    time.sleep(1)
    path1_success = test_path(net, 1)
    
    # Wait between tests
    time.sleep(2)
    
    # Test Path 2
    configure_path2(net)
    time.sleep(1)
    path2_success = test_path(net, 2)
    
    print(f"\n=== Results ===")
    print(f"Path 1 (h1 → s1 → s2 → s4 → h2): {'✅ WORKS' if path1_success else '❌ FAILED'}")
    print(f"Path 2 (h1 → s1 → s3 → s4 → h2): {'✅ WORKS' if path2_success else '❌ FAILED'}")
    
    if path1_success or path2_success:
        print("\n🎉 At least one path is working! Your dual-path topology is functional.")
        
        while True:
            choice = input("\nChoose path to configure (1/2) or 'cli' for manual testing: ").strip()
            if choice == '1':
                configure_path1(net)
                print("Path 1 configured and active")
            elif choice == '2':
                configure_path2(net)
                print("Path 2 configured and active")
            elif choice.lower() == 'cli':
                print("Starting CLI...")
                CLI(net)
                break
            else:
                print("Invalid choice. Enter 1, 2, or 'cli'")
    else:
        print("\n❌ Both paths failed. Starting CLI for debugging...")
        CLI(net)
    
    net.stop()

if __name__ == '__main__':
    main()