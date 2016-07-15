#!/bin/bash
echo -n Enter Password:
read -s password
HOSTS=$@
echo $HOSTS
if ! [[ $TENSPREFIX ]]; then
  TENSPREFIX=10.144.1
fi
for HOST in $HOSTS; do 
last=`dig $HOST.physics.ox.ac.uk +short | cut -f 4 -d \.`
echo ipmitool -E -I lan -H $TENSPREFIX.$last -U ADMIN -E power off

IPMI_PASSWORD=$password ipmitool -E -I lan -H $TENSPREFIX.$last -U ADMIN -E power off
sleep 6
done
for HOST in $HOSTS; do 
last=`dig $HOST.physics.ox.ac.uk +short | cut -f 4 -d \.`
echo ipmitool -E -I lan -H $TENSPREFIX.$last -U ADMIN -E power on
IPMI_PASSWORD=$password  ipmitool -E -I lan -H $TENSPREFIX.$last -U ADMIN -E power on
done
