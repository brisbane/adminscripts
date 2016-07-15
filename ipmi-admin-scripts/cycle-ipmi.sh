#!/bin/bash

HOST=$1
last=`dig  ${HOST}.physics.ox.ac.uk +short | cut -f 4 -d \.`
if ! [[ $last ]]; then
   echo cant find $1
   exit 1
fi
echo -n Enter Password:
read -s password
IPMI_PASSWORD=$password  | ipmitool -I lan -H 10.144.1.${last} -U ADMIN -E bmc reset cold


