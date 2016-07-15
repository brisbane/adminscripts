#!/bin/bash
for i in /data/atlas/atlasdat*/*; do 
user=`stat -L --printf=%U $i`
getent passwd $user | grep -q  '!' && echo $i $user
done
