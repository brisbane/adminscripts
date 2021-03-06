#!/usr/bin/env python
import datetime, os, sys, re, time
import array
import translation_matrix

#matcher1=re.compile(r".*;([\d+]*[\[\d+*\]]*)\.pplxtorque0\d+.physics.ox.ac.uk;.*user=(\w+).*group=(\w+).*queue=(\w+).*etime=(\d+).*start=(\d+).*Resource_List.cput=(\d+[:\d+]*).*resources_used.cput=(\d+[:\d+]*).*resources_used.walltime=(\d+[:\d+]*)")
matcher1=re.compile(r".*;([\d+]*[\[\d+*\]]*)\.pplxtorque0\d+.physics.ox.ac.uk;user=(.*) group=(.*) jobname=.*queue=(\w+).*etime=(\d+).*start=(\d+).*resources_used.cput=(\d+[:\d+]*).*resources_used.walltime=(\d+[:\d+]*)")
matcher2=re.compile(r".*;([\d+]*[\[\d+*\]]*)\.pplxtorque0\d+.physics.ox.ac.uk;user=(.*) group=(.*) jobname=.*queue=(\w+).*etime=(\d+).*start=(\d+).*Resource_List.cput=(\d+[:\d+]*)")
#matcher=re.compile(r".*;([\d+]*[\[\d+*\]]*)\.pplxtorque0\d+.physics.ox.ac.uk;.*user=(\w+).*group=(\w+).*queue=(\w+).*etime=(\d+).*start=(\d+).*Resource_List.cput=(\d+[:\d+]*)")
#matcher=re.compile(r".*;([\d+]*[\[\d+*\]]*)\.pplxtorque0\d+.physics.ox.ac.uk;.*user=(\w+).*group=(\w+).*queue=(\w+).*etime=(\d+).*start=(\d+).*Resource_List.cput=(\d+[:\d+]*).*resources_used.walltime=(\d+[:\d+]*)")
timeparser=re.compile(r"([\d+]*):([\d+]*):([\d+]*)")
ppnmatch=re.compile(r".*Resource_List.*ppn=([\d+]*)")
memmatch=re.compile(r".*resources_used.mem=([\d+]*)([kmgb]*)")
memreqmatch=re.compile(r".*Resource_List.mem=([\d+]*)([kmgb]*)")

test="05/12/2015 21:33:57;E;9486008.pplxtorque05.physics.ox.ac.uk;user=brisbane group=Physics IT Support jobname=test.sh queue=vsim ctime=1431462735 qtime=1431462735 etime=1431462735 start=1431462736 owner=brisbane@pplxint8.physics.ox.ac.uk exec_host=jailxwn01.physics.ox.ac.uk/0 Resource_List.mem=4gb Resource_List.neednodes=1 Resource_List.nodect=1 Resource_List.nodes=1 session=37342 end=1431462837 Exit_status=0 resources_used.cput=00:00:00 resources_used.mem=3160kb resources_used.vmem=29016kb resources_used.walltime=00:01:41"
onlytest=False
global min_t
min_t=-1
global max_t
max_t=-1

global this_month
brisbane='brisbane'
global sl5

def check_os():
   global sl5
   sl5=0
   f=open('/etc/issue')
   for i in f:
    
      if i.find('inux release 5') != -1:
         sl5=1
         break
   f.close()       

def filterinputfile(f):
   if f[0:4]=="2016" and ( f[6:7] == '1' or  f[6:7] == '2' )  : return 1
   if f[0:4]=="2015" :
       if f[4:6] == "11" or ( f[4:6] != '12' and f[6:7] !=  '3' and f[6:7] != '2' ) : return 1
   return 0
global calcmonth, calcyear
global calcmonthmin, calcyearmin
calcmonth=datetime.datetime.utcnow().month
calcyear=datetime.datetime.utcnow().year
def mintime():
      
     global min_t, calcmonth, calcyear, calcmonthmin, calcyearmin
     if min_t == -1: 
        
        calcmonthmin = calcmonth-1
        if this_month:
           calcmonthmin = calcmonth
        calcyearmin=calcyear
        if calcmonthmin < 1:
           calcmonthmin=12
           calcyearmin=calcyear-1
        min_t = time.mktime((calcyearmin,calcmonthmin,01,00,00,0,0,0,0))
     return min_t
def maxtime():
     global max_t
     global calcmonth, calcyear
     if max_t == -1:
        if this_month:
           calcmonth=calcmonth+1
           if calcmonth > 12:
              calcmonth=1
              calcyear+=1    
        max_t = time.mktime((calcyear,calcmonth,01,00,00,0,0,0,0))

     return max_t


