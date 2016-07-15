#!/usr/bin/python
'''Calculate total CPU delivered in terms of HEP-SPEC'''
import os, sys, getopt, time, re, array
from optparse import OptionParser

# Option parsing
usage = "%prog [options] FIRSTDAY <LASTDAY> <INPUTDIR>"
parser=OptionParser(usage=usage)
parser.add_option("-f", "--first", action="store", type="string", dest="firstDay", help="First log file to use (YYYYMMDD format).")
parser.add_option("-l", "--last", action="store", type="string", dest="lastDay", help="Last log file to use (YYYYMMDD format); if unset or FIRSTDAY==LASTDAY, then only use FIRSTDAY's logfile.")
parser.add_option("-d", "--dir", action="store", type="string", dest="inputDir", default="/var/spool/pbs/server_priv/accounting/", help="Location of PBS log files.")
parser.add_option("-b", "--boundary", action="store", type="string", dest="boundaryNode", default="40", help="Boundary node. If you have two clusters with different HEPSPEC scores per node, this number should be set to the first node in the additional cluster. At Glasgow, node001-node140 are 1st Generation nodes; node141 and above are 2nd Generation, so we use the (default) value of 141 here. If you have more than two clusters with differing HEPSPEC values, hack this script as necessary.")
parser.add_option("-b1", "--boundary1", action="store", type="string", dest="boundaryNode1", default="62", help="Boundary node, third type of cluster.")
parser.add_option("-w", "--walltime", action="store_true", dest="timeType", help="Results are WALLTIME, rather than CPUTIME (default)")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="This is VERY verbose. I understand the output, you may too...")

(options, sys.argv[1:]) = parser.parse_args()

#assign some initial values
if options.firstDay:
    firstDay=options.firstDay
else:
    print "Define the first log file to be analysed"
    parser.print_help()
    sys.exit(1)

if options.lastDay:
    lastDay=options.lastDay
else:
    lastDay=options.firstDay

if options.verbose:
    verbose=options.verbose
else:
    verbose=False

if options.timeType:
    timeType=options.timeType
else:
    timeType=False

if options.inputDir:
    inputDir=options.inputDir

if options.boundaryNode:
    boundaryNode=options.boundaryNode
if options.boundaryNode1:
    boundaryNode1=options.boundaryNode1

#convert a date in YYYYMMDD format to unix time in seconds
def convertEpoch(inDate):
    epoch=int(time.mktime(time.strptime(inDate, '%Y%m%d')))
    return epoch

#convert a unix time to the YYYYMMDD format
def convertToCal(inEpoch):
    calendarDate=time.strftime('%Y%m%d',(time.gmtime(inEpoch)))
    return calendarDate

#convert sexidecimal time (HH:MM:SS) to seconds
def timeToSecs(inTime):
   try:
	hours, minutes, seconds = inTime.split(':')
   except ValueError:
        return -1
   return int(hours)*3600 + int(minutes)*60 + int(seconds)
    
#scrape the required data out of the PBS log(s)
def scrapeLog(logName):
    #this was the old way of getting data out - can't rely on the data always being in columns 3, 11, 9 & 18
    #fin, fout =os.popen4("zgrep Exit_status "+inputDir+"/"+currentLog + " | awk '{print $3, $11, $9, $18}' | sed 's/=/ /g' | awk '{print $2, $4, $8-$6}' | sed 's/\/.//g' | sed 's/node//g'| sort -g -k 2",'w')

    #so try some more robust data-extraction
    #extract all completed jobs from PBS log
    fin, fout =os.popen4("zgrep Exit_status "+inputDir+"/"+currentLog,'w')
    #open file to store temporary values...could really do this in memory.
    FILE = open("account.tmpfile",'w')
    for line in fout:
	tmpArray= line.split()
	#only use logged event if we have all required fields for it
	if  "group=" in line and "resources_used.cput=" in line and "exec_host=" in line and "resources_used.walltime=" in line:
	    for entry in tmpArray:
	        if "group=" in entry or "resources_used.cput=" in entry:
	    	    FILE.write(entry.split("=")[1]+ " " )
	        if "exec_host=" in entry:
    		    #convert node001/1 etc to just '001'
		    #if your worker nodes have a different naming convention than ours (node001 etc) you'll have to hack this line. enjoy.
		    renamedNode = ((entry.split("=")[1]).split("/")[0]).lstrip('node')
		    FILE.write(renamedNode + " ")
	        if "resources_used.walltime=" in entry:
	            FILE.write(entry.split("=")[1]+ "\n" )
    FILE.close()

