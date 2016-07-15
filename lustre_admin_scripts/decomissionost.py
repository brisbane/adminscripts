#!/usr/bin/env python

import sys, os, subprocess

import random, threading, Queue, time
ost="61"
if len(sys.argv) < 2 or not sys.argv[1] or sys.argv[1] =='--help':
  print "usage "+sys.argv[0]+" {stop|dir|filelist}"
  print "this is a multi threaded application"
  print 'to stop it, call "'+sys.argv[0]+ ' stop" as the curent user from another shell.  ctrl +c wont work and will leave a mess if it did'
  sys.exit(1)
stopfile=os.getenv("HOME") + '/stopmigration'

print 'to stop this, call "'+sys.argv[0]+ ' stop" as the curent user from another shell.  ctrl +c wont work and will leave a mess if it did'
if sys.argv[1]=="stop":
  os.system("touch "+stopfile)
  sys.exit(0)

else :
   if os.path.exists(stopfile):
     os.remove(stopfile)

print 'to stop this, call "'+sys.argv[0]+ ' stop" as the curent user from another shell.  ctrl +c wont work and will leave a mess if it did'
indir=None
filelist=None
if os.path.isdir(sys.argv[1]):
   indir=sys.argv[1]
elif os.path.isfile(sys.argv[1]):
   filelist=sys.argv[1]
   sys.exit(1)
else:
  sys.exit(1)

ranger={}
def worker():
  while 1:
   i=''
   try:
     i=q.get(True, 10)
   except Queue.Empty:
     return 1
   except:
      print "Unknown error", sys.exc_info()[0]
   try:

     if os.path.exists(stopfile):
          q.task_done()
          continue
     #use filename as seed.  Like a crush map, only move if necessary, but adding a new server will cause almost full rebalance
     cmd="lfs_migrate -yl "+ i
     print"Running "+ cmd
     res=os.system(cmd)
   except:

     print 'done '+i, ' exception', sys.exc_info()[0]
   q.task_done()


num_worker_threads=4

q = Queue.Queue()


tot=0
begin=0
n=0
source=''
proc=0
if indir :
  proc=subprocess.Popen(["lfs", "find",  "-ost",  ost, indir],stdout=subprocess.PIPE, bufsize=1,stdin=subprocess.PIPE)
  source=proc.stdout
  sbsrc=1
else:
  source= open(filelist)
  sbsrc=0
while True:
   x=source.readline()
   if  x == '':
     if sbsrc and proc.poll() != None:
        break
   print 'here'
   q.put(x.strip())

for i in range(num_worker_threads):
     t = threading.Thread(target=worker)
     t.daemon = True
     t.start()

q.join()
if sbsrc:
  proc.kill() 
  proc.wait()
print 'done'
