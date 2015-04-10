import json
import random

file = open("dataset/yelp_academic_dataset_business.json")

dataList = []           # list to store the data

k = 4                   # the number of clusters
mdThreshold = 0.34      # the threshold for MD
threshold = [6, 8, 9]   # the threshold for Variance, example [1, 2, 3]

resultList = []         # the calculated reslut: MD and Variance
clusterResult = {}		# the result of clustering {type: 1, value: 1}, value means the index

centroidList = []       # expamle: [{'stars': 4.5, 'lati': 40.408735, 'id': u'mVHrayjG3uZ_RLHkLj-AMg', 'long': -79.8663507}]
dsList = []             # expamle: [{'No':1, 'N': 10, 'SUM':[], 'SUMSQ':[], :, "Points": [] }]
csList = []
rsList = []				# expamle: [{'stars': 4.5, 'lati': 40.408735, 'id': u'mVHrayjG3uZ_RLHkLj-AMg', 'long': -79.8663507}]

# read the file and transform into the standard format
while 1:
    lines = file.readlines(10000)   	# read the file by lines
    if not lines:
        break 							# break the loop when finishing reading the file
    for line in lines:
    	data_json = json.loads(line)  	# convert the str to json format
    	d = {"id":data_json["business_id"], "long":data_json["longitude"], "lati":data_json["latitude"],"stars":data_json["stars"]}
    	dataList.append(d) 				# add the dicr to the list
print "item:",len(dataList)

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
		latiFloat = float(rd["lati"])
		longFloat = float(rd["long"])
		starsFloat = float(rd["stars"])
		dsList.append({"No":i, "N":1, "SUM":[latiFloat,longFloat,starsFloat],"SUMSQ":[latiFloat**2, longFloat**2,starsFloat**2], "Points":[rd]})
		centroidList[len(centroidList)-1]["No"]= i

print "random centroids:"
for i in range(0, len(centroidList), 1):
	print centroidList[i]
print ""

# clustering
def getSUMSQ(d):
	sq= float(d)**2
	return sq

def getVariance(l):
	v = [] 
	v.append(float(l["SUMSQ"][0])/l["N"] - (float(l["SUM"][0])/l["N"])**2)
	v.append(float(l["SUMSQ"][1])/l["N"] - (float(l["SUM"][1])/l["N"])**2)
	v.append(float(l["SUMSQ"][2])/l["N"] - (float(l["SUM"][2])/l["N"])**2)
	return v

def getCombinedVariance(o1, o2):

	sq = []
	s = []
	v = []

	sq.append(getSUMSQ(o1["lati"]) + float(o2["SUMSQ"][0]))
	sq.append(getSUMSQ(o1["long"]) + float(o2["SUMSQ"][1]))
	sq.append(getSUMSQ(o1["stars"]) + float(o2["SUMSQ"][2]))	
	
	s.append(float(o1["lati"]) + o2["SUM"][0])
	s.append(float(o1["long"]) + o2["SUM"][1])
	s.append(float(o1["stars"]) + o2["SUM"][2])
	
	v.append(float(sq[0])/2 - (float(s[0])/2)**2)
	v.append(float(sq[1])/2 - (float(s[1])/2)**2)
	v.append(float(sq[2])/2 - (float(s[2])/2)**2)

	return v

def getMahalanobis(l1, l2, v):
	md = (((float(l1["lati"]) - float(l2["lati"]))/(v[0]**0.5))**2 + 
		((float(l1["long"]) - float(l2["long"]))/(v[1]**0.5))**2 +
		((float(l1["stars"]) - float(l2["stars"]))/(v[2]**0.5))**2)**0.5
	return md

def getClusterIndex(l, mdThre, varThre, type):
	index = -1
	if type == 1:									# 1: all are variance
		pr = True
		for j in range(0, len(l), 1):
			for i in range(0, len(l[j]["value"]), 1):
				if l[j]["value"][i] > varThre[i]:
					pr = False
					break
			if pr == True:							# If the point find a cluster, then stop. 
				index = j
				return index
		return index

	if type == 2:									# 2: all are md, 
		result = mdThre
		for z in range(0, len(l), 1):
			if l[z]["value"] <= result:
				index = z
				result = l[z]["value"]
		return index

	if type == 3:									# 3: some are md, some are variance
		result = mdThre
		for z in range(0, len(l), 1):
			if l[z]["type"] == 2:					# check the cluster which number of points is bigger than 1 first
				if l[z]["value"] <= result:
					index = z
					result = l[z]["value"]
		
		if index == -1:								# If we can not find a suitable cluster, then check the othet
			r = True
			for j in range(0, len(l), 1):
				if l[j]["type"] == 1:
					for i in range(0, len(l[j]["value"]), 1):
						if l[j]["value"][i] > varThre[i]:
							r = False
							break
					if r == True:					# If we can find a cluster, then stop
						index = j
						return index
			return index
		else:
			return index
		
def getClusterResult(l, mdThre, varThre, k):
	cr = {}							# the result of clustering				
	case = 0 						
	count = 0							
	
	for i in range(0, len(l), 1):
		if l[i]["type"] == 1: 		
			count = count + 1 		# count the number of type 1
	
	if count == k :
		case = 1 					# 1: all are variance
	if count == 0:
		case = 2					# 2: all are md
	if 0 < count < k:
		case = 3 					# 3: some are md, some are variance
	
	if case == 1:
		cr["value"] = getClusterIndex(l, mdThre, varThre, case)
		
		if cr["value"] == -1: 
			cr["type"] = 3 			# 3: means the RS
		else:
			cr["type"] = 1
	if case == 2:
		cr["value"] = getClusterIndex(l, mdThre, varThre, case)
		if cr["value"] == -1: 		# If the point does not belong to any clusters, it would be summarized into RS Set
			cr["type"] = 3
		else:
			cr["type"] = 1
	if case == 3:
		cr["value"] = getClusterIndex(l, mdThre, varThre, case)
		if cr["value"] == -1: 		# If the point does not belong to any clusters, it would be summarized into RS Set
			cr["type"] = 3
		else:
			cr["type"] = 1
	return cr

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

for i in range(0, len(dataList), 1):
	for j in range(0, len(dsList), 1):
		
		if dsList[j]["N"] < 2:  								# if N < 2, then use variance
			td = getCombinedVariance(dataList[i], dsList[j])	# get the combined variance
			resultList.append({"type":1, "value": td})			# store in the result list, type 1 means combined variance
		else:													# if N > 1, then use md
			variance = getVariance(dsList[j])
			md = getMahalanobis(dataList[i],centroidList[j], variance)	# get the MD
			resultList.append({"type":2, "value":md})					# store the result, type 2 means the MD
			
	if(len(resultList) > 0):											# start to clustering, chech which cluster the point belongs to
		
		clusterResult = getClusterResult(resultList, mdThreshold, threshold, k)	# get the clustering result
		if clusterResult["type"] == 1 :											# belongs to a cluster (DS Set)
			
				dsList[clusterResult["value"]] = addToDS(dataList[i], dsList[clusterResult["value"]],)
		if clusterResult["type"] == 3:										
			rsList.append(dataList[i])

	
	resultList = []												# clear the list for the next point
	clusterResult = {}											# clear the dict for the next point

for i in range(0, len(dsList), 1):
	print "cluster", i + 1, ":", dsList[i]["N"]	

print "the number of points in RS:", len(rsList)












