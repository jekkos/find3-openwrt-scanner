#!/bin/sh

. /usr/share/libubox/jshn.sh

usage() { echo "Usage: $0 [-i <string>] [-u <string>] [-f <string>]" 1>&2; exit 1; }

while getopts "i:u:f:h" arg; do
    case $arg in
        i)
            iface=$OPTARG
            ;;
        u)
            url=$OPTARG
            ;;
        f)
            family=$OPTARG
            ;;
        h)
            echo "usage" 
            ;;
    esac
done

if [ -z "${family}" ] || [ -z "${iface}" ] || [ -z "${url}" ]; then
   usage
fi

start=`date +%s`

build_payload() {
    json_init
    json_add_string "f" $family
    json_add_string "d" `cat /proc/sys/kernel/hostname`
    json_add_int "t" "$3"
    json_add_object "s"
    json_add_object "wifi"

    json_add_int "$1" "$2"
    json_close_object
    json_close_object
    payload=$(json_dump)
}

send_payload() {
    build_payload "$@"
    local response=$(curl -s -H 'Content-Type: application/json' -d"${payload}" ${url}/passive)
    echo $response
}

read_output() {
    while IFS= read -r line
    do
        if [ -z "${line##*$Probe*}" ] && [ ! -z "$line" ]; then
            local power=$(echo $line | grep -o -E '\-[0-9]{2}dBm')
            power=${power%dBm}
            local station=$(echo $line | grep -o -E 'SA:([^[:space:]]{2}:?)*')
            station=${station:3:20}
            local now=`date +%s`
            local elapsed=$(expr $now - $start)
            send_payload "$station" "$power" "$now"
            echo "Power: ${power}dBm Station: $station Time: $now"
        fi
    done
}

tcpdump -i $iface -e -s 256 type mgt subtype probe-req | read_output
