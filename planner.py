import sys
import argparse
from datetime import datetime, timedelta

#TODO: support to add the local time for that pop

WEEKDAYS = ['MON','TUE','WED','THU','FRI','SAT','SUN']
PODS = ['AUD','MED','REC','REF','ZINC']

#######################################
############ UTILITY FUNCTIONS#########
def generateLines(file):
	fp = open(file,'r')
	lines = fp.readlines()
	fp.close()
	for i in range(0,len(lines)):
		lines[i] = lines[i].split('\n')[0]
	return lines

def processCron(line):
	temp = line[30:-2].split(' ')

	if len(temp[0]) != 2:
		temp[0] = '0'+ temp[0]

	if len(temp[1]) != 2:
		temp[1] = '0' + temp[1]
	#sample temp: ['20', '13', '?', '*', 'MON-FRI', '*']
	return [temp[1] + ':' + temp[0], temp[4]]

def toHrs(time, ampm):
	temp = time.split(':')
	hrs = temp[0]

	if len(temp)==1:
		minutes = '0'
		time += ':' + minutes
	else:
		minutes = temp[1]

	if ampm == 'AM' and hrs == '12':
		return '0:' + minutes
	if ampm == 'AM':
		return time
	if ampm == 'PM' and hrs == '12':
		return time
	return str(int(hrs) + 12) + ':' + minutes

#returns a range
def processWEEKDAYS(query):
	temp = query.split('-')

	for i in range(0,len(WEEKDAYS)):
		if temp[0] == WEEKDAYS[i]:
			break

	for j in range(i,len(WEEKDAYS)):
		if temp[1] == WEEKDAYS[j]:
			break

	return range(i,j+1,1)

#the diff between ST and UTC
def getDiff(timezone):
	diff = ['','','0']

	if timezone == 'PST':
		#+7 or (-17)%24 = 7 
		diff[0] = '-'
		diff[1] = '17'
	elif timezone == 'IST':
		diff[0] = '-'
		diff[1] = '5'
		diff[2] = '30'
	elif timezone == 'IST(Ireland)':
		diff[0] = '-'
		diff[1] = '1'
	elif timezone == 'SGT':
		diff[0] = '-'
		diff[1] = '8'
	elif timezone == 'AWST':
		diff[0] = '-'
		diff[1] = '8'
	elif timezone == 'ACST':
		diff[0] = '-'
		diff[1] = '9'
		diff[2] = '30'
	elif timezone == 'AEST':
		diff[0] = '-'
		diff[1] = '10'
	else:
		print('Timezone not calliberated')
		sys.exit(0)

	return diff

def adjustDays(days, shift):

	weekdays_dict = { 0: 'SUN', 1: 'MON', 2: 'TUE', 3: 'WED', 4:'THU', 5:'FRI', 6: 'SAT', 7: 'SUN' }
	rev_weekdays_dict = { 'SUN': 0, 'MON' : 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6, 'SUN': 7 }

	temp = days.split('-')

	return weekdays_dict[(rev_weekdays_dict[temp[0]] + shift)%7] + '-' + weekdays_dict[(rev_weekdays_dict[temp[1]] + shift)%7] 

