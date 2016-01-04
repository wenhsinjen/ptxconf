#! /usr/bin/python
import ptxconftools
from ptxconftools import ConfController
import pygtk
import appindicator
pygtk.require('2.0')
import gtk
import os

iconpath = os.path.dirname( ptxconftools.__file__ )+"/iconStyle03_256.png"
print iconpath

class PTXConfUI():
    def __init__(self):
        # create systray interface
        self.systray = appindicator.Indicator( "testname", iconpath, appindicator.CATEGORY_APPLICATION_STATUS)
        self.systray.set_status(appindicator.STATUS_ACTIVE)

        # construct menu
        menu = gtk.Menu()
        mitem = gtk.MenuItem("option1")
        menu.append(mitem)
        mitem.show()
        mitem = gtk.MenuItem("dummy window")
        menu.append(mitem)
        mitem.connect("activate", self.createDummyWindow)
        mitem.show()
        mitem = gtk.MenuItem("exit")
        menu.append(mitem)
        mitem.connect("activate", self.exit_program)
        mitem.show()

        # attach menu to out system tray
        self.systray.set_menu(menu)
    
    def exit_program(self, callback_data=None):
        gtk.main_quit()

    def createDummyWindow(self, callback_data=None):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        entry = gtk.Entry()
        button_ok = gtk.Button("OK")
        button_cancel = gtk.Button("Cancel")
        button_cancel.connect("clicked", self.destroyDummyWindow)
        vbox = gtk.VBox()
        vbox.pack_start(entry)
        hbox = gtk.HBox()
        hbox.pack_start(button_ok)
        hbox.pack_start(button_cancel)
	vbox.pack_start(hbox)
        self.window.add(vbox)
        self.window.show_all()

    def destroyDummyWindow(self, callback_data=None):
	self.window.destroy()
    
    def main(self):
        gtk.main()


p = PTXConfUI()
p.main()
