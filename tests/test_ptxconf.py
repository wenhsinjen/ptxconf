#! /usr/bin/python

from ..src.ptxconf.confcontroller import ConfController

pc = ConfController()
a = pc.penIds
print(pc.penIds)
print(pc.getPenIds())
pc.setDeviceConfig(a[0])
print(pc.getDeviceConfig(a[0]))
pc.resetDeviceConfig(a[0])
print(pc.getDeviceConfig(a[0]))
pc.setDeviceConfig(a[0])
print(pc.getDeviceConfig(a[0]))
