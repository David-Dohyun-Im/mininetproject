from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel

def setup():
    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink)

    # Create hosts and switches
    # <Your codes here>

    # Set up links: h1 - s1 - s2 or s3 - s4 - h2
    # <Your codes here>
    net.start()

    # Get nodes by name: h1, h2, s1~s4
    # <Your codes here>

    # Clear flow tables on all switches (using ovs-ofctl del-flows)
    # <Your codes here>

    # Manually add flow entries for the path: h1 -> s1 -> s2 or s3 -> s4 -> h2
    # (Use ovs-ofctl add-flow command, check port mapping with net.linksBetween)
    # <Your codes here>

    # Run the server on h2 and the client on h1 (include copying send_file.txt)
    # <Your codes here>

    # Print the contents of received_file.txt from h2
    # <Your codes here>

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup()