#groupDict is a dictionary where keys=unix group names (atlas, atlasprd etc) and values=CPU (or wall) time of job
#this function sums the CPU/Wall time per group
def quickSubSum(groupDict,timeFrame):
    dailyTimeDict = {}
    #for atlas, atlasprd, atlassgm, biomed etc
    for group in groupDict:
    	timesArray = []
	if verbose:
	    print groupDict[group]
	for time in groupDict[group]:
	    if int(time) >= 0:
	        timesArray.append(float(time))
	    else:
		#some of our (mainly NGS) jobs appear to complete with negative CPU time!
		print "Time for " + group + " job was negative ("+ str(time) + ")...disregarding"
	totalTime=sum(timesArray)
	if verbose:
	    print timeFrame + " CPU Time for " + group + "=" + str(totalTime)
    	dailyTimeDict[group]=totalTime
    #return a dictionary mapping unix group to total hours CPU/Wall time used in that given day (ie log)
    return dailyTimeDict

#for a given day, calculate the sum of the delivered CPU per group (ie VO)
def sumDaysTime(boundaryNode, boundaryNode1):
    dailyTimeDict0 = {}
    dailyTimeDict1 = {}
    dailyTimeDict2 = {}
    #open the file; columns are - unix group, workernode ID, CPUtime, Walltime
    #these values are read into dataArray in that order
    FILE = open("account.tmpfile", 'r')
    dataArray = []
    groupDict0 = {}
    groupDict1 = {}
    groupDict2 = {}
    groupDict3 = {}
    for line in FILE:
	job=line.split()
	dataArray.append(job)
    #you want to check that the file was read in correctly? run with -v option
    if verbose:
	print "########################"
	print "dataArray"
	print "########################"
        print dataArray

    #for each PBS log entry (ie completed batch job)
    for element in dataArray:
	#At Glasgow we have 2 classes of machine. Node001-140 and node141-309
        #the two classes have different HEPSPEC scores, so we need to know which node a job ran on
        #boundaryNode is the first node of the second class of machines (ie 141 in our case)
	if element[1] < boundaryNode:
	    if verbose:
	        print element
            #create a dictionary containing unix groups that map to a list of CPU/Wall time values for completed jobs
	    if element[0] not in groupDict0:
		groupDict0[element[0]]=[]
	    if element[0] not in groupDict3:
		groupDict3[element[0]]=[]
	    #element[2] is CPU time, [3] is walltime
	    #using the -w option you can use walltime
	    if timeType:
	        secTime=timeToSecs(element[3])
	    else:
	        secTime=timeToSecs(element[2])
	    groupDict0[element[0]].append(secTime)
	    #groupDict3 doesn't distinguish between the different classes of worker nodes...interesting for calculating the total hours
	    #used by a VO if we don't care about HEPSPEC scores.
	    groupDict3[element[0]].append(secTime)
	elif element[1] > boundaryNode and element[1] < boundaryNode1
	    #now we're dealing with a node >= node141
	    if verbose:
		print element
	    if element[0] not in groupDict1:
		groupDict1[element[0]]=[]
	    if element[0] not in groupDict3:
		groupDict3[element[0]]=[]
	    #element[2] is CPU time, [3] is walltime
	    if timeType:
	        secTime=timeToSecs(element[3])
	    else:
	        secTime=timeToSecs(element[2])
	    groupDict1[element[0]].append(secTime)
	    groupDict3[element[0]].append(secTime)
	 else:
             if verbose:
                print element
            if element[0] not in groupDict2:
                groupDict2[element[0]]=[]
            if element[0] not in groupDict3:
                groupDict3[element[0]]=[]
            #element[2] is CPU time, [3] is walltime
            if timeType:
                secTime=timeToSecs(element[3])
            else:
                secTime=timeToSecs(element[2])
            groupDict2[element[0]].append(secTime)
            groupDict3[element[0]].append(secTime)	
    if verbose:
        print "########################"
        print "groupDict0"
        print "########################"
        print groupDict0
	print "########################"
	print "groupDict1"
	print "########################"
        print groupDict1
	print "########################"
	print "groupDict2"
	print "########################"
        print groupDict2

    #use quickSubSum to sum up the hours delivered to each unix group (ie VO) on a given day
    dailyTimeDict0=quickSubSum(groupDict0, "Daily")
    dailyTimeDict1=quickSubSum(groupDict1, "Daily")
    dailyTimeDict2=quickSubSum(groupDict2, "Daily")
    dailyTimeDict3=quickSubSum(groupDict3, "Daily")

    return dailyTimeDict0, dailyTimeDict1, dailyTimeDict2, dailyTimeDict3



