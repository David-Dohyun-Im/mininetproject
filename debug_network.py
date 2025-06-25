#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController
import os

class DualPathTopo(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        
        # Add links
        self.addLink(h1, s1)  # h1-s1
        self.addLink(s1, s2)  # s1-s2 (path 1)
        self.addLink(s1, s3)  # s1-s3 (path 2)
        self.addLink(s2, s4)  # s2-s4
        self.addLink(s3, s4)  # s3-s4
        self.addLink(s4, h2)  # s4-h2

def setup_flows():
    print("=== Setting up OpenFlow rules ===")
    
    # Clear existing flows
    for switch in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl del-flows {switch}')
    
    # Simple learning switch behavior + specific rules
    for switch in ['s1', 's2', 's3', 's4']:
        # Allow ARP
        os.system(f'ovs-ofctl add-flow {switch} "dl_type=0x0806,actions=flood"')
        # Default drop
        os.system(f'ovs-ofctl add-flow {switch} "priority=0,actions=drop"')
    
    # Specific forwarding rules
    # s1: from h1 to both paths, from switches to h1
    os.system('ovs-ofctl add-flow s1 "priority=100,in_port=1,dl_dst=00:00:00:00:00:02,actions=output:2"')
    os.system('ovs-ofctl add-flow s1 "priority=100,in_port=2,dl_dst=00:00:00:00:00:01,actions=output:1"')
    os.system('ovs-ofctl add-flow s1 "priority=100,in_port=3,dl_dst=00:00:00:00:00:01,actions=output:1"')
    
    # s2: forward between s1 and s4
    os.system('ovs-ofctl add-flow s2 "priority=100,in_port=1,dl_dst=00:00:00:00:00:02,actions=output:2"')
    os.system('ovs-ofctl add-flow s2 "priority=100,in_port=2,dl_dst=00:00:00:00:00:01,actions=output:1"')
    
    # s3: forward between s1 and s4
    os.system('ovs-ofctl add-flow s3 "priority=100,in_port=1,dl_dst=00:00:00:00:00:02,actions=output:2"')
    os.system('ovs-ofctl add-flow s3 "priority=100,in_port=2,dl_dst=00:00:00:00:00:01,actions=output:1"')
    
    # s4: from switches to h2, from h2 to both switches
    os.system('ovs-ofctl add-flow s4 "priority=100,in_port=1,dl_dst=00:00:00:00:00:02,actions=output:3"')
    os.system('ovs-ofctl add-flow s4 "priority=100,in_port=2,dl_dst=00:00:00:00:00:02,actions=output:3"')
    os.system('ovs-ofctl add-flow s4 "priority=100,in_port=3,dl_dst=00:00:00:00:00:01,actions=output:1"')
    
    print("OpenFlow rules configured")

def main():
    setLogLevel('info')
    
    topo = DualPathTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None)
    
    net.start()
    
    # Wait a bit for switches to come up
    import time
    time.sleep(2)
    
    setup_flows()
    
    print("\n=== Testing connectivity ===")
    print("Ping test:")
    result = net.pingAll()
    
    print(f"\n=== Checking interfaces ===")
    h1, h2 = net.get('h1', 'h2')
    print(f"h1 IP: {h1.IP()}")
    print(f"h2 IP: {h2.IP()}")
    
    print(f"\n=== Manual ping test ===")
    result = h1.cmd('ping -c 3 10.0.0.2')
    print(f"h1 ping h2: {result}")
    
    print("\nStarting CLI for manual testing...")
    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    main()