class jobinfo:

   def __init__(self,etime,start): 
        self.initquick()
        self.qtime=qtime
        self.start=start
#        self.cput=req_cput
        
   def timeslice(self, width):
       return int(self.hour())/width

   def isbetweentimerange(self, start, end):
       din=datetime.datetime.fromtimestamp(self.hour()*3600)
       d=time.mktime(din.timetuple())
       if d > start and d < end:
           return True
       return False
       
   def hour(self):
        if self._hour == -1:
            #d=datetime.datetime.fromtimestamp(self.start)
            #self._hour=d.hour
            #self._year = d.year
            #self._month = d.month
            #self._day = d.day 
             self._hour=self.etime/3600            
        return self._hour
  
        #return self._hour
   def __init__(self,pline):
        self.initquick()
        
          
        grouptuple=jobinfo.parseline(pline)
        if not grouptuple: 
            print pline 
            sys.exit(1)
        self.new_from_tuple(grouptuple)
        
   def initquick(self):
        self.usedwalltime=-1
        self.usedcput=-1
        self.ppn=1
        self.mem=3000000
   def new_from_tuple(self,grouptuple):
        if len(grouptuple) == 9:
            self.jobid, self.user,          self.group, self.queue,          self.etime, self.start,    self.usedcputstr, self.usedwalltimestr, self.ppn= grouptuple 

        elif len(grouptuple) == 7 :
             self.jobid, self.user,          self.group, self.queue,          self.etime, self.start ,  self.ppn= grouptuple
             self.usedwalltime=-1
             self.usedcput=-1
        else:
            print grouptuple , 'unexpected'
            sys.exit(1)
        self.etime=int(self.etime)
        self.start=int(self.start)
        
        self._hour=-1
        self.group = translation_matrix.translate_group( self.group, self.user )
        return 
   
   def jobnum(self):
        return self.jobid
   def walltime(self):
        return  self.finish - self.start 
   def getusedwalltime(self):
            if self.usedwalltime != -1: 
               return self.usedwalltime
            m=timeparser.match(self.usedwalltimestr)
            groups=m.groups()
            self.usedwalltime = int(groups[1])*60+int(groups[2])+int(groups[0])*3600*self.ppn

   def usedcput(self):
            if self.usedcput != -1: 
               return self.usedcput
            m=timeparser.match(self.usedcputstr)
            groups=m.groups()
            self.usedcput = int(groups[1])*60+int(groups[2])+int(groups[0])*3600*self.ppn
        
   def waittime(self):
        return self.start-self.etime
   @staticmethod
   def lineok(linein):
       if linein.find("esources_used.wall") == -1 :   
 #      if linein.find("exec_host") == -1:
           return False
       return True

   @staticmethod
   def parseline(line):

     if not jobinfo.lineok(line): 
        print "line not ok"
        return None
     try:
       ppn=1
       mem=3000000000
       
       if line.find('ppn=') != -1:
          ppn=int(ppnmatch.match(line).groups()[0])
       if line.find('used.mem=') != -1:
          toomuchperjob=6000000000
          grps=memmatch.match(line).groups()
          if len(grps) > 1:
              mem=int(grps[0])
          elif  len(grps) > 2:
              mem=int(grps[0])

              if grps[1] == 'kb' : mem*=1024
              if grps[1] == 'mb' : mem*=1024*1024
              if grps[1] == 'gb' : mem*=1024*1024*1024
          else: 
             print 'len unexpected '+ line
          if int(mem/toomuchperjob) > ppn:
             ppn=int(mem/toomuchperjob)
       if line.find('Resource_List.mem=') != -1:
          mreqg=memreqmatch.match(line).groups()           
          if len(mreqg) > 1:
              mem=int(grps[0])
          elif len(mreqg) > 2:
              mem=int(grps[0])
              if grps[1] == 'kb' : mem*=1024
              if grps[1] == 'mb' : mem*=1024*1024
              if grps[1] == 'gb' : mem*=1024*1024*1024
          if int(mem/4294967290) > ppn:
             ppn=int(mem/4294967290)         
 
       match=matcher1.match(line)
#       print "for matcher1"
       if len(match.groups()) < 1:
          match=matcher2.match(line)
#       print "for matcher2"
       over=match.groups()
       return over+ ( ppn, )
     except Exception, exception :
        print exception
     return None

class jobstore:
       
       def __init__(self,ujoblendict,gjoblendict,queues):
            #=['testing', 'veryshort', 'shortjobs' , 'normal', 'lowpriority', 'datatransfer']):
            self.ujoblendict=ujoblendict
            self.gjoblendict=gjoblendict 
            self.queues=queues