#main code starts here
#want YYYYMMDD dates in unix time format
startEpoch=convertEpoch(firstDay)
endEpoch=convertEpoch(lastDay)
period=(endEpoch-startEpoch)+86400
#accPeriod is the accounting period in days
accPeriod=period/86400
if period < 0:
    print "Error: The end time cannot be before the start time!"
    sys.exit(1)
print "First log file to use ", firstDay, " ( = ", startEpoch, "unix time)"
print "Last log file to use ", lastDay, " ( = ", endEpoch, "unix time)"
print "Accounting period = ", accPeriod, "day(s) ( = ",period,"sec)"
print "Assuming PBS logs are in ", inputDir
print "Assuming your worker nodes are named nodeXXX etc."
print "If they aren't you'll need to tinker with this script."
print "Hint: look for renamedNode= in the code"
if timeType:
    print "Calculating Wall time"
else:
    print "Calculating CPU time"
	
#dictionaries mapping unix group to the daily CPU/Wallclock time delivered
masterTimeDict0={}
masterTimeDict1={}
masterTimeDict2={}
masterTimeDict3={}
for day in range(1, accPeriod+1):
    #print convertToCal(startEpoch+(day*86400))
    currentLog=convertToCal(startEpoch+(day*86400))
    logName=inputDir+"/"+currentLog
    print "########################"
    print "Working on " + currentLog
    print "########################"
    #read the PBS log
    scrapeLog(logName)
    #get 3 dictionaries that map the unix group (hence VO) to CPU/Walltime delivered on a given day
    #dictionary 1 is for ClusterVision nodes; 2 is Viglen and 3 is just a sum of these.
    dailyTimeDict0, dailyTimeDict1, dailyTimeDict2, dailyTimeDict3=sumDaysTime(boundaryNode,boundaryNode1)

    if verbose:
        print "########################"
        print "Subcluster1:"
        print "########################"
        print dailyTimeDict0
        print "########################"
        print "Subcluster2:"
        print "########################"
        print dailyTimeDict1
        print "########################"
        print "Subcluster3:"
        print "########################"
        print dailyTimeDict2


    #append the daily time dictionaries to a master dictionary which will be a mapping of unix group (ie VO) to CPU time delivered.
    for group in dailyTimeDict0:
        if group not in masterTimeDict0:
            masterTimeDict0[group]=[]
        masterTimeDict0[group].append(int(dailyTimeDict0[group]))

    for group in dailyTimeDict1:
	if group not in masterTimeDict1:
	    masterTimeDict1[group]=[]
        masterTimeDict1[group].append(int(dailyTimeDict1[group]))
    if verbose:
        print masterTimeDict1

    for group in dailyTimeDict2:
	if group not in masterTimeDict2:
	    masterTimeDict2[group]=[]
        masterTimeDict2[group].append(int(dailyTimeDict2[group]))
    if verbose:
        print masterTimeDict2

    for group in dailyTimeDict3:
	if group not in masterTimeDict3:
	    masterTimeDict3[group]=[]
        masterTimeDict3[group].append(int(dailyTimeDict3[group]))
    if verbose:
        print masterTimeDict3

