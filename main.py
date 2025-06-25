#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel
import os
import time
import threading
import subprocess
import sys

class CustomTopology(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        
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

def configure_flow_rules(net):
    """Configure flow rules for all switches to enable both paths"""
    
    print("\n=== Configuring OpenFlow Rules ===")
    
    # Clear existing flow tables
    for switch in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl del-flows {switch}')
        print(f"Cleared flow table for {switch}")
    
    # Switch s1 flow rules
    os.system('ovs-ofctl add-flow s1 "in_port=1,dl_dst=00:00:00:00:00:02,actions=output:2"')
    os.system('ovs-ofctl add-flow s1 "in_port=1,dl_dst=00:00:00:00:00:02,actions=output:3"')
    os.system('ovs-ofctl add-flow s1 "in_port=2,dl_dst=00:00:00:00:00:01,actions=output:1"')
    os.system('ovs-ofctl add-flow s1 "in_port=3,dl_dst=00:00:00:00:00:01,actions=output:1"')
    print("Configured flow rules for s1")
    
    # Switch s2 flow rules (path 1: s1-s2-s4)
    os.system('ovs-ofctl add-flow s2 "in_port=1,dl_dst=00:00:00:00:00:02,actions=output:2"')
    os.system('ovs-ofctl add-flow s2 "in_port=2,dl_dst=00:00:00:00:00:01,actions=output:1"')
    print("Configured flow rules for s2")
    
    # Switch s3 flow rules (path 2: s1-s3-s4)
    os.system('ovs-ofctl add-flow s3 "in_port=1,dl_dst=00:00:00:00:00:02,actions=output:2"')
    os.system('ovs-ofctl add-flow s3 "in_port=2,dl_dst=00:00:00:00:00:01,actions=output:1"')
    print("Configured flow rules for s3")
    
    # Switch s4 flow rules
    os.system('ovs-ofctl add-flow s4 "in_port=1,dl_dst=00:00:00:00:00:02,actions=output:3"')
    os.system('ovs-ofctl add-flow s4 "in_port=2,dl_dst=00:00:00:00:00:02,actions=output:3"')
    os.system('ovs-ofctl add-flow s4 "in_port=3,dl_dst=00:00:00:00:00:01,actions=output:1,output:2"')
    print("Configured flow rules for s4")
    
    # Add ARP handling rules for all switches
    for switch in ['s1', 's2', 's3', 's4']:
        os.system(f'ovs-ofctl add-flow {switch} "dl_type=0x0806,actions=flood"')
    
    print("Flow rules configured successfully!")

def create_test_file():
    """Create test file for transfer"""
    test_content = """This is a test file for Mininet file transfer testing.

Network topology demonstration:
h1 (10.0.0.1) -- s1 -- s2 -- s4 -- h2 (10.0.0.2)
                 |           |
                 s3 ---------

Available paths:
Path 1: h1 → s1 → s2 → s4 → h2
Path 2: h1 → s1 → s3 → s4 → h2

Test data: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
Binary test data follows...
""" + ''.join(chr(i) for i in range(256)) + """

End of test file - transfer complete!
"""
    
    os.makedirs('/tmp', exist_ok=True)
    with open('/tmp/send_file.txt', 'w') as f:
        f.write(test_content)
    
    file_size = os.path.getsize('/tmp/send_file.txt')
    print(f"Created test file: /tmp/send_file.txt ({file_size} bytes)")
    return file_size

def verify_transfer():
    """Verify file transfer success"""
    print("\n=== File Transfer Verification ===")
    
    original_file = '/tmp/send_file.txt'
    received_file = '/tmp/send_file.txt.1'
    
    if not os.path.exists(original_file):
        print(f"ERROR: Original file not found: {original_file}")
        return False
    
    if not os.path.exists(received_file):
        print(f"ERROR: Received file not found: {received_file}")
        return False
    
    # Compare file sizes
    orig_size = os.path.getsize(original_file)
    recv_size = os.path.getsize(received_file)
    
    print(f"Original file size: {orig_size} bytes")
    print(f"Received file size: {recv_size} bytes")
    
    if orig_size != recv_size:
        print("✗ ERROR: File sizes do not match!")
        return False
    
    print("✓ File sizes match")
    
    # Compare file contents
    try:
        with open(original_file, 'rb') as f1, open(received_file, 'rb') as f2:
            if f1.read() == f2.read():
                print("✓ File contents match perfectly")
                print("SUCCESS: File transfer completed successfully!")
                return True
            else:
                print("✗ ERROR: File contents do not match!")
                return False
    except Exception as e:
        print(f"ERROR: Failed to compare files: {e}")
        return False

def cleanup_files():
    """Clean up test files"""
    files_to_clean = ['/tmp/send_file.txt', '/tmp/send_file.txt.1', '/tmp/send_file.txt.2']
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up: {file_path}")

def run_automated_test(net):
    """Run automated file transfer test"""
    print("\n" + "="*60)
    print("STARTING AUTOMATED FILE TRANSFER TEST")
    print("="*60)
    
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # Create test file
    file_size = create_test_file()
    
    print("\n=== Starting Server on h2 ===")
    # Start server on h2 in background
    server_cmd = 'cd /home/dohyun11111m/mininetproject && python server.py'
    server_process = h2.popen(server_cmd, shell=True)
    
    # Give server time to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    print("\n=== Testing Connectivity ===")
    # Test basic connectivity
    result = net.ping([h1, h2], timeout='1')
    if result > 0:
        print("WARNING: Basic ping test failed")
    else:
        print("✓ Basic connectivity confirmed")
    
    print("\n=== Starting Client on h1 ===")
    # Start client on h1
    client_cmd = 'cd /home/dohyun11111m/mininetproject && python client.py'
    print(f"Executing: {client_cmd}")
    
    try:
        client_result = h1.cmd(client_cmd)
        print("Client output:")
        print(client_result)
        
        # Give some time for file transfer to complete
        time.sleep(2)
        
        # Verify transfer
        success = verify_transfer()
        
        if success:
            print(f"\n🎉 SUCCESS: File transfer test completed successfully! 🎉")
            print(f"Transferred {file_size} bytes from h1 to h2 via dual-path network")
        else:
            print(f"\n❌ FAILED: File transfer test failed")
            
    except Exception as e:
        print(f"ERROR during client execution: {e}")
        success = False
    
    finally:
        # Stop server
        try:
            server_process.terminate()
            server_process.wait()
            print("Server stopped")
        except:
            pass
    
    return success

def setup():
    # Set log level
    setLogLevel('info')
    
    print("="*60)
    print("MININET DUAL-PATH FILE TRANSFER DEMONSTRATION")
    print("="*60)
    
    # Create topology
    topo = CustomTopology()
    
    # Create network with OVS switches and TC links
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, controller=None)
    
    # Start network
    print("\n=== Starting Mininet Network ===")
    net.start()
    
    # Configure flow rules
    configure_flow_rules(net)
    
    print("\nNetwork topology:")
    print("h1 (10.0.0.1) -- s1 -- s2 -- s4 -- h2 (10.0.0.2)")
    print("                 |           |")
    print("                 s3 ---------")
    print("\nTwo paths available:")
    print("Path 1: h1 → s1 → s2 → s4 → h2")
    print("Path 2: h1 → s1 → s3 → s4 → h2")
    
    try:
        # Run automated test
        test_success = run_automated_test(net)
        
        print("\n" + "="*60)
        if test_success:
            print("AUTOMATED TEST: PASSED ✓")
        else:
            print("AUTOMATED TEST: FAILED ✗")
        print("="*60)
        
        # Ask user if they want to access CLI
        print(f"\nTest completed. Network is still running.")
        print("Options:")
        print("1. Press Enter to access Mininet CLI for manual testing")
        print("2. Press Ctrl+C to exit")
        
        try:
            input()
            print("\nStarting Mininet CLI...")
            print("Available commands:")
            print("  pingall        - Test connectivity")
            print("  dump           - Show network configuration") 
            print("  h1 python client.py  - Run client manually")
            print("  h2 python server.py  - Run server manually")
            CLI(net)
        except KeyboardInterrupt:
            print("\nSkipping CLI, shutting down...")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    finally:
        print("\n=== Cleaning Up ===")
        cleanup_files()
        net.stop()
        print("Network stopped and cleanup completed")

if __name__ == '__main__':
    try:
        setup()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
        sys.exit(1)