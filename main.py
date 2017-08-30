#!/usr/bin/python
# try:
import os, sys, signal, pwd
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import socket
import datetime 

sys.path.append('lib')
sys.path.append('libCSS')
import log
import simpleMail
import directory
import timeFunc
import fileFunctions
import userUtil
import versions
import tarSplit2
import pushCSS2
import migrate2
import systemUtil
import programUtil
import dictFunc
# except ImportError:
# 	print "missing modules for main.py"
# 	sys.exit(1)


		
############## variable assignments - begin #####################
baseAssign="LIST/baseVariables.txt"
baseVar = dictFunc.fileToDict(baseAssign, ",")

variableAssign="LIST/variableAssign.txt"
dictVar = dictFunc.fileToDict(variableAssign, "#")
sizeOfBaseDict = len (baseVar)
for x in range(0, sizeOfBaseDict):
	for (n, v) in dictVar.items():
		var = dictVar[n]
		for (key, value) in baseVar.items():
			searchTerm="<"+str(key)+">"
			retVal=var.find(searchTerm)
			if retVal != -1:
				newString = var.replace(searchTerm, value)
				dictVar[n]=newString

for (n, v) in dictVar.items():
	exec('%s=%s' % (n, repr(v)))
os.chdir(scriptDir)
body = ""

start_time = datetime.datetime.now()
hostName=socket.gethostname()
dictVar['hostName'] = hostName
logCount = directory.countFilesWithPrefix ("LOG","log_")
fromaddr = "admin@" + hostName
mailList = {}
mailList['from_addr'] = fromaddr
mailList['to_addr'] = toaddr
type="nearLine"
############## variable assignments - end #####################

l=log.log()
l.setData(prefix, "myLogger")
l.logDelete("LOG",logCount,logNum)
l.info("log count: " + str(logCount))
l.info("start_time: " + str(start_time))
#if file does not exist =>  used to avoid double running the script
retDict=systemUtil.createRaceConditionFile(checkfile)
retVal=int(retDict['retVal'])
comment=retDict['comment']
if retVal == 1:
	mailList['subject'] = "double run script fault - " + scriptName + ":  --- " + checkfile +" exists ---"
	message = "double run script fault - " + scriptName  + ":  --- "+ checkfile + " exists --- \n"
	message = message + comment
	l.abort(message)
	mailList['message'] = message
	simpleMail.shortMessage (mailList)
	sys.exit(1)

for k in retDict:
	print "key:  " + k + " value: "  + str(retDict[k])
#setup function status if it does not exist
if retDict['fileExistPrior'] == "no":
	functionString = "0000"
	systemUtil.updateRaceConditionFile(checkfile, "functionStatus", functionString)
else:
	sep=","
	raceDict=dictFunc.fileToDict( checkfile, sep )
	functionString=raceDict["functionStatus"]

userName=userUtil.getUsername()
l.info ("user name: " + userName)	
total = len(sys.argv)
if total == 2:
	stage=str(sys.argv[1])
	#default production
	#developement
	l.info ("First argument: %s" % str(sys.argv[1]))
else:
	stage="production"	
############################# main - begin ###########################
if stage == "production":
	l.info("production")
	
	key = "functionStatus"
	indexForString = 0
	#migrate2.migrate (lg, mailList, baseAssign, variableAssign, type, remoteHost, user, stage)
	retDict=programUtil.functionStatusWrapReturn ( checkfile, key, indexForString, migrate2.migrate, l, mailList, dictVar, type, remoteHost, user, stage)
	l.info("migrate comments  \n" + retDict['comments'])
	
	indexForString = 2
	#tarSplit2.tarSplit (lg, amount, unit, mailList, stage, baseAssign, dictVar)
	retDict=programUtil.functionStatusWrapReturn ( checkfile, key, indexForString, tarSplit2.tarSplit, l, 2, "TB", mailList, stage, dictVar, type)
	l.info("tarSplit comments  \n" + retDict['comments'])

	indexForString = 3
	#pushCSS2.pushCSS2(lg, mailList, dictVar, type, stage, remoteHost, user)
	retDict=programUtil.functionStatusWrapReturn ( checkfile, key, indexForString, pushCSS2.pushCSS2, l, mailList, dictVar, type, stage, remoteHost, user)
	l.info("pushCSS comments  \n" + retDict['comments'])

elif stage == "development":
	l.info("development")
	migrate.migrate(l, mailList, variableAssign, type)

else:
	l.info("other")
############################# main - end ###########################

end_time =  datetime.datetime.now()
l.info("end_time: " + str(end_time))
timeDict = timeFunc.timeDuration2 (end_time, start_time)
printHours = timeDict['printHours']
printMins = timeDict['printMins']
printSec = timeDict['seconds']
body = scriptName +" script on " + hostName + " took " + str(printHours) + ":" + str(printMins) + " or " + str(printSec) + " seconds to run"
fromaddr = "admin@" + hostName
subject = hostName +" - " + scriptName
mailList['message'] = body 
mailList['subject'] = subject
simpleMail.shortMessage (mailList)
resultDic = fileFunctions.fileDirDeleteBash(checkfile)
if resultDic['retVal'] == 1:
 	subject = hostName +" Warning - checkfile not deleted"
	body = scriptName +"  "  + subject + " /n" + checkfile
	mailList['message'] = body 
	mailList['subject'] = subject
	simpleMail.shortMessage (mailList)

