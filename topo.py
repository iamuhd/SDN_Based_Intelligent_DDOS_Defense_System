from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

class DDoSTopo(Topo):
    def build(self):
        # Switch
        s1 = self.addSwitch('s1')

        # Users (h1, h2, h3, h4, h5, h6)
        h1 = self.addHost('h1', ip='10.0.0.1', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4', mac='00:00:00:00:00:04')
        h5 = self.addHost('h5', ip='10.0.0.5', mac='00:00:00:00:00:05')
        h6 = self.addHost('h6', ip='10.0.0.6', mac='00:00:00:00:00:06')
        # 4. Connect everyone to the switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)
        self.addLink(h5, s1)
        self.addLink(h6, s1)


if __name__ == '__main__':
    topo = DDoSTopo()
    # Connect to the Ryu Controller (Port 6633)
    net = Mininet(topo=topo, controller=RemoteController(name='c0', port=6633), link=TCLink)
    
    net.start()
    print("----------------------------------------------------------------")
    print("Network Ready.")
    print("Users: h1, h2, h3, h4, h5, h6")
    print("----------------------------------------------------------------")
    CLI(net)
    net.stop()