def write_csv(jobstore):
       global calcmonthmin, calcyearmin, calcmonth, calcyear
       f=open('/tmp/outfile.csv','w')
       f.write("Jobslot hours used between 01/"+ str(calcmonthmin)+'/'+ str(calcyearmin)+ " and 01/"+str(calcmonth)+'/'+str(calcyear)+"\n")
       f.write("By User\n")
       joblendict=jobstore.ujoblendict
       for i in jobstore.queues:
          if i not in joblendict: continue
          f.write(str(i)+'\n')
          dnow=joblendict[i]
          for key in sorted(dnow.iterkeys()):
             print "%d,%s" % (key/3600, dnow[key])
             f.write("%d,%s\n" % (key/3600, dnow[key]) )
       f.write("By Group\n")
       joblendict=jobstore.gjoblendict
       for i in jobstore.queues:
          if i not in joblendict: continue
          f.write(str(i) + '\n')
          dnow=joblendict[i]
          for key in sorted(dnow.iterkeys()):
             print "%d,%s" % (key/3600, dnow[key])
             f.write("%d,%s\n" % (key/3600, dnow[key]) )
       f.close()
       basefname='clusteruse_SL6_'
       global sl5
       if sl5:
            basefname= "clusteruse_SL5_"

       os.system("su -c \"cp /tmp/outfile.csv  /home/brisbane/public_html/clusteruse/"+basefname+str(calcmonthmin)+"_"+str(calcyearmin)+".csv\" "+ brisbane)

class usertimes:
   def __init__(self):
      self.times=dict()
      self.count=dict()
   def add(self,queue,user,time,njobs): 

      if queue not in self.times.keys():
           self.times[queue]=dict()
           self.count[queue]=dict()

      if user not in self.times[queue].keys():
           
           self.times[queue][user]=0
           self.count[queue][user]=0
      self.times[queue][user]+=time*njobs
      self.count[queue][user]+=njobs

   def Output(self):
       print "outputting"
       for i in self.times.keys(): 
           qtot=0
           nuser=0
           for j in self.times[i].keys():

               userav=self.times[i][j]/self.count[i][j]
               print "for queue: ", i, " user: ", j, " wait time average was ",  userav/60, " min"
               qtot+=userav
               nuser+=1
           print "\n\nThe average by user for ", i, " was " , qtot/nuser/60 , "min \n"
              
def write_html(jobstore):
       global calcmonthmin, calcyearmin, calcmonth, calcyear
       f=open('/tmp/outfile.html','w')
       f.write("<h1>Jobslot hours used between 01/"+ str(calcmonthmin)+'/'+ str(calcyearmin)+ " and 01/"+str(calcmonth)+'/'+str(calcyear)+"</h1>\n")
       f.write("<h1>By User</h1>\n")
       joblendict=jobstore.ujoblendict
       for i in jobstore.queues:
          if i not in joblendict: continue
          f.write('<h2>'+str(i) + ':</h2>\n')
          dnow=joblendict[i]
          for key in sorted(dnow.iterkeys()):
             print "%d: %s" % (key/3600, dnow[key])
             f.write("<p> %d: %s</p>\n" % (key/3600, dnow[key]) )
       f.write("<h1>By Group</h1>\n")
       joblendict=jobstore.gjoblendict
       for i in jobstore.queues:
          if i not in joblendict: continue
          f.write('<h2>'+str(i) + ':</h2>\n')
          dnow=joblendict[i]
          for key in sorted(dnow.iterkeys()):
             print "%d: %s" % (key/3600, dnow[key])
             f.write("<p> %d: %s</p>\n" % (key/3600, dnow[key]) )
       f.close()
       f=open('/etc/issue')
       basefname='clusteruse_SL5_'
       for i in f:
          if i.find('inux release 6') != -1:
             basefname= "clusteruse_SL6_"
       f.close()

       os.system("su -c \"cp /tmp/outfile.html  /home/brisbane/public_html/clusteruse/"+basefname+str(calcmonthmin)+"_"+str(calcyearmin)+".html\" "+brisbane)

