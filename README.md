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
cd outcast

# this cmd will generate the rate.png and avg_bw.png for n=2/6/12 senders on a parking lot topo
sudo ./outcast-sweep.sh
```

## Reproducing TCP outcast on Fat Tree Topology
For this part we use the Fattree TOPO and POX controller defined in [here](https://github.com/gramorgan/mininet-fat-tree) for this part.
Test setup - [Mininet 2.2.2 VM with pox installed](https://github.com/mininet/mininet/releases/tag/2.2.2)
### The steps to run this experiment are:
