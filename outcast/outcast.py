#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, output
from mininet.node import CPULimitedHost
from mininet.node import Controller
from mininet.link import TCLink
from mininet.util import irange, custom, quietRun, dumpNetConnections
from mininet.cli import CLI

from time import sleep, time
from multiprocessing import Process
from subprocess import Popen
# import termcolor as T
import argparse

import sys
import os
from util.monitor import monitor_devs_ng

def cprint(s, color, cr=True):
    """Print in color
       s: string to print
       color: color to use"""
    # if cr:
    #     print(T.colored(s, color))
    # else:
    #     print(T.colored(s, color))

parser = argparse.ArgumentParser(description="Outcast tests")
parser.add_argument('--bw', '-b',
                    type=float,
                    help="Bandwidth of network links",
                    required=True)

parser.add_argument('--dir', '-d',
                    help="Directory to store outputs",
                    default="results")

parser.add_argument('-n',
                    type=int,
                    help=("Number of senders"
                    "Must be >= 1"),
                    required=True)

parser.add_argument('--cli', '-c',
                    action='store_true',
                    help='Run CLI for topology debugging purposes')

parser.add_argument('--time', '-t',
                    dest="time",
                    type=int,
                    help="Duration of the experiment.",
                    default=60)

parser.add_argument('--routing', '-r',
                    dest="routing",
                    help="Routing to use.",
                    default="hashed")

# Expt parameters
args = parser.parse_args()

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')

# Topology to be instantiated in Mininet
class OutcastTopo(Topo):
    "Parking Lot Topology"
    def __init__(self, n=1, cpu=.1, bw=10, delay=None,max_queue_size=None, **params):
        """Outcast topology with one receiver
        and n clients.
        n: number of clients
        cpu: system fraction for each host
        bw: link bandwidth in Mb/s
        delay: link delay (e.g. 10ms)"""
        # Initialize topo
        Topo.__init__(self, **params)
        # Host and link configuration
        hconfig = {'cpu': cpu}
        lconfig = {'bw': bw, 'delay': delay,'max_queue_size': max_queue_size }
        # Create the actual topology
        receiver = self.addHost('receiver')
        # Switch ports 1:uplink 2:hostlink 3:downlink
        h0Switch, aggrSwitchPort, switchRec = 1, 2, 3
        #small sender
        h0 = self.addHost('h0', **hconfig)
        s1 = self.addSwitch('s1')
        aggrSwitch = self.addSwitch('s2')
        for i in range(1, n+1):
            h = self.addHost('h'+str(i), **hconfig)
            self.addLink(h, aggrSwitch, port1=0, port2=i+1, **lconfig)    
	
        self.addLink(h0, s1, port1=0, port2=h0Switch, **lconfig)
        self.addLink(aggrSwitch, s1, port1=1, port2=aggrSwitchPort, **lconfig)
        # self.addLink(s1, receiver, port1=switchRec, port2=0, **lconfig)
        self.addLink(receiver, s1, port1=0, port2=switchRec, **lconfig)


        # Uncomment the next 8 lines to create a N = 3 parking lot topology
        #s2 = self.add_switch('s2')
        #h2 = self.add_host('h2', **hconfig)
        #self.add_link(s1, s2,
        #              port1=downlink, port2=uplink, **lconfig)
        #self.add_link(h2, s2,
        #              port1=0, port2=hostlink, **lconfig)
        #s3 = self.add_switch('s3')
        #h3 = self.add_host('h3', **hconfig)
        #self.add_link(s2, s3,
        #              port1=downlink, port2=uplink, **lconfig)
        #self.add_link(h3, s3,
        #              port1=0, port2=hostlink, **lconfig)

        # End: Template code

def waitListening(client, server, port):
    "Wait until server is listening on port"
    if not 'telnet' in client.cmd('which telnet'):
        raise Exception('Could not find telnet')
    cmd = ('sh -c "echo A | telnet -e A %s %s"' %
           (server.IP(), port))
    while 'Connected' not in client.cmd(cmd):
        output('waiting for', server,
               'to listen on port', port, '\n')
        sleep(.5)

def progress(t):
    while t > 0:
        # cprint('  %3d seconds left  \r' % (t), 'cyan', cr=False)
        print('  %3d seconds left  \r' % (t))
        t -= 1
        sys.stdout.flush()
        sleep(1)
    print()

def start_tcpprobe():
    os.system("rmmod tcp_probe &>/dev/null; modprobe tcp_probe;")
    Popen("cat /proc/net/tcpprobe > %s/tcp_probe.txt" % args.dir, shell=True)

def stop_tcpprobe():
    os.system("killall -9 cat; rmmod tcp_probe &>/dev/null;")

def run_outcast_expt(net, n):
    "Run experiment"

    # the seconds determine the number of datapoints for each host
    seconds = args.time

    # Start the bandwidth and cwnd monitors in the background
    monitor = Process(target=monitor_devs_ng, 
            args=('%s/bwm.txt' % args.dir, 1.0))
    monitor.start()
    start_tcpprobe()

    # Get receiver and clients
    recvr = net.getNodeByName('receiver')
    sender1 = net.getNodeByName('h1')

    # Start the receiver
    port = 5001
    recvr.cmd('iperf -Z reno -s -p', port,
              '> %s/iperf_server.txt' % args.dir, '&')

    waitListening(sender1, recvr, port)

    
    # Use getNodeByName() to get a handle on each sender.
    # Use sendCmd() and waitOutput() to start iperf and wait for them to finish
    # iperf command to start flow: 'iperf -c %s -p %s -t %d -i 1 -yc > %s/iperf_%s.txt' % (recvr.IP(), 5001, seconds, args.dir, node_name)
   
    
    for i in range(0, n+1):
        node_name = 'h' + str(i)
        # This was indented outside earlier
        sender = net.getNodeByName(node_name)
        sender.sendCmd('iperf -Z reno -c %s -p %s -t %d -i 1 -yc > %s/iperf_%s.txt' % (recvr.IP(), 5001, seconds, args.dir, node_name))

    for i in range(0,n+1):
        sender = net.getNodeByName('h' + str(i))
        sender.waitOutput()

    recvr.cmd('kill %iperf')

    # Shut down monitors
    monitor.terminate()
    stop_tcpprobe()

def check_prereqs():
    "Check for necessary programs"
    prereqs = ['telnet', 'bwm-ng', 'iperf', 'ping']
    for p in prereqs:
        if not quietRun('which ' + p):
            raise Exception((
                'Could not find %s - make sure that it is '
                'installed and in your $PATH') % p)

def main():
    "Create and run experiment"
    start = time()

    topo = OutcastTopo(n=args.n)

    host = custom(CPULimitedHost, cpu=.15)  # 15% of system bandwidth
    link = custom(TCLink, bw=args.bw, delay='1ms',
                  max_queue_size=200)

    net = Mininet(topo=topo, link=link)

    net.start()
    
    # cprint("*** Dumping network connections:", "green")
    print("*** Dumping network connections:")
    dumpNetConnections(net)

    # cprint("*** Testing connectivity", "blue")
    print("*** Testing connectivity")

    net.pingAll()

    if args.cli:
        # Run CLI instead of experiment
        CLI(net)
    else:
        # cprint("*** Running experiment", "magenta")
        print("*** Running experiment")
        run_outcast_expt(net, n=args.n)

    net.stop()
    end = time()
    os.system("killall -9 bwm-ng")
    # cprint("Experiment took %.3f seconds" % (end - start), "yellow")
    print("Experiment took %.3f seconds" % (end - start))

if __name__ == '__main__':
    check_prereqs()
    main()

