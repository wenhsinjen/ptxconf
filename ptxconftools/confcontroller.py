import sys
import subprocess

class ConfController():
    penIds = None

    def __init__(self):
        self.penIds = self.getPenIds()

    def getPenIds(self):
        retval = subprocess.Popen("xinput list", shell=True, stdout=subprocess.PIPE).stdout.read()

        ids = []
	for line in retval.split("]"):
            if "Pen" in line:
                ids.append( int(line.split("id=")[1].split("[")[0].strip()) )
        return ids

    def getDeviceConfig(self, id):
        command = subprocess.Popen('xinput list-props %d | grep "Coordinate Transformation Matrix"' % id, shell=True, stdout=subprocess.PIPE).stdout.read()
        return command

    def setDeviceConfig(self, id):
        command = subprocess.Popen("xinput set-prop %d 'Coordinate Transformation Matrix' 0.5 0 0.5 0 1 0 0 0 1" % id, shell=True, stdout=subprocess.PIPE).stdout.read()
        return command

    def resetDeviceConfig(self, id):
        command = subprocess.Popen("xinput set-prop %d 'Coordinate Transformation Matrix' 1 0 0 0 1 0 0 0 1" % id, shell=True, stdout=subprocess.PIPE).stdout.read()
        return command
