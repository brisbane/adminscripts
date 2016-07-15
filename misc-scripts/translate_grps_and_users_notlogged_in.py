#!/usr/bin/python
import os, sys, time

mapperg={}
mapperu={}
chownuser=True
generatelistonly=True

#onlytest=False
dodebug=True
dodebug=False

global exceptions
global cantcope
global batchfile2
global batchfile1
global batchfile

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
   if not ingid in mapperg and not inuid in mapperu: return 1
   if ingid in mapperg:
     outgid=mapperg[ingid]
   if inuid in mapperu and chownuser:
      outuid=mapperu[inuid]
   if outuid == -1 and outgid == -1:
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
         os.chown(f,outuid,outgid)
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

  mapperg[9991] = 39991
  mapperg[460] = 30460
  mapperg[401] = 30401
  mapperg[400] = 30400
  mapperg[560] = 30560
  mapperg[340] = 30340
  mapperg[250] = 30250
  mapperg[650] = 30650
  mapperg[480] = 30480
  mapperg[402] = 30402
  mapperg[351] = 30531
  mapperg[350] = 30350
  mapperg[403] = 30403
  mapperg[7817] = 37817
  mapperg[170] = 30170
  mapperg[330] = 30330
  mapperg[160] = 30160
  mapperg[630] = 30630
  mapperg[280] = 30280
  mapperg[105] = 30105
  mapperg[620] = 30620
  mapperg[404] = 30404
  mapperg[450] = 30450
  mapperg[550] = 30550
  mapperg[3200] = 33200
  mapperg[370] = 30370
  mapperg[490] = 30490
  mapperg[430] = 30430
  mapperg[130] = 30130

  mapperu[268] = 10281
#macallister:A/g/roiNEbVW.:268:10016:J.B.Macallister (IT Staff),662,73388:/home/macllstr:/bin/tcsh
  mapperu[272] = 327990491
#mcarthur:f/YtH6F4Dx5d2:272:10016:i mcarthur (IT Staff),662a,73350:/home/mcarthur:/bin/tcsh
  mapperu[277] = 10213
#topp:jyiWt4DE2H.0Y:277:10016:S Topp-Jorgensen (IT Staff),663,73506:/home/topp:/bin/bash -> caps in AD
 # mapperu[282] = 10564 
#weidberg:hi2Hrvh5HcVI2:282:30350:Tony Weidberg (LHC),631,73370:/home/weidberg:/bin/bash -> caps in AD
  mapperu[301] = 21018
#devenish:9lgDpZV2kBIX.:301:30330:rce devenish (ZEUS),675,73320:/home/devenish:/bin/tcsh
  mapperu[313] = 10210
#hunter:wo8meGMS9WJeg:313:10016:Chris Hunter,660,73501:/home/hunter:/bin/tcsh
 # mapperu[315] = 21119
#cooper:OD3o5PhvDXGUg:315:30330:Amanda Cooper (ZEUS),756,73406:/home/cooper:/bin/tcsh
  mapperu[316] = 21086
#harnew:7WMsVNB4XAU4s:316:30330:Neville Harnew (ZEUS),629,73316:/home/harnew:/bin/tcsh
  mapperu[319] = 21098
#renton:$1$LaFgCekh$QtWomJMDWPXK3jDttPG6N/:319:30370:Peter Renton (DELPHI),752,73327:/home/renton:/bin/tcsh
  mapperu[325] = 21067
#cobb:44a7vDJgBOeZw:325:30450:John Cobb (PDK),672,73328:/home/cobb:/bin/tcsh
  mapperu[334] = 21078
#radojicic:$1$txF22NiI$ot0GbP0reDPBFc39ertlT0:334:30370:Dusan Radojicic:/home/dusan:/bin/tcsh
  mapperu[380] = 21097
#walczak:$1$vAlyZ2m6$y5cllgPU7JLQLuCBpqSBv/:380:30330:Roman Walczak (ZEUS),628,73324:/home/walczak:/bin/tcsh
  mapperu[382] = 21016
#reichold:xsKzkqIuB2eR2:382:30250:Armin Reichold (Licas):/home/reichold:/bin/tcsh
  mapperu[396] = 21010
#myatt:HL5ymb3kxyYA.:396:30370:Gerald Myatt (DELPHI),611,73326:/home/myatt:/bin/tcsh
  mapperu[443] = 21006 
#wastie:oyUfTwJysfM/w:443:10027:Roy Wastie (ELECTRONICS),4482a,73437:/home/wastie:/bin/bash
  mapperu[466] = 21150
#libby:xAAOIkW2D3iDs:466:30160:James F. Libby (LHCB),651,73396:/home/libby:/bin/tcsh
  mapperu[475] = 21013
#doucas:$1$fhZ2uOSj$fjN6N/orBJxtDNMUPPB2L.:475:30340:George Doucas (SNO),674,73313:/home/doucas:/bin/tcsh
  mapperu[479] = 10560
#biller:pjQtx14r4JEM6:479:30340:Steve Biller (SNO),750,73386:/home/biller:/bin/tcsh -> caps in ad
  mapperu[500] = 7738
#cdsno:5Vqw4z4eCLBbM:500:30340:cdsno Oxford (SNO):/home/cdsno:/bin/tcsh
  mapperu[508] = 20123
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
  if len( sys.argv ) > 1:
      target=sys.argv[1]
  
  domain(target)
