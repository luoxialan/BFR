import json
import random

file = open("yelp_academic_dataset_business.json")

# parameters for input data
data = ""
dataList = [] 		# list to store the data

# parameters for clusters
k = 4
mdThreshold = 0.34
threshold = [6, 8, 9]
resultList = []
#mdResultList = []
clusterIndex = 0
clusterResult = {}
centroidList = [] 	# expamle: [{'stars': 4.5, 'lati': 40.408735, 'id': u'mVHrayjG3uZ_RLHkLj-AMg', 'long': -79.8663507}]
dsList = [] 		# expamle: [{'No':1, 'N': 10, 'SUM':[], 'SUMSQ':[], :, "Points": [] }]
csList = []
rsList = []

# read the file and transform into the standard format
while 1:
    lines = file.readlines(10000)   	# read the file by lines
    if not lines:
        break 							# break the loop when finishing reading the file
    for line in lines:
    	data = data, json.dumps(line) 	# combine the line
    	data_json = json.loads(line)  	# convert the str to json format
    	d = {"id":data_json["business_id"], "long":data_json["longitude"], "lati":data_json["latitude"],"stars":data_json["stars"]}
    	dataList.append(d) 				# add the dicr to the list

# get k centroids
# function: check duplication in the centroid list 
def Duplication(l, id):
	result = True
	for i in range(0, len(l), 1):
		if l[i]["id"] is id:
			result = False
			break
	return result
	
# get the centroids
i = 0
while i < k:
	rd = random.choice(dataList)
	if Duplication(centroidList, rd["id"]):
		centroidList.append(rd)
		i = len(centroidList)
		longFloat = float(rd["long"])
		latiFloat = float(rd["lati"])
		starsFloat = float(rd["stars"])
		dsList.append({"No":i, "N":1, "SUM":[latiFloat,longFloat,starsFloat],"SUMSQ":[latiFloat**2, longFloat**2,starsFloat**2], "Points":[rd]})
		centroidList[len(centroidList)-1]["No"]= i

print "item:",len(dataList)

print "random centroids:"
for i in range(0, len(centroidList), 1):
	print centroidList[i]
print ""

#	print "DS set:"	
# 	for i in range(0, len(centroidList), 1):
#		print dsList[i]

def getSUMSQ(d):
	sumsq = float(d)**2
	return sumsq

def getVariance(l):
	v = [0,0,0] 
	v[0] = float(l["SUMSQ"][0])/l["N"] - (float(l["SUM"][0])/l["N"])**2
	v[1] = float(l["SUMSQ"][1])/l["N"] - (float(l["SUM"][1])/l["N"])**2
	v[2] = float(l["SUMSQ"][2])/l["N"] - (float(l["SUM"][2])/l["N"])**2
	return v

def getMahalanobis(l1, l2, v):
	md = (((float(l1["lati"]) - float(l2["lati"]))/(v[0]**0.5))**2 + 
		((float(l1["long"]) - float(l2["long"]))/(v[1]**0.5))**2 +
		((float(l1["stars"]) - float(l2["stars"]))/(v[2]**0.5))**2)**0.5
	return md

def getTVariance(o1, o2):

	#print "orignal ds set:", 
	#print o2
	#print "The point to be check:"
	#print o1

	sq = [0,0,0]
	s = [0,0,0]
	
	sq[0] = getSUMSQ(o1["lati"]) + float(o2["SUMSQ"][0])
	sq[1] = getSUMSQ(o1["long"]) + float(o2["SUMSQ"][1])
	sq[2] = getSUMSQ(o1["stars"]) + float(o2["SUMSQ"][2])	
	
	#print "The SUMSQ aftering combine:",
	#print sq
	
	s[0] = float(o1["lati"]) + o2["SUM"][0]
	s[1] = float(o1["long"]) + o2["SUM"][1]
	s[2] = float(o1["stars"]) + o2["SUM"][2]
	#print "The SUM after combine:"
	#print s
	
	v = [0,0,0]
	v[0] = float(sq[0])/2 - (float(s[0])/2)**2
	v[1] = float(sq[1])/2 - (float(s[1])/2)**2
	v[2] = float(sq[2])/2 - (float(s[2])/2)**2
	
	#print "The variance:"
	#print v
	#print ""

	return v