def avwaittimes(jobs,yunitsm=60,xunitsh=1,userignore=[], groupignore=[], h='all'):
   onlyhour=None
   timeslicewidth=xunitsh
   units=yunitsm
   if not h == 'all':
      onlyhour=h
   nvshort=dict()
   vshort=dict()
   short=dict()
   nshort=dict()
   normal=dict()
   nnormal=dict()
   testing=dict()
   ntesting=dict()
   
   userjobs=dict()
   groupjobs=dict()


   normwait=dict()
   vshortwait=dict()
   testingwait=dict()
   shortwait=dict()

   dictos=[nvshort, vshort,     short, nshort,   nnormal, normal,    ntesting, testing,  shortwait, vshortwait, normwait, testingwait]

   classifier=dict()
   utime=usertimes()      
   
   for j in jobs.values():
      ncut=vcut=scut=60*4000
      
      h=j.timeslice(timeslicewidth)

      if onlyhour and not h == onlyhour:
         continue
      if onlyhour and h == onlyhour:
         print h, j.etime, j.start, j.jobid, j.waittime()
         
      for x in dictos:
          if h not in x:
               x[h]=0

      wt=j.waittime()
      
      if j.getusedwalltime() != -1 and  j.isbetweentimerange(mintime(), maxtime()):
       if j.queue not in userjobs:
          userjobs[j.queue]=dict()
          groupjobs[j.queue]=dict()
       if j.user not in userjobs[j.queue]:
          userjobs[j.queue][j.user]=0
       if j.group not in groupjobs[j.queue]:
          groupjobs[j.queue][j.group]=0
       userjobs[j.queue][j.user] += j.getusedwalltime()
       groupjobs[j.queue][j.group] += j.getusedwalltime()
       translation_matrix.set_user2group(j.user,j.group)

      if j.queue == 'normal' and wt > ncut:
          continue
      if j.queue == 'veryshort' and wt > vcut:
          continue
      if j.queue == 'shortjobs' and wt > scut:
          continue
      if j.queue == 'short' and wt > scut:
          continue


      if j.user in userignore : continue
      if j.group in groupignore : continue

      utime.add(j.queue,j.user,j.waittime(),1)
      if j.queue == 'normal':

          nnormal[h]+=1*units
          normal[h]+=j.waittime()
      if j.queue == 'shortjobs' or j.queue=='short':
          nshort[h]+=1*units
          short[h]+=j.waittime()
      if j.queue == 'veryshort':
          nvshort[h]+=1*units
          vshort[h]+=j.waittime()
      if j.queue == 'testing':
          ntesting[h]+=1*units
          testing[h]+=j.waittime()
  

   for h in nvshort.keys():
      normwait[h]=0
      vshortwait[h]=0
      shortwait[h]=0
      testingwait[h]=0
      if onlyhour and h == onlyhour:
           print normal[h], nnormal[h], ' the two'
      if nnormal[h] == 0:
          normwait[h]='N/A'
      else:
         normwait[h]=normal[h]/nnormal[h]


      if nshort[h] == 0:
          shortwait[h]='N/A'
      else:
         shortwait[h]=short[h]/nshort[h]
      if nvshort[h] == 0:
          vshortwait[h]='N/A'
      else:
         vshortwait[h]=vshort[h]/nvshort[h]
      if ntesting[h] == 0:
          testingwait[h]='N/A'
      else:
         testingwait[h]=testing[h]/ntesting[h]
      atime=datetime.datetime.fromtimestamp((3600*h*timeslicewidth)).strftime("%y%m%d-%H")
      btime=datetime.datetime.fromtimestamp((3600*h*timeslicewidth+timeslicewidth-1)).strftime("%y%m%d-%H")
      print 'average wait time between ', atime,':00 and ', btime,':59 :\n\t normal - ', normwait[h], ' short - ', shortwait[h], ' vshort - ', vshortwait[h] , ' testing - ', testingwait[h]
      if 'N/A' != normwait[h] and normwait[h] > 15000:
          print 'normwait big ',  h
   
   print "userjobs" 

   print userjobs 
   print "groupjobs "
   print groupjobs 

   utime.Output() 
   joblendict={}
   joblendictg={}

   for i in userjobs.keys():
       print i, ':\n'
       if not i in joblendict :
           joblendict[i]={}
       for user in userjobs[i].keys():
          print  user,',', userjobs[i][user]/3600
          joblendict[i][userjobs[i][user]] = user

   
   print '\ngroups:\n'
   for i in groupjobs.keys():
       print i, '\n'
       if not i in joblendictg :
           joblendictg[i]={}

       for grp in groupjobs[i].keys():
          print grp,',', groupjobs[i][grp]/3600   
          joblendictg[i][groupjobs[i][grp]] = grp
   js=''

   global sl5
   if sl5:
       js=jobstore(joblendict,joblendictg,[ 'veryshort', 'shortjobs' , 'normal', 'lowpriority'])
   else:
       js=jobstore(joblendict,joblendictg,[ 'veryshort', 'short' , 'normal', 'lowpriority'])

   write_html(js)
   write_csv(js)

   return normwait, shortwait, vshortwait, testingwait
 
   

