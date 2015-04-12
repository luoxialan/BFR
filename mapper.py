import sys
import json

#file = open("dataset/test.json")

dataList = []       # list to store the data

mdThreshold = 0.34      # the threshold for MD
threshold = [6, 8, 9]   # the threshold for Variance, example [1, 2, 3]
csList = []             # example: [{'No':1, 'N': 10, 'SUM':[], 'SUMSQ':[], :, "Points": [] }]

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
    n = item2["N"]
    sq.append(getSUMSQ(item1["lati"]) + float(item2["SUMSQ"][0]))
    sq.append(getSUMSQ(item1["long"]) + float(item2["SUMSQ"][1]))
    sq.append(getSUMSQ(item1["stars"]) + float(item2["SUMSQ"][2]))

    s.append(float(item1["lati"]) + item2["SUM"][0])
    s.append(float(item1["long"]) + item2["SUM"][1])
    s.append(float(item1["stars"]) + item2["SUM"][2])

    v.append(float(sq[0])/(n+1) - (float(s[0])/(n + 1))**2)
    v.append(float(sq[1])/(n+1) - (float(s[1])/(n + 1))**2)
    v.append(float(sq[2])/(n+1) - (float(s[2])/(n + 1))**2)

    return v

def check(item, threshold):
    result = True
    for i in range(0, len(item), 1):
        if item[i] > threshold[i]:
            result = False
            return result
    return result


def addToCS(item, cluster):
    cluster["SUMSQ"][0] = float(cluster["SUMSQ"][0]) + getSUMSQ(item["lati"])
    cluster["SUMSQ"][1] = float(cluster["SUMSQ"][1]) + getSUMSQ(item["long"])
    cluster["SUMSQ"][2] = float(cluster["SUMSQ"][2]) + getSUMSQ(item["stars"])
    cluster["SUM"][0] = cluster["SUM"][0] + item["lati"]
    cluster["SUM"][1] = cluster["SUM"][1] + item["long"]
    cluster["SUM"][2] = cluster["SUM"][2] + item["stars"]
    cluster["N"] = cluster["N"] + 1
    cluster["points"].append({"id":item["id"]})
    return cluster

# input comes from STDIN (standard input)
for line in sys.stdin:
    # remove leading and trailing whitespace
    # convert the str to json format
    data_json = json.loads(line)
    data = {"id":data_json["business_id"], "long":data_json["longitude"], "lati":data_json["latitude"],"stars":data_json["stars"]}
    # add the dict to the list
    dataList.append(data)
          

#while 1:
#    lines = file.readlines(10000)       # read the file by lines
#    if not lines:
#        break                           # break the loop when finishing reading the file
#    for line in lines:
#        data_json = json.loads(json.dumps(line))    # convert the str to json format
#        d = {"id":data_json["business_id"], "long":data_json["longitude"], "lati":data_json["latitude"],"stars":data_json["stars"]}
#        dataList.append(d)              # add the dicr to the list

#print "The number of items:", len(dataList)

for i in range(0, len(dataList), 1):
    if len(csList) == 0:
        latiFloat = float(dataList[i]["lati"])
        longFloat = float(dataList[i]["long"])
        starsFloat = float(dataList[i]["stars"])
        csList.append({"N":1, "SUMSQ":[latiFloat**2, longFloat**2, starsFloat**2],"SUM":[latiFloat,longFloat, starsFloat],"points": [{"id":dataList[i]["id"]}]})
    else:
        cv = []
        added = 0
        for j in range(0, len(csList), 1):
            cv = getCombinedVariance(dataList[i], csList[j])

            if check(cv, threshold):
                #print cv
                csList[j] = addToCS(dataList[i], csList[j])
                added = 1
                break
        if added == 0:
            latiFloat = float(dataList[i]["lati"])
            longFloat = float(dataList[i]["long"])
            starsFloat = float(dataList[i]["stars"])
            csList.append({"N":1, "SUMSQ":[latiFloat**2, longFloat**2, starsFloat**2],"SUM":[latiFloat, longFloat, starsFloat],"points": [{"id":dataList[i]["id"]}]})

for i in range(0, len(csList), 1):
    print csList[i]


