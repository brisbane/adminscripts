#!/usr/bin/python
import os, sys, time
import pwd
from paramiko_demo import doconnect


apperg={}
mapperu={}
mapperg={}
chownuser=True
generatelistonly=False

#onlytest=False
dodebug=True
dodebug=False

global exceptions
global cantcope
global batchfile2
global batchfile1
global batchfile

seenuids={}

def debug(st):
   if dodebug==True:
       print st
def get_new_session(t):
  chan =  t.open_session()
  f=chan.makefile()
  return chan, f
  #chan.invoke_shell()

def remove_logged_in_users_from_mapperu(mapperu, filterfile):
  #systems_to_check=["pplxint5", "pplxint6", "pplxint8", "pplxint9", "ppcryo1", "ppcryo2" ,"ppcryo3", "ppcryo4", "ppcryo6", "ppcryo7", "ppcryo8"]
  systems_to_check=["pplxint5", "pplxint6", "pplxint8", "pplxint9"]

  #forcefilter=["barra", "tseng", "gallas", "hays", "cooper", "macmahon", "malde", "gwenlan", "henry", "kraus", "barr", "viehhauser", "mikhailik"]
  #forcefilter=["barra", "tseng", "gallas", "hays", "cooper", "macmahon", "malde", "gwenlan", "barr", "viehhauser"]
  forcefilter=[]

   
  for k in mapperu.keys():
     print k, mapperu[k]
  users=[]
  for host in systems_to_check:
    try:
      t=doconnect(host, "root")
    except:
      print "Cant reach ", host
      continue
    chan, f = get_new_session(t)
 
 
    chan.exec_command("who | cut -f 1 -d ' '")
    for u in  f.readlines():
      user=u.strip()
      if user not in users:
        users.append(user)
    chan.close()
    t.close()
  if len(users) < 2: 
     print "Bombing out becuase I couldnt fill the logged in users map with anything"
     sys.exit(1)
  for u in forcefilter:
       print "force filtering: ", u     
       users.append(u)
  for user in users:
     uid=pwd.getpwnam(user).pw_uid
     if mapperu.has_key(uid):
        print "Filtering out  ", user,  uid, mapperu[uid]
        filterfile.write(user+'\n')
        mapperu.pop(uid)

  


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
     s=os.lstat(f) 
     ingid=s.st_gid
     inuid=s.st_uid
   except OSError , e:
     if e.errno == 2: return 0 
     #too many levels of symlink or not existing
     elif e.errno==40 :
        debug( "too many links" )
        return 0
     #no idea why its 13 and 1, 110 is connection timed out, 20 is dangling symlink
     elif e.errno==1  or e.errno==13 or e.errno==110 or e.errno==20:
        #permission denied
        exceptions.write(f+"\n")
        return 0
     else: 
       exceptions.write(f+"\n")
       print "unhandled exception 1", f, e.errno
       return 0
   except:
      exceptions.write(f+"\n")
      print "unhandled exception 2", f
      return 0
   if not ingid in mapperg and not inuid in mapperu: return 1
   if ingid in mapperg:
     outgid=mapperg[ingid]
   if inuid in mapperu and chownuser:
      outuid=mapperu[inuid]
   if outuid == -1 and outgid == -1:
      return 0

   if f.find('\n') != -1:
        cantcope.write(f+' because of new line\n') 
   else:
        batchfile.write(f+'\n')
   if f.find(':') == -1:
         batchfile1.write(f+':'+str( outuid)+':'+str(outgid)+':'+str(inuid)+':'+str(ingid)+'\n')

   elif f.find('|') == -1: 
         batchfile2.write(f+'|'+str( outuid)+'|'+str(outgid)+'|'+str(inuid)+'|'+str(ingid)+'\n')
   else:
         cantcope.write(f+' because of delim\n')
   seenuids[inuid]=1

   if not generatelistonly:
      try:
         print "will chown", f, outuid, outgid
         os.lchown(f,outuid,outgid)
      except OSError , e:
        if e.errno==1 or e.errno==13 or e.errno==110 or e.errno == 2:
          #permission denied, 2 is no such file 
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
  mapperg[555] = 30555
  mapperg[430] = 30430
  mapperg[130] = 30130

  mapperu[268] = 10281
