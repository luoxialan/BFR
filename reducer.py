#!/usr/bin/env python

import sys
import json
import ast

dataList = []       # list to store the data

mdThreshold = 0.34      # the threshold for MD
threshold = [4, 8, 0.8]   # the threshold for Variance, example [1, 2, 3]
csList = []             # example: [{'No':1, 'N': 10, 'SUM':[], 'SUMSQ':[], :, "Points": [] }]
csSet = []

def getSUMSQ(d):
    sq= float(d)**2
    return sq

def getVariance(item):
    v = []
    v.append(float(item["SUMSQ"][0])/l["N"] - (float(item["SUM"][0])/l["N"])**2)
    v.append(float(item["SUMSQ"][1])/l["N"] - (float(item["SUM"][1])/l["N"])**2)
    v.append(float(item["SUMSQ"][2])/l["N"] - (float(item["SUM"][2])/l["N"])**2)
    return v

def getCombinedVariance(item1, item2):
    sq = []
    s = []
    v = []
    n = int(item2["N"])+int(item1["N"])

    sq.append(float(item1["SUMSQ"][0]) + float(item2["SUMSQ"][0]))
    sq.append(float(item1["SUMSQ"][1]) + float(item2["SUMSQ"][1]))
    sq.append(float(item1["SUMSQ"][2]) + float(item2["SUMSQ"][2]))

    s.append(item1["SUM"][0] + item2["SUM"][0])
    s.append(item1["SUM"][1] + item2["SUM"][1])
    s.append(item1["SUM"][2] + item2["SUM"][2])

    v.append(float(sq[0])/n - (float(s[0])/n)**2)
    v.append(float(sq[1])/n - (float(s[1])/n)**2)
    v.append(float(sq[2])/n - (float(s[2])/n)**2)

    return v

def check(item, threshold):
    result = True
    for i in range(0, len(item), 1):
        if item[i] > threshold[i]:
            result = False
            return result
    return result


def combineClustering(cluster1, cluster2):

    cluster2["SUMSQ"][0] = float(cluster1["SUMSQ"][0]) + float(cluster2["SUMSQ"][0])
    cluster2["SUMSQ"][1] = float(cluster1["SUMSQ"][1]) + float(cluster2["SUMSQ"][1])
    cluster2["SUMSQ"][2] = float(cluster1["SUMSQ"][2]) + float(cluster2["SUMSQ"][2])
    cluster2["SUM"][0] = cluster1["SUM"][0] + cluster2["SUM"][0]
    cluster2["SUM"][1] = cluster1["SUM"][1] + cluster2["SUM"][1]
    cluster2["SUM"][2] = cluster1["SUM"][2] + cluster2["SUM"][2]
    cluster2["N"] = cluster1["N"] + cluster2["N"]
    cluster2["points"].append(cluster1["points"])

    return cluster2

for line in sys.stdin:
    #data_json = json.loads(json.dumps(line))    
    
    l = {}
    l = ast.literal_eval(line)
    
    dataList.append(l)

for i in range(0, len(dataList), 1):
    if len(csList) == 0:
        csList.append(dataList[i])
    else:
        cv = []
        added = 0
        for j in range(0, len(csList), 1):
            cv = getCombinedVariance(dataList[i], csList[j])
            if check(cv, threshold):
                csList[j] = combineClustering(dataList[i], csList[j])
                added = 1
                break
        if added == 0:
            csList.append(dataList[i])


# format data for the importing
for i in range(0, len(csList), 1):
    if len(csList[i]) > 1:
        del csList[i]["SUM"]
        del csList[i]["SUMSQ"]
        csSet.append(csList[i])

for i in range(0, len(csSet), 1):
    print csSet[i]