#sum the master dictionaries, so we now have a mapping of unix group to CPU delivered (hours) for the entire accounting period
#ie, one entry per day
totalCPU0=quickSubSum(masterTimeDict0,"Total")
totalCPU1=quickSubSum(masterTimeDict1,"Total")
totalCPU2=quickSubSum(masterTimeDict2,"Total")
totalCPU3=quickSubSum(masterTimeDict3,"Total")
if verbose:
    print "############################"
    print "Subcluster #1 Total CPU time"
    print "############################"
    print totalCPU0
    print "############################"
    print "Subcluster #2 Total CPU time"
    print "############################"
    print totalCPU1
    print "############################"
    print "Subcluster #3 Total CPU time"
    print "############################"
    print totalCPU2
    print "############################"
    print " Total CPU time of all the Cluster"
    print "############################"
    print totalCPU3


#num = raw_input("HEPSPEC score (per core) of Subcluster #1 (ie < node " + boundaryNode + ") : ")
#hepSpec1core= int(num)
#num = raw_input("HEPSPEC score (per core) of Subcluster #2 (ie >= node " + boundaryNode + ") : ")
#hepSpec2core= int(num)
#hardcoded values, because I got tired of interactively entering them each time I ran the script.
#these are the HEPSPEC values per core of your (assumed two) clusters. If you only have one cluster, set these equal
hepSpec1core= 3.5
hepSpec2core= 7.22
hepSpec3core= 8.09
print "Using HEPSPEC scores of ", hepSpec1core, ",", hepSpec2core, "and" hepSpec3core, "per core."
print "You will probably want to change the hard-coded variables"
print "hepSpec1core and hepSpec2core to suit your cluster."

masterHEPSPEC = {}
#calculate hepspec delivered for each subcluster, per group and append this to a master dictionary.
for group in totalCPU0:
    hepSpec0total = hepSpec1core * totalCPU0[group]
    if verbose:
        print group, hepSpec0total, "HEPSPEC hours"
    if group not in masterHEPSPEC:
	masterHEPSPEC[group]=[]
    masterHEPSPEC[group].append(float(hepSpec0total))

for group in totalCPU1:
    hepSpec1total = hepSpec1core * totalCPU1[group]
    if verbose:
        print group, hepSpec1total, "HEPSPEC hours"
    if group not in masterHEPSPEC:
	masterHEPSPEC[group]=[]
    masterHEPSPEC[group].append(float(hepSpec1total))

for group in totalCPU2:
    hepSpec2total = hepSpec2core * totalCPU2[group]
    if verbose:
        print group, hepSpec2total, "HEPSPEC hours"
    if group not in masterHEPSPEC:
        masterHEPSPEC[group]=[]
    masterHEPSPEC[group].append(float(hepSpec2total))
#sum up the master dictionary
masterHEPSPECsum = quickSubSum(masterHEPSPEC,"Total")

#show me the results.
print "############################"
print "HEPSPEC hours delivered per group"
print "############################"
sortedKeys=masterHEPSPECsum.keys()
sortedKeys.sort()
for group in sortedKeys:
    print group, "%.d" % round(masterHEPSPECsum[group],0), "HEPSPEChours"

#compare these results to the "Sum CPU" values presented by the accounting portal at
#http://www3.egee.cesga.es/gridsite/accounting/CESGA/egee_view.php
#they should be the same. At Glasgow, we noted disparity with the pheno & nanocmos VOs. See
#https://gus.fzk.de/ws/ticket_info.php?ticket=49246
print "############################"
print "CPU hours delivered per group"
print "############################"
sortedKeys=totalCPU3.keys()
sortedKeys.sort()
for group in sortedKeys:
    if totalCPU3[group] > 1800:
        print group, "%.d" % round(totalCPU3[group]/3600,0), "Hours"
    else:
        print group, " 0 HOURS"

#tidy up after yerself, you mucky pup.
os.remove("account.tmpfile")