#macallister:A/g/roiNEbVW.:268:10016:J.B.Macallister (IT Staff),662,73388:/home/macllstr:/bin/tcsh
  mapperu[272] = 327990491
#mcarthur:f/YtH6F4Dx5d2:272:10016:i mcarthur (IT Staff),662a,73350:/home/mcarthur:/bin/tcsh
  mapperu[277] = 10213
#topp:jyiWt4DE2H.0Y:277:10016:S Topp-Jorgensen (IT Staff),663,73506:/home/topp:/bin/bash -> caps in AD
  mapperu[282] = 10564 
#weidberg:hi2Hrvh5HcVI2:282:30350:Tony Weidberg (LHC),631,73370:/home/weidberg:/bin/bash -> caps in AD
  mapperu[301] = 21018
#devenish:9lgDpZV2kBIX.:301:30330:rce devenish (ZEUS),675,73320:/home/devenish:/bin/tcsh
  mapperu[313] = 10210
#hunter:wo8meGMS9WJeg:313:10016:Chris Hunter,660,73501:/home/hunter:/bin/tcsh
  mapperu[315] = 21119
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
  mapperu[808] = 2800
#monalisa
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
  mapperu[379] = 21017
#dhowell:!:379:30350:David Howell (LHC),457,73507:/home/dhowell:/bin/false
  mapperu[483] = 2138917078
#jelley:!:483:30340:Nick Jelley (SNO),630,73380:/home/jelley:/bin/false
  mapperu[495] = 21105
#lyons:*:21105:10027:Louis Lyons:/home/lyons:/bin/bash
#lyons:!:495:30370:Louis Lyons (DELPHI) NEVER ENABLE WITH THIS UID,620,73317:/home/lyons:/bin/false
  mapperu[536] = 2138917080
#huffman:*:2138917080:2114816467:huffman:/home/huffman:/bin/bash
#huffman:ekG7.bHVTlZXo:536:33200:Todd Huffman (CDF/LHC),631,73370:/home/huffman:/bin/bash
  mapperu[574] = 21104
#burrows:*:21104:10027:Philip Burrows:/home/burrows:/bin/bash
#burrows:!:574:30170:Phil Burrows (LC):/home/burrows:/bin/false
  mapperu[592] = 14509
#azfar:*:14509:10027:Farrukh Azfar:/home/azfar:/bin/bash
#azfar:jKzbfrAeePAew:592:33200:Dr. Farrukh Azfar (CDF):/home/azfar:/bin/tcsh
  mapperu[595] = 21025
#weber:*:21025:10027:Alfons Weber:/home/weber:/bin/bash
#weber:6Vd3dJbUivBO.:595:30130:Alfons Weber (MINOS)98:/home/weber:/bin/tcsh
  mapperu[618] = 21302
#brodet:*:21302:10027:Eyal Brodet:/home/brodet:/bin/bash
#brodet:$1$cboA9CsW$qrivGJE.adAUZrINDMkBn1:618:30370:Eyal Brodet (Delphi)99(visitor status 2010-2015):/home/brodet:/bin/bash
  mapperu[621] = 21014
#lavorato:*:21014:10027:Antonia Lavorato:/home/lavorato:/bin/bash
#lavorato:!:621:30350:Antonia Lavorato (LHC)99:/home/lavorato:/bin/false
  mapperu[629] = 21027
#kraus:*:21027:10027:Hans Kraus:/home/kraus:/bin/bash
#kraus:WnKmrHOwnQlXg:629:30400:Hans Kraus:/home/kraus:/bin/bash
  mapperu[631] = 21087
#barr:*:21087:10027:Giles Barr:/home/barr:/bin/bash
#barr:WD/VgFqvATExM:631:30550:Giles Barr (t2k):/home/barr:/bin/tcsh
  mapperu[653] = 21026
#gibson:*:21026:10027:Stephen Gibson:/home/gibson:/bin/bash
#gibson:!:653:30350:Stephen Gibson (LHC)2000:/home/gibson:/bin/false
  mapperu[539] = 2138917040
  #john harris
  mapperu[1007] = 10332
  #bartolini 
  mapperu[920] = 2600
  #font
  
  mapperu[620] = 106512
  #christian
  mapperu[655] = 21029
