#Module confcontroller
#Functions
##CTMGenerator(dw, dh, mw, mh, mx, my)
generate coordinate transform matrix for a tablet controlling screen out of n_screens in a row
#Classes
##ConfController 
This class exposes information about pen/tablet pointing device configuration
and gives methods for reconfiguring those devices
###Ancestors (in MRO)
confcontroller.ConfController
###Class variables
monitorIds
penIds
###Instance variables
penIds
###Methods
####__init__(self)
####getDeviceConfig(self, id)
####getMonitorIds(self)
Returns a list of screens composing the default x-display
####getPenIds(self)
Returns a list of input id/name pairs for all available pen/tablet xinput devices
####refresh(self)
####refreshMonitorIds(self)
reload monitor layout information
####refreshPenIds(self)
reload pen/touch tabled ids
####resetDeviceConfig(self, id)
####setDeviceConfig(self, id, ctm='0.5 0 0.5 0 1 0 0 0 1')
####setPen2Monitor(self, pen, monitor)
Configure pen to control monitor
