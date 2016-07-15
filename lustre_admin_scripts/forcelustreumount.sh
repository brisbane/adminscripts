#!/bin/bash
if ! [[ $1 ]] || [ $1 = -h ]; then
echo This code takes the name of the filesystem
echo eg $0 /data/atlas
echo Its then going to force change directory on all processes with cwd open on it, soft kill all processes using it then wait a bit and hard kill everything else
echo a report of what it did is generated
echo run with the secondargument as -n to see what it would do assuming everything worked first time
echo if you are having trouble parsing the maps for a particular pid, you can change the skip pids option in the code "(no cmd line option, sorry)"
exit 0
fi
#space seperateed list of pids to ignore
#skippids="29571 1111"
for i in $skippids; do 
  pidskip="$pidskip -p ^$i"
done
echo skipping pids: $pidskip

if [[ $2 ]] && [ $2 == -n ]; then
  dontdoit=1
fi
echo=""
chdirs=`lsof $pidskip | grep $1 | grep pplxlustre25mds3 | grep "cwd       DIR"`
kills=`lsof $pidskip | grep $1 | grep pplxlustre25mds3 | grep -v "cwd       DIR"`
ifs=$IFS
IFS=$'\n'

for i in $chdirs; do 
  pid=`echo $i | awk '{print $2}'`
  chdirpids="$chdirpids $pid"
  chdircwds="$chdircwds $pid:`echo $i | awk '{print $9}'`"
done

for i in $kills; do 
  killpids="$killpids `echo $i | awk '{print $2}'`"
done

echo Im going to change these process directories:
for i in $chdirs ; do echo $i; done

echo Then Im going to kill these processes
for i in $kills ; do echo $i; done



IFS=$ifs
if ! [[ $dontdoit ]]; then

  for i in $chdirpids ; do 
    $echo ~brisbane/bin/admin-scripts/forcechdir $i '/'
  done
  for i in $killpids ; do 
    $echo kill $i
  done
  sleep 5
  IFS=$ifs
  fkills=`lsof $pidskip | grep $1`

  IFS=$'\n'
  echo now Im going to force kill these
  for i in $fkills; do 
      echo $i
  done

  for i in $fkills; do
  $echo kill -9 `echo $i | awk '{print $2}'`
  done
sleep 2



fi

echo then Im going to restart autofs and cd back into the new $1 dis

IFS=' '
for i in $chdircwds; do 
  pid=$(echo $i | cut -f 1 -d : )
  dir=$(echo $i | cut -f 2 -d : )
  echo change  pid $pid back to dir $dir
done

if [[ $1 == "/data/atlas" ]]; then
  umount /lustre/atlas25/
elif [[ $1 == "/data/lhcb" ]]; then
  umount /lustre/lhcb25
fi

echo when you want to remount the fs, press enter
read 
if [[ $1 == "/data/atlas" ]]; then
  mount /lustre/atlas25/
elif [[ $1 == "/data/lhcb" ]]; then
  mount /lustre/lhcb25
fi
if ! [[ $dontdoit ]]; then
$echo service autofs restart
sleep 2
for i in $chdircwds; do 
  pid=$(echo $i | cut -f 1 -d : )
  dir=$(echo $i | cut -f 2 -d : )
  $echo ~brisbane/bin/admin-scripts/forcechdir $pid $dir
done


fi

