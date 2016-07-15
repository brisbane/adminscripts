#!/bin/env python
import pwd
from paramiko_demo import doconnect

filterprint=True

systems_to_check=["pplxint5", "pplxint6", "pplxint8", "pplxint9", "ppcryo1", "ppcryo2" ,"ppcryo3", "ppcryo4", "ppcryo6", "ppcryo7", "ppcryo8"]

def get_new_session(t):
  chan =  t.open_session()
  f=chan.makefile()
  return chan, f
  #chan.invoke_shell()

def remove_logged_in_users_from_mapperu(mapperu):
  systems_to_check=["pplxint5", "pplxint6", "pplxint8", "pplxint9", "ppcryo1", "ppcryo2" ,"ppcryo3", "ppcryo4", "ppcryo6", "ppcryo7", "ppcryo8"]



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


    chan.exec_command("last -w")
    thismonth='Feb'
    for u in  f.readlines():
      if u.find(thismonth) != -1 : print u 
      user=u.split(' ')[0].strip()
      if user not in users:
        users.append(user)
    chan.close()
    t.close()
  if len(users) < 2:
     print "Bombing out becuase I couldnt fill the logged in users map with anything"
     sys.exit(1)
  for user in users:
     uid=pwd.getpwnam(user).pw_uid
     if mapperu.has_key(uid):
        print "Filtering out  ", user,  uid, mapperu[uid]
        mapperu.pop(uid)
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

for user in users:
   
   print user,  pwd.getpwnam(user).pw_uid


if filterprint:
  mapperu={}
  mapperu[268] = 10281
  mapperu[272] = 327990491
  mapperu[277] = 10213
  mapperu[282] = 10564 
  mapperu[301] = 21018
  mapperu[313] = 10210
  mapperu[315] = 21119
  mapperu[316] = 21086
  mapperu[319] = 21098
  mapperu[325] = 21067
  mapperu[334] = 21078
  mapperu[380] = 21097
  mapperu[382] = 21016
  mapperu[396] = 21010
  mapperu[443] = 21006 
  mapperu[466] = 21150
  mapperu[475] = 21013
  mapperu[479] = 10560
  mapperu[500] = 7738
  mapperu[508] = 20123
  mapperu[379] = 21017
  mapperu[483] = 2138917078
  mapperu[495] = 21105
  mapperu[536] = 2138917080
  mapperu[574] = 21104
  mapperu[592] = 14509
  mapperu[595] = 21025
  mapperu[618] = 21302
  mapperu[621] = 21014
  mapperu[629] = 21027
  mapperu[631] = 21087
  mapperu[653] = 21026
  mapperu[655] = 21029
  mapperu[709] = 21102
  mapperu[721] = 21085
  mapperu[770] = 106530
  mapperu[784] = 21028
  mapperu[792] = 21132
  mapperu[800] = 21022
  mapperu[811] = 21238
  mapperu[840] = 21060
  mapperu[845] = 21112
  mapperu[850] = 21101
  mapperu[852] = 21528
  mapperu[888] = 21163
  mapperu[898] = 21158
  mapperu[918] = 10628
  mapperu[934] = 10209
  mapperu[936] = 2138917081
  mapperu[1000] = 21186
  mapperu[1001] = 21136
  mapperu[1002] = 21165
  mapperu[1003] = 21178
  mapperu[1011] = 21201
  mapperu[1032] = 21049
  mapperu[1037] = 14623
  mapperu[1040] = 21295
  mapperu[1047] = 21475
  mapperu[1075] = 10218
  mapperu[1137] = 22163

remove_logged_in_users_from_mapperu(mapperu)