def toUTC(time, ampm, timezone):
	time = toHrs(time,ampm)
	diff = getDiff(timezone)
	s1 = time
	s2 = diff[1] + ':' + diff[2]
	fmt = '%H:%M'
	tdelta = datetime.strptime(s1, fmt) - datetime.strptime(s2, fmt)
	days, seconds = tdelta.days, tdelta.seconds
	
	if timezone == 'PST' and int(time.split(':')[0]) >= 17:
		days = 1
	elif timezone == 'PST' and int(time.split(':')[0]) < 17:
		days = 0

	hours = (days * 24 + seconds // 3600)%24
	minutes = (seconds % 3600) // 60
	seconds = seconds % 60
	return (days,str(hours) + ':' + str(minutes))
######################################

######################################
##########IMPORTANT DATA STRUCTURES###
def populate_sched_dict(lines):

	#0-AUD, 1-MED, 2-REC, 3-REF, 4-ZINC
	sched_dict = { 0:[], 1:[], 2:[], 3:[], 4:[] } 
	for i in range(0,len(lines)):
		if lines[i][4:21] == "application_index":
			pod = int(lines[i][24]) 
			pod_schedule = processCron(lines[i+2])
			pod_schedule.append(int(lines[i+3][24:]))
			#sample pod_schedule: ['22:20', 'MON-FRI', 14]
			sched_dict[pod].append(pod_schedule)
	return sched_dict

def populate_data(sched_dict):

	# data = {
	# 			AUD: {MON: [], TUE: [], WED: [], THU: [], FRI: [], SAT: []}
	# 		 }
	#MON:SUN - 0:6
	data = { 
		0: {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6:[]},
		1: {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6:[]},
		2: {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6:[]},
		3: {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6:[]},
		4: {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
	}

	for i in range(0,len(sched_dict)):
		for j in range(0,len(sched_dict[i])):
			for k in processWEEKDAYS(sched_dict[i][j][1]):
				data[i][k].append([sched_dict[i][j][0],sched_dict[i][j][2]])

	for i in range(0,len(data)):
		for j in range(0,len(data[i])):
			data[i][j].sort(key = lambda x:x[0])

	return data
#######################################

############################
##### VIEW SCHEDULES #######
def viewSchedules(file_name):
	lines = generateLines(file_name)
	sched_dict = populate_sched_dict(lines)
	data = populate_data(sched_dict)
	print_data_plan(data)

def print_data_plan(data):
	# debugging print
	for i in range(0,len(data)):
		print("-----" + PODS[i] + "------")
		for j in range(0,len(data[i])):
			print(WEEKDAYS[j] + ": " + str(data[i][j]))
		print("")
#############################

#####################################
########## INPUT SCHEDULE ###########
def processInputSchedule(text, region):
	# text = 'Scale Up,AUD,10,3:20,AM,IST,MON-FRI' #sample query
	elements = text.split(',')
	scaling = elements[0]
	pod_name = elements[1]
	
	index = ''
	if pod_name == 'AUD':
		index = '0'
	elif pod_name == 'MED':
		index = '1'
	elif pod_name == 'REC':
		index = '2'
	elif pod_name == 'REF':
		index = '3'
	elif pod_name == 'ZINC':
		index = '4'
	else:
		print('Invalid pod name')
		sys.exit(0)

	replicas = elements[2]
	day_shift, utc_time = toUTC(elements[3],elements[4],elements[5])
	days = elements[6]
	adjusted_days = adjustDays(days,day_shift)
	local_time = elements[3] + ' ' + elements[4] 
	return makeOutput(scaling,pod_name,index,replicas,local_time, utc_time,days,adjusted_days)

def getInputSchedule():
	print("Give the schedule to be added")
	# input_schedule = input("Scale up/Scale down: ")
	# input_schedule += ',' + input("AUD/MED/REF/REC/ZINC: ")
	# input_schedule += ',' + input("# of replicas: ")
	# input_schedule += ',' + input("Time (HH:MM): ")
	# input_schedule += ',' + input("AM/PM: ") 
	# input_schedule += ',' + input("PST/IST/IST(Ireland)/SGT/AWST/ACST/AEST: ")
	# input_schedule += ',' + input("Weekdays e.g.(MON-FRI):  ")
	input_schedule = 'Scale Up,ZINC,7,6:20,PM,PST,MON-FRI'
	return input_schedule
#####################################

#####################################
############# CHECKING SCHEDULE #####
def checkScheduleAlreadyPresent(lines, gslines):
	sched_dict = populate_sched_dict(lines)
	app_index = int(gslines[1][24])
	utc_time,weekdays = processCron(gslines[3])

	for i in range(0,len(sched_dict[app_index])):
		if [utc_time, weekdays] == sched_dict[app_index][i][:2]:
			return True

	return False

def checkSchedule(ifile, iSchedule):
	lines = generateLines(ifile)

	generatedSchedule = processInputSchedule(iSchedule)
	gslines = generatedSchedule.splitlines()

	if checkScheduleAlreadyPresent(lines,gslines):
		print('Schedule Already Present')
		print(generatedSchedule)
######################################

#######################################
############# ADDING SCHEDULE #########
def addSchedule(ifile, ofile, iSchedule):

	lines = generateLines(ifile)

	region = getRegion(lines)

	generatedSchedule = processInputSchedule(iSchedule, region)
	gslines = generatedSchedule.splitlines()
	
	if checkScheduleAlreadyPresent(lines,gslines):
		print('-----Schedule Already Present, Nothing Added, No new file Generated-----')
		viewSchedules(ifile)
	else:
		#'  }' -> '  },'
		lines[-2] += ','
		for gsline in gslines:
			lines.insert(-1,gsline)
		writeToFile(ofile,lines)
		print('\nAdded Schedule:\n' + generatedSchedule)
		viewSchedules(ofile)

def writeToFile(ofile, lines):
	fp = open(ofile,'w')
	for line in lines:
		fp.writelines(line + '\n')
	fp.close()

def makeOutput(scaling, pod_name, index, replicas, local_time, utc_time, days, adjusted_days):
	schedule =  "  {\n"
	schedule += "    application_index = " + index + "\n"
	schedule += "    schedule_name     = " + "\"<" + scaling + "> Set " + pod_name + " replicas to " + replicas + " at " + local_time + " Local Time " + days + "\"\n"
	schedule += "    schedule          = " + "\"cron(" + utc_time.split(':')[1] + " " + utc_time.split(':')[0] + " ? * " + adjusted_days + " *)\"\n"
	schedule += "    min_replicas      = " + replicas + "\n"
	schedule += "  }\n"
	return schedule

def getRegion(lines):
	for line in lines:
		if line[0:16] == 'k8s_cluster_name':
			if 'us-west-2' in line:
				return 'PST'
			if 'ap-south-1' in line:
				return 'IST'
			if 'eu-west-1' in line:
				return 'IST(Ireland)'
			break
########################################

##############################################
########### REMOVE SCHEDULE (one at a time) ##
def removeSchedule(ifile, ofile, iSchedule):

	lines = generateLines(ifile)

	generatedSchedule = processInputSchedule(iSchedule)
	gslines = generatedSchedule.splitlines()
	
	if remove(ofile, lines, gslines):
		print("Successfully removed the schedule\n" +generatedSchedule)
		viewSchedules(ofile)
	else:
		print("Schedule not present in the input file, nothing to be removed")
		viewSchedules(ifile)

def remove(ofile, lines, gslines):
	app_index = gslines[1][24]
	utc_time, weekdays = processCron(gslines[3])	

	i = 0
	while i < len(lines)-1:
		if lines[i+1][4:21] == 'application_index' and lines[i+1][24] == app_index and [utc_time,weekdays] == processCron(lines[i+3]):
			lines.pop(i)	# {
			lines.pop(i)	#     application_index = 0
			lines.pop(i)	#     schedule_name     = "<Scale Up> Set AUD replicas to 7 at 5 20 AM Local Time MON-FRI"
			lines.pop(i)	#     schedule          = "cron(20 12 ? * MON-FRI *)"
			lines.pop(i)	#     min_replicas      = 7
			lines.pop(i)	# },
			lines[-2] = '  }'
			writeToFile(ofile, lines)
			return True
		i += 1
	return False
##############################################	

def parse_args(args):
    desc = 'Tool to generate plans'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-i', '--inputfile', required=True, help='Input File')
    parser.add_argument('-o', '--outputfile', required=False,default='output.tfvars',help='Output File')
    parser.add_argument('-v','--operation',required=False,default='view', help='Operation to be performed')
    args = parser.parse_args(args)
    return args

def main(args):
    args = parse_args(args[1:])
    input_file_name = args.inputfile
    output_file_name = args.outputfile
    oper = args.operation

    if oper == 'view':
    	viewSchedules(input_file_name)
    elif oper == 'add':
    	addSchedule(input_file_name, output_file_name, getInputSchedule())
    elif oper == 'check':
    	checkSchedule(input_file_name, getInputSchedule())
    elif oper == 'remove':
    	removeSchedule(input_file_name, output_file_name, getInputSchedule())
    else:
    	#TODO
    	print('functionality to be added')

if __name__ == '__main__':
    sys.exit(main(sys.argv))

