import subprocess
import re
import routerFunctions
from struct import *


"""
spans = []
ipAddresses = {}

output = subprocess.check_output("route -n", shell=True).decode()

ipPattern = re.compile(r'[1][9][2][.]\d\d\d[.]\d[.][0-200]')

matches = ipPattern.finditer(output)

for match in matches:
    spans.append(match.group())

print(spans)

#for ip in spans:
    #ipAddresses.update({output[ip]})
"""
myIDstr = str(201)
nodeGraph = {myIDstr: ['202', '203']}
print(nodeGraph)
nodeGraph.update({myIDstr: ['202']})
print(nodeGraph)
tempGraphData = nodeGraph[myIDstr]
print(tempGraphData)


