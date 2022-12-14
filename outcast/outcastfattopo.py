#!/usr/bin/python

import sys
from time import sleep, time
from multiprocessing import Process
from subprocess import Popen
import shlex
from mininet.node import RemoteController
from topo_ft import FatTreeTopo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import custom, dumpNetConnections
from mininet.clean import cleanup
from util.monitor import monitor_devs_ng

from subprocess import Popen, PIPE
import os
import sys
import atexit
import signal
import glob

# we get arg parsing for free!
from outcast import start_tcpprobe, stop_tcpprobe, args, waitListening

K = 4

CONTROLLERS = {
    '2level': 'controller_2level',
    'dijkstra': 'controller_dj'
}

def run_pox():
    controller = CONTROLLERS['2level']
    p_pox = Popen(
        [os.environ['HOME'] + '/pox/pox.py', 'fakearp', controller, '--topo=fattree,%d'%K, '--install'],
        # make pox ignore sigint so we can ctrl-c mininet stuff without killing pox
        preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
    )
    atexit.register(p_pox.kill)


def main():

    atexit.register(cleanup)
    # just in case program gets interrupted before iperfs get killed
    atexit.register(lambda: os.system('killall iperf 2> /dev/null'))

    run_pox()

    sleep(10)

    k = 4
    topo = FatTreeTopo(k=k)

    host = custom(CPULimitedHost, cpu=.5)  # 15% of system bandwidth
    link = custom(TCLink, bw=args.bw, delay='.05ms',
                  max_queue_size=200)

    net = Mininet(topo=topo, host=host, link=link, controller=RemoteController, autoSetMacs=True)

    net.start()

    sleep(5)

    print "*** Dumping network connections:"
    dumpNetConnections(net)
    # raw_args = shlex.split("/home/ubuntu/pox/pox.py riplpox.riplpox --topo=ft,%s --routing=%s" % (k, args.routing))

    # proc = Popen(raw_args)

    # print "********************************************************"
    # print "*******************STARTED RIPLPOX**********************"

    # #This sleep 10 is to give the riplpox controller time to start up before you start sending.  Seems to work well.
    # sleep(10)


    # 
    # Actual Experiment
    #

    seconds = args.time

    # Start the bandwidth and cwnd monitors in the background
    monitor = Process(target=monitor_devs_ng, 
            args=('%s/bwm.txt' % args.dir, 1.0))
    monitor.start()
    start_tcpprobe()

    # Get receiver and clients
    recvr = net.getNodeByName('p0_s0_h2')
    sender1 = net.getNodeByName('p0_s0_h3')

    # Start the receiver
    port = 5001
    recvr.cmd('iperf -Z reno -s -p', port,
              '> %s/iperf_server.txt' % args.dir, '&')

    waitListening(sender1, recvr, port)

    # TODO: start the sender iperf processes and wait for the flows to finish
    # Hint: Use getNodeByName() to get a handle on each sender.
    # Hint: Use sendCmd() and waitOutput() to start iperf and wait for them to finish
    # iperf command to start flow: 'iperf -c %s -p %s -t %d -i 1 -yc > %s/iperf_%s.txt' % (recvr.IP(), 5001, seconds, args.dir, node_name)
    # Hint (not important): You may use progress(t) to track your experiment progress
    
    for p in range(k):  # Pod Range
        for e in range(2):  # Edge range
            for h in range(2, (k/2)+2):  # Host Range
                if p == 0 and e == 0: 
                    continue
                node_name = 'p%d_s%d_h%d' % (p, e, h)
                sender = net.getNodeByName(node_name)
                sender.sendCmd('iperf -Z reno -c %s -p %s -t %d -i 1 -yc > %s/iperf_%s.txt' % (recvr.IP(), 5001, seconds, args.dir, node_name))
   
    for p in range(k):  # Pod Range
        for e in range(2):  # Edge range
            for h in range(2, (k/2)+2):  # Host Range
                if p == 0 and e == 0: 
                    continue
                node_name = 'p%d_s%d_h%d' % (p, e, h)
                sender = net.getNodeByName(node_name)
                sender.waitOutput()

    recvr.cmd('kill %iperf')

    # Shut down monitors
    monitor.terminate()
    stop_tcpprobe()





    #Here just use p.terminate() to stop the process when you are done
    net.stop()
    proc.terminate()

if __name__ == '__main__':
    main()
