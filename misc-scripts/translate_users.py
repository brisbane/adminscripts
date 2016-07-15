#!/usr/bin/python
import os, sys, time

mapperu={}
chownuser=True
generatelistonly=True

#onlytest=False
dodebug=True

global exceptions
global cantcope
global batchfile2
global batchfile1
global batchfile

if len(sys.argv)<3 or sys.argv[1] == '-h':
  print "usage :"
  print sys.argv[0], "{ppuserid (old id)} {AD user id (new id)} {directory (default /data)} {reallydoit=0/1 (default 0)} "
  sys.exit(1)

inppuser = int(sys.argv[1])
inaduser = int(sys.argv[2])
if len (sys.argv) >4:
  if sys.argv[4] != '1' and sys.argv[4] != '0':
     print "usage :"
     print sys.argv[0], "{ppuserid (old id)} {AD user id (new id)} {directory (default /data)} {reallydoit=0/1 (default 0)} "

     sys.exit(1)
  if sys.argv[4] == 'y' or sys.argv[4] == '1':
     generatelistonly=False

def debug(st):
   if dodebug==True:
       print st
def translate(f):
   global exceptions
   global cantcope
   global batchfile2
   global batchfile1
   global batchfile

   debug( f )
   ingid=-1
   inuid=-1
   outuid=-1
   outgid=-1
   try:
     s=os.stat(f) 
     ingid=s.st_gid
     inuid=s.st_uid
   except OSError , e:
     if e.errno == 2: return 0 
     #too many levels of symlink
     elif e.errno==40 :
        debug( "too many links" )
        return 0
     #no idea why its 13 and 1, 110 is connection timed out
     elif e.errno==1  or e.errno==13 or e.errno==110:
        #permission denied
        exceptions.write(f+"\n")
        return 0
     raise
   except:
    raise
   if not inuid in mapperu: 
     print "blerch", inuid, mapperu
     return 1
   if inuid in mapperu and chownuser:
      outuid=mapperu[inuid]

   print outuid
   if outuid == -1 :
      return 0

   if f.find('\n') != -1:
        cantcope.write(f+'because of new line\n') 
        batchfile.write(f+'\n')
   if f.find(':') == -1:
         batchfile1.write(f+':'+str( outuid)+':'+str(outgid)+':'+str(inuid)+':'+str(ingid)+'\n')
   elif f.find('|') == -1: 
         batchfile2.write(f+'|'+str( outuid)+'|'+str(outgid)+'|'+str(inuid)+'|'+str(ingid)+'\n')
   else:
         cantcope.write(f+'because of delim\n')

   if not generatelistonly:
      try:
         print "will chown", f, outuid, outgid
         os.lchown(f,outuid,outgid)
      except OSError , e:
        if e.errno==1 or e.errno==13 or e.errno==110:
          #permission denied
          exceptions.write(f+"\n")
          return 0
      except:
          raise
   debug( "chown to "+str( outuid) + " " + str(outgid)+" " + f+'\n' )
   if not chownuser and inuid in mapperu:
      debug( "rather than "+str( mapperu[inuid]))
   return 0
def domain(target='/data'):
  global exceptions
  global cantcope
  global batchfile2
  global batchfile1
  global batchfile
  now=str(time.time())
  os.makedirs (os.path.join(os.getenv('HOME'),"chowner",now ))
  exceptions=open(os.path.join(os.getenv('HOME'),"chowner",now ,'exceptions.txt'),'w')
  cantcope=open(os.path.join(os.getenv('HOME'), "chowner",now,'cantcope.txt'),'w')
  batchfile1=open(os.path.join(os.getenv('HOME'),"chowner",now, 'batchfile1.txt'),'w')
  batchfile2=open(os.path.join(os.getenv('HOME'), "chowner",now, 'batchfile2.txt'),'w')
  batchfile=open(os.path.join(os.getenv('HOME'), "chowner",now, 'batchfile.txt'),'w')

  mapperu[inppuser] = inaduser
#coe:$1$DIzIOUzZ$hzhr6jPBvjxdReh.xOJzP0:508:30250:Paul Coe (AOPP Collaborator):/home/coe:/bin/tcsh

  if os.path.isdir(target):
    print 'Taking data from Directory'
    time.sleep(4)
    for root, dirs, files in os.walk(target):
      for dir in dirs:
        translate(os.path.join(root,dir))
      for f in files:
        translate(os.path.join(root,f))
  else:
    print 'Taking data from File'
    time.sleep(4)
    for l in open(target,'r'):
        translate(l.strip())
  exceptions.close()
  cantcope.close()
  batchfile1.close()
  batchfile2.close()
  batchfile.close()

if __name__ == "__main__":
  target='/data'
  if len( sys.argv ) > 3:
      target=sys.argv[3]
  
  domain(target)