#henry:*:21029:10027:Samuel Henry:/home/henry:/bin/bash
#henry:vyW7cTW7EvfDw:655:30400:Samuel Henry (CRESST)2000:/home/henry:/bin/tcsh
  mapperu[709] = 21102
#wilkinsong:*:21102:10027:Guy Wilkinson:/home/wilkinsong:/bin/bash
#wilkinsong:rHiZSrVBluhG2:709:30160:Guy Wilkinson:/home/wilkinsn:/bin/tcsh
  mapperu[721] = 21085
#viehhauser:*:21085:10027:Georg Viehhauser:/home/viehhauser:/bin/bash
#viehhauser:$1$kM2VN7Uk$POVXlos.ztCtTm/fD.7Ji1:721:30350:Georg Viehhauser (LHC):/home/viehhaus:/bin/tcsh
  mapperu[770] = 106530
#tseng:*:106530:10027:tseng:/home/tseng:/bin/bash
#tseng:iGkAz/aBtc9ZI:770:30350:Jeff Tseng (LHC):/home/tseng:/bin/tcsh
  mapperu[777] = 10565
#gwenlan:*:10565:10027:Claire Gwenlan:/home/Gwenlan:/bin/bash
#gwenlan:6ol/W44joxTdY:777:30350:Claire Gwenlan (Atlas/Zeus):/home/gwenlan:/bin/bash
  mapperu[784] = 21028
#mikhailik:*:21028:10027:Vitalii Mikhailik:/home/mikhailik:/bin/bash
#mikhailik:0O43zPkjicTTQ:784:30400:Vitalii Mikhailik (Cresst):/home/vmikhai:/bin/tcsh
  mapperu[792] = 21132
#barra:*:21132:10027:Alan Barr:/home/barra:/bin/bash
#barra:851VS4lVsAnmc:792:30350:Alan Barr (Cambridge LHC):/home/barra:/bin/zsh
  mapperu[800] = 21022
#dehchar:*:21022:10027:Mohamed Dehchar:/home/dehchar:/bin/bash
#dehchar:!:800:30350:Mohamed Dehchar (LHC)03,613,73424:/home/dehchar:/bin/false
  mapperu[811] = 21238
#evans:*:21238:10026:evans:/home/evans:/bin/bash
#evans:!:811:30130:Justin Evans (MINOS)MPhys:/home/evans:/bin/false
  mapperu[840] = 21060
#dennis:*:21060:10027:Christopher Dennis:/home/dennis:/bin/bash
#dennis:!:840:30350:Christopher Dennis (LHC)04:/home/dennis:/bin/false
  mapperu[537] = 2700
  #lhcb
  mapperu[845] = 21112
#malde:*:21112:10027:Sneha Malde:/home/malde:/bin/bash
#malde:nqsXMP5WR.qRE:845:30160:Sneha Malde (LHCb/CDF)04:/home/malde:/bin/tcsh
  mapperu[850] = 21101
#issever:*:21101:10027:issever:/home/issever:/bin/bash
#issever:swItkjEtvb9P2:850:30350:Cigdem Issever (LHC):/home/issever:/bin/bash
  mapperu[852] = 21528
#deleruen:*:21528:10027:Nicolas Delerue:/home/deleruen:/bin/bash
#deleruen:tkobHNPJliWIM:852:30170:Nicolas Delerue (LC):/home/delerue:/bin/tcsh
  mapperu[888] = 21163
#dale:*:21163:10027:John Dale:/home/dale:/bin/bash
#dale:6jrbdWQVdjFnA:888:30250:John Dale (LiCAS)05:/home/dale:/bin/tcsh
  mapperu[898] = 21158
#wilsont:*:21158:10027:Ted Wilson:/home/wilsont:/bin/bash
#wilsont:!:898:30170:Ted Wilson (LC)Cern:/home/wilsont:/bin/false
  mapperu[918] = 10628
#hays:*:10628:10027:hays:/home/hays:/bin/bash
#hays:ev55oO.ZaXmIw:918:30350:Chris Hays (CDF/ATLAS):/home/hays:/bin/bash
  mapperu[934] = 10209
