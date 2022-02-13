from subprocess import Popen, PIPE
from re import match, findall


class ConfController:
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

    def getOutputCommand(self, command, **kwargs):
        # from docs: "[...] the use of shell=True is strongly discouraged in cases where the command string
        # is constructed from external input"
        # http://docs.python.org/2/library/subprocess.html#frequently-used-arguments
        process = Popen(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True, **kwargs)
        retval, stderr = process.communicate()

        if stderr:
            import inspect
            # get previous function name from inspect.stack()[1][3]
            print(f"Errro call from: {inspect.stack()[1][3]}. {stderr}")
        return retval

    def getPointerDeviceMode(self, id):
        """Queries the pointer device mode. Returns "asolute" or "relative" """
        retval = self.getOutputCommand(f"xinput query-state {id}")

        for line in retval.split("\n"):
            if "mode=" in line.lower():
                return line.lower().split("mode=")[1].split(" ")[0]
        return None

    def getPenTouchIds(self):
        """Returns a list of input id/name pairs for all available pen/tablet xinput devices"""
        retval = self.getOutputCommand("xinput list")

        ids = {}
        for line in retval.split("]"):
            if "pointer" in line.lower() and "master" not in line.lower():
                id = int(line.split("id=")[1].split("[")[0].strip())
                name = line.split("id=")[0].encode().split(b"\xb3", 1)[1].strip().decode()
                if self.getPointerDeviceMode(id) == "absolute":
                    ids[name + "(%d)" % id] = {"id": id}
        return ids

    def getMonitorIds(self):
        """Returns a list of screens composing the default x-display"""
        retval = self.getOutputCommand("xrandr")

        display0_dim = {"w": None, "h": None}

        monitors = {}
        id = 1
        for line in retval.split("\n"):
            if line[:8] == "Screen 0":
                # here the xrandr dev meant to call it display 0 in line with xorg.
                for part in line.split(", "):
                    if "current" in part:
                        display0_dim["w"] = int(part.split("current")[1].split("x")[0])
                        display0_dim["h"] = int(part.split("current")[1].split("x")[1])
            elif "connected" in line and "disconnected" not in line:
                port = line.split(" ")[0]
                layout_strings = line.split("(")[0].strip().split(" ")
                for element in layout_strings:
                    if match("^[0-9]+x[0-9]+\+[0-9]+\+[0-9]+$", element.strip()) is not None:
                        placement = element
                if layout_strings[-1].strip().lower() in ("right", "left", "inverted"):
                    rotation = layout_strings[-1].strip().lower()
                else:
                    rotation = None

                w = int(placement.split("x")[0])
                h = int(placement.split("x")[1].split("+")[0])
                x = int(placement.split("x")[1].split("+")[1])
                y = int(placement.split("x")[1].split("+")[2])
                mon_name = port
                monitors[mon_name] = {"w": w, "h": h, "x": x, "y": y, "rotation": rotation, "id": id}
                id += 1

        # add display to monitors
        monitors["display"] = {"w": display0_dim["w"], "h": display0_dim["h"], "x": 0, "y": 0,
                               "rotation": None, "id": id}

        return monitors, display0_dim

    def getDeviceCTM(self, id):
        retval = self.getOutputCommand(f'xinput list-props {id} | grep "Coordinate Transformation Matrix"')
        return [float(val) for val in findall(r"-?\d.\d+", retval)]

    def setDeviceCTM(self, id, ctm=None):
        if ctm is None:
            ctm = [0.5, 0, 0.5, 0, 1, 0, 0, 0, 1]
        ctm = " ".join([str(item) for item in ctm])

        return self.getOutputCommand(f"xinput set-prop {id} 'Coordinate Transformation Matrix' {ctm}")

    def setDeviceOutputMap(self, id, output):
        return self.getOutputCommand(f"xinput --map-to-output {id} {output}")

    def resetDeviceCTM(self, id):
        return self.getOutputCommand(
            f"xinput set-prop {id} 'Coordinate Transformation Matrix' 1 0 0 0 1 0 0 0 1")

    def setDeviceAxesSwap(self, id, swap=False):
        return self.getOutputCommand(f"xinput set-prop {id} 'Evdev Axes Swap' {int(swap)}")

    def setDeviceAxisInversion(self, id, xinv=False, yinv=False):
        return self.getOutputCommand(f"xinput set-prop {id} 'Evdev Axis Inversion' {int(xinv)} {int(yinv)}")

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
        self.setDeviceAxesSwap(id, swap)
        self.setDeviceAxisInversion(id, xinv, yinv)

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
        ctm = self._CTMGenerator(dw, dh, mw, mh, mx, my)
        # self.resetDeviceCTM(penid)
        self.setDeviceCTM(penid, ctm)
        self.setDeviceAxisRotation(penid, rot)

    def _CTMGenerator(self, dw, dh, mw, mh, mx, my):
        """generate coordinate transform matrix for a tablet controlling screen out of n_screens in a row"""
        # returns a normal rightside up matrix and the correct fractions
        return [float(mw) / dw, 0, float(mx) / dw, 0, float(mh) / dh, float(my) / dh, 0, 0, 1]
