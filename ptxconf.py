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

        # instantiate confcontroller
        self.myConf = ConfController()

    def resetConfig(self, callback_data=None):
        # find ids for the right input device
        myid = self.myConf.penIds
        a = myid[0]
        # reset matrixes to 0s
        self.myConf.resetDeviceConfig(a)
        # print in terminal what id of the device was used
        print a

    def mapTabletToDisplay(self, callback_data=None):
        # find ids for the right input device
        myid = self.myConf.penIds
        a = myid[0]
        # first reset Transformation Matrixs back to 0
        self.myConf.resetDeviceConfig(a)
        # then set the Transformation Matrix(currently only set to the 2nd screen out of 2 displays)
        self.myConf.setDeviceConfig(a)
        # print in terminal what id of the device was used
        print a

    def cancelAndDestroyDummyWindow(self, callback_data=None):
        # undo or reset config by calling the reset function
        self.resetConfig()
        # close the popup window by calling the destroyDummyWindow function
        self.destroyDummyWindow()

    def exit_program(self, callback_data=None):
        # This function kills the program PTXConf.
        # Can be called from 2 places, 1 from the appindicator dropdown menu "Exit",
        # another from the config popup window "Exit" button.
        gtk.main_quit()

    def createDummyWindow(self, callback_data=None):
        # This creats a popup window for more detailed configuration if user find necessary.
        # Still incomplete at the moment.
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title("PTXConf")
        self.window.connect("destroy", self.destroyDummyWindow)
        
        button_set = gtk.Button("Set Tablet to Right of 2 Displays")
        button_cancel = gtk.Button("Cancel")
        button_cancel.connect("clicked", self.cancelAndDestroyDummyWindow)
        button_set.connect("clicked", self.mapTabletToDisplay)
        button_reset = gtk.Button("Reset")
        button_reset.connect("clicked", self.resetConfig)
        button_exit = gtk.Button("Exit")
        # button_exit.connect("clicked", self.destroyDummyWindow)
        button_exit.connect("clicked", self.exit_program)
        vbox = gtk.VBox()
        hbox01 = gtk.HBox()
        hbox02 = gtk.HBox()
        hbox03 = gtk.HBox()
        label01 = gtk.Label(" Number of Displays ")
        label02 = gtk.Label(" Mapping to Position ")
        # drop down menus are not doing anything.
        # Future goal is to detect number of screens and which screens to map to. 
        dropDown01 = gtk.combo_box_new_text()
        dropDown01.append_text('Select a number:')
        dropDown01.append_text('1')
        dropDown01.append_text('2')
        dropDown01.append_text('3')
        dropDown01.set_active(0)
        dropDown02 = gtk.combo_box_new_text()
        dropDown02.append_text('Select a position:')
        dropDown02.append_text('Left')
        dropDown02.append_text('Center')
        dropDown02.append_text('Right')
        dropDown02.set_active(0)
        # inserting all widgets in place
        hbox01.pack_start(label01)
        hbox01.pack_start(dropDown01)
        hbox02.pack_start(label02)
        hbox02.pack_start(dropDown02)
        hbox03.pack_start(button_set)
        hbox03.pack_start(button_cancel)
        hbox03.pack_start(button_reset)
        hbox03.pack_start(button_exit)
	vbox.pack_start(hbox01)
        vbox.pack_start(hbox02)
        vbox.pack_start(hbox03)
        self.window.add(vbox)
        self.window.show_all()

    def destroyDummyWindow(self, callback_data=None):
        # close the popup window, app will still be docked on top menu bar.
	self.window.destroy()
    
    def main(self):
        gtk.main()


p = PTXConfUI()
p.main()
