#!/bin/sh

usage() { echo "Usage: $0 [-i <string>] [-u <string>] [-f <string>]" 1>&2; exit 1; }

while getopts "h:i:f:u" arg; do
    case $arg in
        h)
            echo "usage" 
            ;;
        u)
            url=$OPTARG
            echo $url
            ;;
        f)
            family=$OPTARG
            echo $family
            ;;
        i)
            iface=$OPTARG
            echo $iface
            ;;
    esac
done

if [ -z "${family}" ] || [ -z "${iface}" ] || [ -z "${url}" ]; then
   usage
fi

start=`date +%s`

function read_output() {
    while IFS= read -r line
    do
        if [ -z "${line##*$Probe*}" ]; then
            local power=$(grep -E 's\(-\d+|0\)dBm' $line)
            local station=$(grep -E '.*SA:\(.*?\)\s' $line)
            local now=`date +%s`
            local elapsed=$(expr $now - $start)
            echo "$power $station $now"
        fi
    done
}

tcpdump -i $i -e -s 256 type mgt subtype probe-req | read_output
