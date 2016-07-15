#!/usr/bin/env python

import sys, os

import random, threading, Queue, time
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
     random.seed(i)
     r=random.uniform(0, tot)
     for x in ranger.keys():
       if r > ranger[x][0] and r < ranger[x][1]:
          index=str(x)
     ext=random.uniform(0,1)
     tmpname=i+".tmp"+str(ext)
     useddir=''
     if not indir:
       useddir=os.path.dirname(i)
     else:
       useddir=indir
     cmd="cd " + useddir+";lfs getstripe -i "+str(i)
     indexinit=os.popen(cmd).readlines()[0].strip()
     if indexinit != index:
        cmd="cd "+useddir+";lfs setstripe -i "+index+ " " + tmpname +" && /usr/bin/rsync -a --inplace "+i + " " + tmpname+"  && /bin/rm "+ i+ " && /bin/mv "+tmpname+" " + i  +" && echo success: "+i
        print"Running "+ cmd
        res=os.system(cmd)
     print 'done '+i
   except:

     print 'done '+i, ' exception', sys.exc_info()[0]
   q.task_done()


num_worker_threads=10

q = Queue.Queue()

#TODO, this is wasteful as it migrates all the files. It could leave some of the ones on overpopulated osts in place.
#balance for speed
#layout map, the wieght given to each server target
layout={}
#decomission
#layout[61] = 1
layout[71] = 1
layout[81] = 1
layout[91] = 1
layout[101] = 1
layout[111] = 1
layout[131] = 0.5
layout[132] = 0.5
layout[171] = 0.5
layout[172] = 0.5
layout[181] = 0.5
layout[182] = 0.5
layout[191] = 0.5
layout[192] = 0.5
layout[221] = 0.5
layout[222] = 0.5
layout[231] = 4
layout[241] = 4

tot=0
begin=0
for k  in layout.keys():
   
   tot=layout[k]+tot

   end=begin+layout[k]
   ranger[k]=(begin, end)

   begin=end

print tot
current_bal=''
if indir:
  current_bal=os.popen("lfs getstripe -i "+indir+"/*| sort | uniq -c").readlines()
n=0

for i in current_bal:

  l=i.strip().split(' ')
  n+=int(l[0])

thelist=[]
if indir:
  thelist=os.listdir(indir)
else:
  thelist=open(filelist).readlines()

for i in thelist:
  print i
  q.put(i.strip())

for i in range(num_worker_threads):
     t = threading.Thread(target=worker)
     t.daemon = True
     t.start()

q.join()

print 'done'
if indir:
  final_bal=os.popen("lfs getstripe -i "+indir+"/*| sort | uniq -c").readlines()
  print current_bal
  print final_bal



