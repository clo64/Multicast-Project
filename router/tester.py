import subprocess
import re
import routerFunctions
from struct import *
import dijkstra
from graphs import Graph


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

if __name__ == "__main__":

    nodeGraph = {
            '101': ['201'],
            '102': ['205'],
            '103': ['206'],
            '104': ['207'],
            '201': ['202', '203', '204', '101'], 
            '203': ['201', '206'], 
            '202': ['201', '205'], 
            '205': ['202', '206', '102'], 
            '204': ['201', '207'], 
            '207': ['204', '206', '104'], 
            '206': ['203', '205', '207', '103']
    }

    graph = Graph(nodeGraph)

    print("Shortest Path")
    print(graph.find_path('101', '103'))

