#!/bin/bash

host="http://datengammelstelle.de/hq_strom"

while true; do 
	sleep 5; 
	wget $host/get.php?val=$(tail -1 /srv/powerpi/power.out) -O /dev/null -q
done