def checkThreshold(variance, threshold):
	result = True
	for i in range(0, len(variance)-1, 1):
		if variance[i] > threshold[i]:
			result = False
			break
	return result

def addToDS(item, cluster):
	cluster["SUMSQ"][0] = float(cluster["SUMSQ"][0]) + getSUMSQ(item["lati"])
	cluster["SUMSQ"][1] = float(cluster["SUMSQ"][1]) + getSUMSQ(item["long"])
	cluster["SUMSQ"][2] = float(cluster["SUMSQ"][2]) + getSUMSQ(item["stars"])	
	cluster["SUM"][0] = item["lati"]
	cluster["SUM"][1] = item["long"]
	cluster["SUM"][2] = item["stars"]
	cluster["N"] = cluster["N"] + 1
	cluster["Points"].append(item)
	return cluster

def addToRS(item, ):
	pass


def getClusterIndex(l, t, tList, type):
	if type == 1:
		index = -1 
		result = 0
		r = True
		for j in range(0, len(l), 1):
			for i in range(0, len(l[j]["value"]), 1):
				if l[j]["value"][i] > tList[i]:
					r = False
					break
			if r == True:
				index = j
				return index
				break
		return index
	if type == 2:
		index = -1
		result = t
		for z in range(0, len(l), 1):
			if l[z]["value"] <= result:
				index = z
				result = l[z]["value"]
		return index
	if type == 3:
		index = -1
		result = t
		for z in range(0, len(l), 1):
			if l[z]["type"] == 2:
				if l[z]["value"] <= result:
					index = z
					result = l[z]["value"]
		if index == -1:
			r = True
			for j in range(0, len(l), 1):
				if l[j]["type"] == 1:
					for i in range(0, len(l[j]["value"]), 1):
						if l[j]["value"][i] > tList[i]:
							r = False
							break
					if r == True:
						index = j
						return index
			return index
		else:
			return index
		
def getClusterResult(l, t, tList, k):
	cr = {}
	case = 0 # 1: all are variance, 2: all are md, 3: some are md , some are variance
	t1 = 0
	t2 = 0
	for i in range(0, len(l), 1):
		if l[i]["type"] == 1: # mean variance 
			t1 = t1 + 1
		if l[i]["type"] == 2:
			t2 = t2 + 1
	
	if t1 == k :
		case = 1
	if t2 == k:
		case = 2
	if 0 < t1 < k:
		case = 3

	
	if case == 1:
		cr["value"] = getClusterIndex(l, t, tList, case)
		cr["type"] = 1
	if case == 2:
		cr["value"] = getClusterIndex(l, t, tList, case)
		cr["type"] = 1
	if case == 3:
		cr["type"] = 1
		cr["value"] = getClusterIndex(l, t, tList, case)
		
	return cr

for i in range(0, len(dataList), 1):
	for j in range(0, len(dsList), 1):
		if dsList[j]["N"] < 2:  # if N < 2, then use Threshol
			td = getTVariance(dataList[i], dsList[j])
			resultList.append({"type":1, "value": td})

		else:					# if N > 1, then use md
			variance = getVariance(dsList[j])
			md = getMahalanobis(dataList[i],centroidList[j], variance)
			resultList.append({"type":2, "value":md})
			
	if(len(resultList) > 0):
		clusterResult = getClusterResult(resultList, mdThreshold, threshold, k)
		if clusterResult["type"] == 1 :
			if clusterResult["value"] == -1:
				rsList.append(dataList[i])
			else:
				dsList[clusterResult["value"]] = addToDS(dataList[i], dsList[clusterResult["value"]],)
		if clusterResult["type"] == 2:
			pass
	resultList = []
	clusterResult = {}

for i in range(0, len(dsList), 1):
	print "cluster", i + 1, ":", dsList[i]["N"]	

print "the number of points in RS:", len(rsList)

def CS():
	pass

def RS():
	pass













