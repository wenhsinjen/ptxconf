import sys
import subprocess
import re

try:
    import configparser
except:
    import ConfigParser as configparser


class ConfController():
    """This class exposes information about pen/tablet pointing device configuration
    and gives methods for reconfiguring those devices"""
    penTouchIds = None
    monitorIds = None
    display = None

    def __init__(self):
        self.penTouchIds = self.getPenTouchIds()
        self.monitorIds, self.display = self.getMonitorIds()

    def refresh(self):
        self.refreshMonitorIds()
        self.refreshPenTouchIds()

    def refreshMonitorIds(self):
        """reload monitor layout information """
        self.monitorIds, self.display = self.getMonitorIds()

    def refreshPenTouchIds(self):
        """reload pen/touch tabled ids"""
        self.penTouchIds = self.getPenTouchIds()

    def getPointerDeviceMode(self, id):
        """Queries the pointer device mode. Returns "asolute" or "relative" """
        retval = subprocess.Popen("xinput query-state %d"%(id), shell=True, stdout=subprocess.PIPE).stdout.read()

        for line in retval.split("\n"):
            if "mode=" in line.lower():
                return line.lower().split("mode=")[1].split(" ")[0]
        return None

    def getPenTouchIds(self):
        """Returns a list of input id/name pairs for all available pen/tablet xinput devices"""
        retval = subprocess.Popen("xinput list", shell=True, stdout=subprocess.PIPE).stdout.read()

        ids = {}
        for line in retval.split("]"):
            if "pointer" in line.lower() and "master" not in line.lower():
                id = int(line.split("id=")[1].split("[")[0].strip())
                name = line.split("id=")[0].split("\xb3",1)[1].strip()
                if self.getPointerDeviceMode(id) == "absolute":
                    ids[name+"(%d)"%id]={"id":id}
        return ids

    def getMonitorIds(self):
        """Returns a list of screens composing the default x-display"""
        retval = subprocess.Popen("xrandr", shell=True, stdout=subprocess.PIPE).stdout.read()

        display0_dim = {"w":None,"h":None}
        monitors = {}
        for line in retval.split("\n"):
            if "Screen 0" == line[:8]:
                # here the xrandr dev meant to call it display 0 in line with xorg.
                for part in line.split(", "):
                    if "current" in part:
                        display0_dim["w"] = int(part.split("current")[1].split("x")[0])
                        display0_dim["h"] = int(part.split("current")[1].split("x")[1])
            elif "connected" in line and "disconnected" not in line:
                port = line.split(" ")[0]
                layout_strings = line.split("(")[0].strip().split(" ")
                for element in layout_strings:
                    if re.match("^[0-9]+x[0-9]+\+[0-9]+\+[0-9]+$",element.strip()) is not None:
                        placement = element
                if layout_strings[-1].strip().lower() in ("right","left","inverted"):
                    rotation = layout_strings[-1].strip().lower()
                else:
                    rotation = None
                w = int( placement.split("x")[0] )
                h = int( placement.split("x")[1].split("+")[0] )
                x = int( placement.split("x")[1].split("+")[1] )
                y = int( placement.split("x")[1].split("+")[2] )
                mon_name = port
                monitors[mon_name]={"w":w, "h":h, "x":x, "y":y, "rotation":rotation}
        # add display to monitors
        monitors["display"]={"w":display0_dim["w"], "h":display0_dim["h"], "x":0, "y":0, "rotation":None}

        return monitors, display0_dim

    def getDeviceCTM(self, id):
        command = subprocess.Popen('xinput list-props %d | grep "Coordinate Transformation Matrix"' % id, shell=True, stdout=subprocess.PIPE).stdout.read()
        return command

    def setDeviceCTM(self, id, ctm="0.5 0 0.5 0 1 0 0 0 1"):
        command = subprocess.Popen("xinput set-prop %d 'Coordinate Transformation Matrix' %s" % (id, ctm), shell=True, stdout=subprocess.PIPE).stdout.read()
        return command

    def resetDeviceCTM(self, id):
        command = subprocess.Popen("xinput set-prop %d 'Coordinate Transformation Matrix' 1 0 0 0 1 0 0 0 1" % id, shell=True, stdout=subprocess.PIPE).stdout.read()
        return command

    def setDeviceAxesSwap(self, id, swap=False):
        command = subprocess.Popen("xinput set-prop %d 'Evdev Axes Swap' %d" % (id, int(swap)), shell=True, stdout=subprocess.PIPE).stdout.read()
        return command

    def setDeviceAxisInversion(self, id, xinv=False, yinv=False):
        command = subprocess.Popen("xinput set-prop %d 'Evdev Axis Inversion' %d %d" % (id, int(xinv), int(yinv)), shell=True, stdout=subprocess.PIPE).stdout.read()
        return command

    def setDeviceAxisRotation(self, id, rotation=None):
        if rotation == "right":
            swap = True
            xinv = False
            yinv = True
        elif rotation == "left":
            swap = True
            xinv = True
            yinv = False
        elif rotation == "inverted":
            swap = False
            xinv = True
            yinv = True
        else:
            swap = False
            xinv = False
            yinv = False
        self.setDeviceAxesSwap(id,swap)
        self.setDeviceAxisInversion(id,xinv,yinv)

    def setPT2Monitor(self, pen, monitor):
        """Configure pen to control monitor"""
        penid = self.penTouchIds[pen]["id"]
        dw = self.display["w"]
        dh = self.display["h"]
        mw = self.monitorIds[monitor]["w"]
        mh = self.monitorIds[monitor]["h"]
        mx = self.monitorIds[monitor]["x"]
        my = self.monitorIds[monitor]["y"]
        rot = self.monitorIds[monitor]["rotation"]
        ctm = CTMGenerator( dw, dh, mw, mh, mx, my)
        #self.resetDeviceCTM(penid)
        self.setDeviceCTM(penid, ctm)
        self.setDeviceAxisRotation(penid,rot)

def CTMGenerator( dw, dh, mw, mh, mx, my ):
    """generate coordinate transform matrix for a tablet controlling screen out of n_screens in a row"""
    return "%f 0 %f 0 %f %f 0 0 1"%(float(mw)/dw, float(mx)/dw, float(mh)/dh, float(my)/dh)