def makeplot(name, dicto,timeslice=1):
   f=open('/root/plots/'+name+'.txt', "w")
   voklast=0
   ebar=0
   for k, v in dicto.items():

        vok=str(v)
        if vok=='N/A':
             vok=str(voklast)
             ebar+=60
        else: 
            voklast=vok
            ebar=0
        f.write(str(k*timeslice)+' '+vok+' '+str(ebar)+'\n')

   f.close()
       
def calcwaittime(wt, name, scale=1):

   dkt={"total":{}}
   for k,v in wt.items():
       if v =='N/A' : continue
       d=datetime.datetime.fromtimestamp(k*3600)
       month=d.strftime("%B%y")
       daytype='evening'
       if d.weekday() == 5 or d.weekday() == 6:
          daytype = 'weekend'
       elif d.hour > 11 and d.hour < 18:
          daytype='workhours'
       
       if month not in dkt:
           dkt[month]=dict()
       if daytype not in dkt[month]:
           dkt[month][daytype]=[0,0] 
       if 'overall' not in dkt[month]:
           dkt[month]['overall']=[0,0]
 
       if daytype not in dkt['total']:
           dkt["total"][daytype]=[0,0]
       if 'overall' not in dkt["total"]:
           dkt["total"]['overall']=[0,0]
       dkt[month][daytype][0]+=v
       dkt[month][daytype][1]+=1
       dkt[month]['overall'][0]+=v
       dkt[month]['overall'][1]+=1
       dkt["total"][daytype][0]+=v
       dkt["total"][daytype][1]+=1
       dkt["total"]['overall'][0]+=v
       dkt["total"]['overall'][1]+=1

   d = { "January13": 1,
         "Febuary13": 2,
         "March13": 3,
         "April13": 4,
         "May13": 5,
         "June13":6,
         "July13":7,
         "August13":8,
         "September13":9,
         "October13":10,
         "November13":11,
         "December13":12,
         "January14":13,
         "February14":14,
         "March14":15,
         "April14":16,
         "May14":17,
         "June14":18,
         "July14":19,
         "August14":20,
         "September14":21,
         "October14":22,
         "November14":23,
         "December14":24,
         "January15":25,
         "February15":26,
         "March15":27,
         "April15":28,
         "May15":29,
         "June15":30,
         "total": 999,
       }
   result = sorted(dkt.iteritems(), key=lambda (x, y): (d[x], y))
#   print result

   for m,dtd in result:
#   result=dkt
#   for m,dtd in result.items():

       print "for " , name ," in :", m, "\n"
       for dt, v in dtd.items():
           print "during the ", dt, " wait time averages ", v[0]/v[1]/scale, " minutes"


if __name__=='__main__':

   global this_month

   this_month=0
   if len(sys.argv)>1:
    if sys.argv[1] == '1':
     this_month=1
    elif sys.argv[1]=='0':
     this_month=0 
   jobs={}
   check_os()


#   groupignore=['jai']
   #userignore=[]
   userignore=['derkach']
   groupignore=[]
   accounting_dirs=["/var/torque/server_priv/accounting"]
#   accounting_dirs=["/root/acctest"]
   fullpaths=[]
   #if len(sys.argv) > 1 :
   #   accounting_dirs=[ sys.argv[1] ]
   for i in accounting_dirs:
      for j in os.listdir(i):
          if filterinputfile(j):
              fullpaths.append(os.path.join(i,j))
   
   #TODO - remove after testing
   #fullpaths=[sys.argv[1]]
   if onlytest==True:
     j=jobinfo(test)
   else:
    for f in fullpaths:
      fl=open(f,'r')
      for l in fl.readlines():

        if not jobinfo.lineok(l) :continue
        j=jobinfo(l)
        if j.jobnum() not in jobs:
            jobs[j.jobnum()]=j
      fl.close()
   timeslice=1
   ts=timeslice
   waitscale=60
   n,s,v,t = avwaittimes(jobs,waitscale,1,userignore,groupignore)
   calcwaittime(n,"normal",waitscale/60)
   calcwaittime(t,"testing",waitscale/60)
   calcwaittime(v,"veryshort",waitscale/60)
   global sl5
   if sl5:
         calcwaittime(s,"shortjobs",waitscale/60)
   else:
         calcwaittime(s,"short",waitscale/60)
         


#   makeplot('normal', n,ts) 
#   makeplot('short', s,ts)
#   makeplot('vshort', v,ts)
#   makeplot('testing', t,ts)
