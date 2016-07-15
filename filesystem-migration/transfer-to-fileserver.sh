#!/bin/bash
fileservers="pplxfs16 pplxfs10 pplxfs11 pplxfs12 pplxfs13 pplxfs14 pplxfs15"
RUN=$2
for i in $fileservers; do 
   scp $1 root@$i:/root/
   if [[ $RUN ]] && [ $RUN == y ]; then
        ssh -a -x -t root@$i screen -xRR -A -e^Zz -U -O "sleep 100"
   fi
done 
