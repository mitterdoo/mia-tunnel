#!/bin/bash

host=$(head -1 /usr/bin/mia-tunnel/mia_ip.txt)
iptables -t nat -D PREROUTING -p tcp --dport 8096 -j DNAT --to-destination $host:8096
iptables -t nat -D PREROUTING -p tcp --dport 8096 -j DNAT --to-destination $host:8200
iptables -t nat -D PREROUTING -p tcp --dport 61208 -j DNAT --to-destination $host:61208
iptables -t nat -D PREROUTING -p udp --dport 1900 -j DNAT --to-destination $host:1900
iptables -t nat -D PREROUTING -p udp --dport 7359 -j DNAT --to-destination $host:7359
iptables -t nat -D PREROUTING -p tcp --dport 80 -j DNAT --to-destination $host:80
iptables -t nat -D PREROUTING -p tcp --dport 7878 -j DNAT --to-destination $host:7878
iptables -t nat -D PREROUTING -p tcp --dport 8989 -j DNAT --to-destination $host:8989
iptables -t nat -D PREROUTING -p tcp --dport 9091 -j DNAT --to-destination $host:9091
iptables -t nat -D PREROUTING -p tcp --dport 9092 -j DNAT --to-destination $host:9092
iptables -t nat -D PREROUTING -o tailscale0 -j MASQUERADE
