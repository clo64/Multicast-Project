import os, json, glob

#Threshold value for how far destinations can be from RP
threshold = 3
#initalize centralTable JSON
ceteralTable = []

#Create array to store names of all routing tables
contents = []
#Open folder containing all routing tables
dir = os.path.dirname(__file__)
#print("Relative directory is {}".format(dir))
routingTablePath = '{}\\routingTables\\'.format(dir)
json_pattern = os.path.join(routingTablePath, '*.json')
file_list = glob.glob(json_pattern)
for file in file_list:
  contents.append(file)

#Loop over all routing tables and build centeralTable
for file in contents:
    with open(file,'r') as f:
        data = json.load(f)
    
    #Pull costs for each destination on a given router
    #Store them in a serpate array so they can be indiviually parsed later
    destCost = []
    for dest in data["destination"]:
        #print(dest["name"])
        #print(dest["path"])
        #print(dest["cost"])
        destCost.append(dest["cost"])

    #Get Filename
    #Which is also router ID
    (fileName, ext) = os.path.splitext(os.path.basename(file))
    #Create JSON for each router entry
    tableElement = {
        "router": fileName,
        "destDist": destCost,
        "totCost": sum(destCost)
    }

    #Update entry to centeralTable
    ceteralTable.append(tableElement)

print(json.dumps(ceteralTable, indent = 3, sort_keys=True))

#Select RP from centeralized table
selectedRP = ""
costRP = 256
for ii in range(len(ceteralTable)):
    #If router has lower cost it is eligible RP
    if ceteralTable[ii]["totCost"] < costRP:
        #Check destDist against threshold
        #This help in tie breaking if necessary
        if all(yy <= threshold for yy in ceteralTable[ii]["destDist"]):
            selectedRP = ceteralTable[ii]["router"]
            costRP = ceteralTable[ii]["totCost"]
        else:
            continue
    #if ceteralTable[ii]["totCost"] == costRP:

print("The selected RP is : {}".format(selectedRP))