#macmahon:*:10209:10016:Ewan MacMahon:/home/macmahon:/bin/bash
#macmahon:*:934:10016:Ewan MacMahon (IT Support):/home/macmahon:/bin/bash
  mapperu[936] = 2138917081
#gallas:*:2138917081:10027:gallas:/home/gallas:/bin/bash
#gallas:ZaJewlA9TIwZ2:936:30350:Elizabeth Gallas (ATLAS):/home/gallas:/bin/bash
  mapperu[1000] = 21186
#sheehy:*:21186:10027:Suzanne Sheehy:/home/sheehy:/bin/bash
#sheehy:qf/18RKYpj6sE:1000:30170:Suzanne Sheehy (JAI 07):/home/sheehy:/bin/bash
  mapperu[1001] = 21136
#thomasch:*:21136:10027:Christopher Thomas:/home/thomasch:/bin/bash
#thomasch:VISu7.I.gZujk:1001:30160:Christopher Thomas (LHCb 07):/home/thomas:/bin/bash
  mapperu[1002] = 21165
#farrington:*:21165:10027:Sinead Farrington:/home/farrington:/bin/bash
#farrington:!:1002:30350:Sinead Farrington (ATLAS):/home/sineadf:/bin/false
  mapperu[1003] = 21178
#mjohn:*:21178:10027:Malcolm John:/home/mjohn:/bin/bash
#mjohn:P9bTbyjhd2qjo:1003:30160:Malcolm John (LHCb 07):/home/mjohn:/bin/bash
  mapperu[1011] = 21201
#apolle:*:21201:10027:Rudi Apolle:/home/apolle:/bin/bash
#apolle:!:1011:30350:Rudi Apolle,DWB 658b:/home/apolle:/bin/false
  mapperu[1032] = 21049
#corner:*:21049:10027:Laura Corner:/home/corner:/bin/bash
#corner:j.a5kte7mAyS.:1032:30450:Laura Corner (Laserwire):/home/lcorner:/bin/bash
  mapperu[614] = 30614
  #zeusqcd
  mapperu[1037] = 14623
#povey:*:14623:20020:Adam Povey:/home/povey:/bin/tcsh
#povey:!:1037:33200:Adam Povey (CDF Project Student 2008):/home/povey:/bin/false
  mapperu[1040] = 21295
#lloyd:*:21295:20009:David Lloyd:/home/lloyd:/bin/bash
#lloyd:!:1040:30350:David Lloyd (Atlas Summer student):/home/lloyd:/bin/false
  mapperu[1047] = 21475
#peng:*:21475:10026:peng:/home/peng:/bin/bash
#peng:!:1047:30460:Wang Peng (LPWA Summer student):/home/peng:/bin/false
  mapperu[1075] = 10218
#mohammad:*:10218:10016:Kashif Mohammad:/home/mohammad:/bin/bash
#mohammad:$1$T7WhACFn$c56a/k1qWoeL2tL40KTs41:1075:10016: Kashif Mohammad (ITStaff):/home/mohammad:/bin/bash
  mapperu[1137] = 22163
#gandinip:*:22163:10027:Paolo Gandini:/home/gandinip:/bin/bash
#gandinip:$1$Xu/puukg$a7AVEDUZaFNP2.JsxnB8o/:1137:30160:Paolo Gandini (LHCb 2009):/home/gandinip:/bin/bash


  #filterfile=open(os.path.join(os.getenv('HOME'), "chowner",now, "filteredusers"),"w+")
  #remove_logged_in_users_from_mapperu(mapperu,filterfile)  
  #filterfile.close()

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
  sedder=open(os.path.join(os.getenv('HOME'), "chowner",now, 'sedder.sh'),'w')
  for k in mapperu.keys():
     if not seenuids.has_key(k): continue
     try:
       user=pwd.getpwuid(k).pw_name
     except:
       #probably already translated
       user=pwd.getpwuid(mapperu[k]).pw_name
     if not user:
         print "ahh", user
     strg="sed -i 's|"+user+':\(.*\):'+str(k)+'|'+user+':\\1:'+str(mapperu[k])+"|' /var/yp/src/passwd" 
     print strg
     sedder.write(strg+'\n')
  sedder.close()

if __name__ == "__main__":
  target='/data'
  if len( sys.argv ) > 1:
      target=sys.argv[1]
  
  domain(target)

