import subprocess

def getID():
    p = subprocess.Popen("ifconfig | grep 192 | awk '{print $2}' | awk -F. '{print $4}'", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return output

def convertID(id):
    return "192.168.1." + str(id)