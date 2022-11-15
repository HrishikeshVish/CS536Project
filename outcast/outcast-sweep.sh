#!/bin/bash

# Exit on any failure
set -e

# Check for uninitialized variables
set -o nounset

ctrlc() {
	killall -9 python3
	mn -c
	exit
}

trap ctrlc SIGINT

start=`date`
exptid=`date +%b%d-%H:%M`
rootdir=outcast-$exptid
bufferdir=buffersizing-$exptid
bw=100

# Note: you need to make sure you report the results
# for the correct port!
# In this example, we are assuming that each
# client is connected to port 2 on its switch.

for n in 2 6 12; do
    dir=$rootdir/n$n
    buffdir=$bufferdir/nf-r1-regular
    python3 outcast.py --bw $bw \
        --dir $dir \
        -t 60 \
        -n $n
        --buffdir $buffdir \
    python3 util/plot_rate.py --rx \
        --maxy $bw \
        --xlabel 'Time (s)' \
        --ylabel 'Rate (Mbps)' \
        --n $n \
	-i '(s2-eth[2-9])|(s2-eth1[0-9])|(s1-eth1)' \
        -f $dir/bwm.txt \
        -o $dir/rate.png \
	--bwout $dir/avg_bw.png
    python3 util/plot_tcpprobe.py \
        -f $dir/tcp_probe.txt \
        -o $dir/cwnd.png
done

echo "Started at" $start
echo "Ended at" `date`
echo "Output saved to $rootdir"
