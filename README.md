# CS536 - Project - Reproducing Research 
Paper Followed: [paper link](https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/prakash)
## Reproducing TCP outcast on Parking lot topology
First part is to reproduce the TCP outcast problem on a parking lot topology with n(2/6/12) senders on 3 hop distance and 1 sender (getting outcasted)
on 2 hop distance from the receiver. 

Test setup - AWS EC2 instance (t2.large running ubuntu 22.04 in us-east-1d AZ)
### The steps to run this experiment are:
```
# env setup steps
sudo apt upgrade
sudo apt update
sudo apt-get install mininet
sudo apt-get install python3-pip python-dev
sudo pip3 install termcolor
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

## Reproducing TCP outcast on Fat Tree Topology
For this part we use the Fattree TOPO and POX controller defined in [here](https://github.com/gramorgan/mininet-fat-tree) for this part.

Test setup - [Mininet 2.2.2 VM with pox installed](https://github.com/mininet/mininet/releases/tag/2.2.2)
### The steps to run this experiment are:
```
# clone the repo
git clone  https://github.com/HrishikeshVish/CS536Project.git
cd CS536Project/outcast

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
