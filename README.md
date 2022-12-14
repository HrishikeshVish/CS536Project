# CS536 - Project - Reproducing Research 
Paper Followed: [paper link](https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/prakash)
## Reproducing TCP outcast on Parking lot topology
First part is to reproduce the TCP outcast problem on a parking lot topology with n(2/6/12) senders on 3 hop distance and 1 sender (getting outcasted)
on 2 hop distance from the receiver. 

Test setup - AWS EC2 instance (t2.large running ubuntu 22.04 in us-east-1d AZ, Python 3.7.13)
### The steps to run this experiment are:
```
# env setup steps
sudo apt upgrade
sudo apt update
sudo apt-get install mininet
sudo apt-get install python3-pip python-dev
sudo apt-get install -y bwm-ng

# clone this repo
git clone  https://github.com/HrishikeshVish/CS536Project.git
cd CS536Project/outcast

# this cmd will generate the rate.png and avg_bw.png for n=2/6/12 senders on a parking lot topo
sudo ./outcast-sweep.sh

# the output dir will look like (n2/n6/n12)
(base) ➜  aws tree outcast-Nov12-16:25/n2 
outcast-Nov12-16:25/n2
├── avg_bw.png
├── bwm.txt
├── cwnd.png
├── iperf_h0.txt
├── iperf_h1.txt
├── iperf_h2.txt
├── iperf_server.txt
├── rate.png
...
```
### The steps to run experiments on unsynchronised flows:
```
# Make the following changes in the outcast.py file for simulating early start by 100ms:
Add the following line of code after line 184:
if n==0: sleep(100/1000)
# Make the following changes in the outcast.py file for simulating delay start by 100ms:
Replace the line 179 by the following:
for i in range(n,-1,-1 ):
Add the following line of code after line 184:
if n==1: sleep(100/1000) 
# Make the following changes in the outcast.py file for simulating delay start by 200ms:
Replace the line 179 by the following:
for i in range(n,-1,-1 ):
Add the following line of code after line 184:
if n==1: sleep(200/1000) 
```

### The steps to run experiments on different tcp variants:
```
# Make the following changes in the outcast.py file for simulating tcp cubic:
Replace the line 168 by the following:
recvr.cmd('iperf -Z cubic -s -p', port,'> %s/iperf_server.txt' % args.dir, '&')
Replace the line 183 by the following:
sender.sendCmd('iperf -Z cubic -c %s -p %s -t %d -i 1 -yc > %s/iperf_%s.txt' % (recvr.IP(), 5001, seconds, args.dir, node_name))

# Make the following changes in the outcast.py file for simulating tcp newreno:
Replace the line 168 by the following:
recvr.cmd('iperf -Z newreno -s -p', port,'> %s/iperf_server.txt' % args.dir, '&')
Replace the line 183 by the following:
sender.sendCmd('iperf -Z newreno -c %s -p %s -t %d -i 1 -yc > %s/iperf_%s.txt' % (recvr.IP(), 5001, seconds, args.dir, node_name))
```
### The steps to run experiments on tcp pacing:
```
# Make the following changes in the outcast.py file for simulating tcp pacing:
Add the following two lines after the line 206:
os.system("sysctl -w net.ipv4.tcp_pacing_ss_ratio=75")
os.system("sysctl -w net.ipv4.tcp_pacing_ca_ratio=75")
```


## Reproducing TCP outcast on Fat Tree Topology
For this part we use the Fattree TOPO and POX controller defined in [here](https://github.com/gramorgan/mininet-fat-tree) for this part.

Test setup - [Mininet 2.2.2 VM, ubuntu 14.04 with POX](https://github.com/mininet/mininet/releases/tag/2.2.2) - 1 CPU, 2 GB RAM
### The steps to run this experiment are:
```
# clone the repo
git clone  https://github.com/HrishikeshVish/CS536Project.git
cd CS536Project/outcast

# checkout fattree-plot branch
git checkout fattree-plot

# create symlinks to ~/pox/ext - the default POX installation
ln -s topo_ft.py ~/pox/ext/
ln -s fakearp.py ~/pox/ext/
ln -s controller_dj.py ~/pox/ext/
ln -s controller_2level.py ~/pox/ext/

# run the fattree topo code
sudo ./fattree-sweep.sh

# the o/p result dir will look like
mininet@mininet-vm:~/CS536Project/outcast$ tree outcast-Nov13-17:06/n4
outcast-Nov13-17:06/n4
|-- bwm.txt
|-- iperf_p0_s1_h2.txt
|-- iperf_p0_s1_h3.txt
...

# Running plot_rate.py seems impossible as the links to install pip are not valid anymore
# copying the bwm.txt file into AWS/PC and running plot_rate.py cmd
python util/plot_rate.py --rx --maxy 1 --maxx 60 --metric 'max' --xlabel 'Time (s)' \
--ylabel 'Rate (Mbps)' -i 'p[0-3]_s0-eth[1-2]' -f bwm.txt -o rate.png

```
