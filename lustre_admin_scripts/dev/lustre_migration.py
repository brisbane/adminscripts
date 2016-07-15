#!/bin/env python 
import re,os, sys, random
#atlas-OST000c_UUID   19313886264 14917971788  3429905640  81% /lustre/atlas[OST:12]
match=re.compile(r"^atlas-OST00([\d+,a-f]*).*\[OST:(\d+)\]$")


def get_server_maps():
  servdict={}
  for l in os.popen("lfs df").readlines():
     m= match.match(l)
     if m: 
        g=m.groups()
        print g
        server=os.popen("cat /proc/fs/lustre/osc/atlas-OST00"+g[0]+"*/ost_conn_uuid","r").readlines()[0].strip()
        servdict[g[1].strip()]=server 
  return servdict

def lustreconn_2_hostname(i):
   return os.popen("dig +short -x  "+i.split('@')[0]).readlines()[0].strip(".\n")
def servername2osts(name):
    #Get the ip
    cmd =  "dig +short "+name
    osts=[]
    ip=os.popen(cmd).readlines()[0].strip()

    for root, dir, files in os.walk("/proc/fs/lustre/osc"):
      for f in files:
             if f=="ost_conn_uuid":
                  tcpcon=open(root+'/'+f,'r').readlines()[0].strip()
                  if str(ip+'@tcp') == tcpcon:
                      osts.append(os.path.basename(root))
    return osts 
def determine_striping(direc):
   namedue=True
   stripedict={}
   
   for i in os.popen("lfs getstripe -ir "+direc) :
       if namedue: 
          name=i
          namedue=False
       else :
          namedue=True
          k=i.strip()
          if not stripedict.has_key(k):
            stripedict[k]=[]
          stripedict[k].append(name.strip())
   return stripedict
     
def stripedict_2_server(stripedict, servertrans):
    serverfiledict={}
    for k, val in stripedict.items():
       if k == "-1": 
          continue
       serverfiledict[servertrans[k] ]=val
    return serverfiledict

def optimize_suggest(servervals):
  tot=0
  n=0
  retd={}
  for i , val in servervals.items():
     #count up files on servers
     tot+=len(val)
     n+=1
  average=tot/n
  #give list of servers to offline
  servers_to_offline=[]
  for  i , val  in servervals.items():
     if len(val)-2 > average:
        servers_to_offline.append( ( i, len(val)-2 - average) )
  print servers_to_offline

  #randomly select N files to migrate from offline servers
  for s, n in servers_to_offline:
    sample=[]
    for i, line in enumerate(servervals[s]):
      if i < n:
           sample.append(line)
      #reservoir sampling
      elif i >= n and random.random() < n/float(i+1):
            replace = random.randint(0,len(sample)-1)
            #print  " replaced " ,sample[replace] , ' with ', line
            sample[replace]=line  
    print "for server " ,  lustreconn_2_hostname(s), " migrate :" , len(sample), ' files'
    retd[lustreconn_2_hostname(s)]=sample
  return retd


if __name__=='__main__' : 
  print 'running'
  if len(sys.argv)!=2 :
     print "need directory to rebalance"
     sys.exit(1)
  dir=sys.argv[1]
  smaps = get_server_maps()
  std = determine_striping(dir)
  servervals=stripedict_2_server(std,smaps)
  for i , val in servervals.items():
       print os.popen("dig +short -x  "+i.split('@')[0]).readlines()[0].strip(".\n"),' : \n',  len(val)
  migfiles=optimize_suggest(servervals)

  print ' INSTRUCTIONS '
  print '1) offline the following servers:'
  for i in migfiles:
     print i
  print "thats the following osts:"
  tooffline=[]
  for i in migfiles:
     for j in  servername2osts(i):
         print j[0:17]
         tooffline.append(j[0:17])
  for i in tooffline:
     print "lctl --device `lctl dl | grep " + i + "  | awk '{print $1}'` deactivate"
     
  outfname="migfiles"
  print "2) migrate the files I am about to write in '"+outfname+"'"
  f=open(outfname,"w")
  for i in migfiles:
   for j in migfiles[i]:
     f.write("lfs_migrate -y "+ j+"\n")
  f.close()
  f=open("t","w")
#  for j in migfiles['pplxlustreoss09.physics.ox.ac.uk']:
#     f.write("lfs_migrate -y "+ j+"\n")
#  f.close()



