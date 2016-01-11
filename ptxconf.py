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
        mitem = gtk.MenuItem("configure")
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

    # def resetAllConfig(self, callback_data=None):
    #    self.myConf.resetAllDeviceConfig()

    def getActiveInput(self):
        a = self.window.dropDown01.get_active_text()
        b = self.window.dropDown01.get_active()
        if b > 0:
            return a
        
    def getSelectedDisplay(self, callback_data=None):
        a = self.window.dropDown02.get_active_text()
        b = self.window.dropDown02.get_active()
        # myDisplay = self.myConf.monitorIds["a"]
        if b > 0: 
            # print self.myConf.monitorIds[a]
            # c{} = self.myConf.monitorIds[a]
            return a

    def mapTabletToDisplay(self, callback_data=None):
        # find ids for the right input device
        pen = self.getActiveInput()
        # get the display width, screen_width and screen_offset for CTMGenerator function to calculate matrix
        monitor = self.getSelectedDisplay()
        # call API with these settings
        self.myConf.setPen2Monitor(pen, monitor)

    # def cancelAndDestroyDummyWindow(self, callback_data=None):
    #    # undo or reset config by calling the reset function
    #    self.resetAllConfig()
    #    # close the popup window by calling the destroyDummyWindow function
    #    self.destroyDummyWindow()

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
        
        button_apply = gtk.Button("Apply")
        # button_cancel = gtk.Button("Cancel")
        # button_cancel.connect("clicked", self.cancelAndDestroyDummyWindow)
        # button_reset = gtk.Button("Reset")
        # button_reset.connect("clicked", self.resetAllConfig)
        button_exit = gtk.Button("Exit")
        # button_exit.connect("clicked", self.destroyDummyWindow)
        button_exit.connect("clicked", self.exit_program)
        vbox = gtk.VBox()
        hbox01 = gtk.HBox()
        hbox02 = gtk.HBox()
        hbox03 = gtk.HBox()
        label01 = gtk.Label(" tablet id ")
        label02 = gtk.Label(" select screen ")
        # dropdown menus 1 and 2, users choose what input device map to what monitor.
        # creat and set up dopdownmenu 1: user select from a list of connected pen input deivces. 
        dropDown01 = gtk.combo_box_new_text()
        dropDown01.set_tooltip_text("choose an input device to configure")
        # getting the list of names of the input device
        # set up the dropdown selection for input devices
        dropDown01.append_text('Select input device:')
        for i in self.myConf.penIds:
            dropDown01.append_text(i)
        dropDown01.set_active(0)
        # dropDown01.connect("changed", self.getActiveInput)
        # creat and set up dopdownmenu 2: user select from a list of connected display/output deivces.
        dropDown02 = gtk.combo_box_new_text()
        dropDown02.set_tooltip_text("choose a Display device to map the input to")
        # getting the list of display names
        # set up the dropdown selection for monitors
        dropDown02.append_text('Select a monitor:')
        for i in self.myConf.monitorIds:
            dropDown02.append_text(i)
        dropDown02.set_active(0)
        dropDown02.connect("changed", self.getSelectedDisplay)

        # connect apply button to function
        button_apply.connect("clicked", self.mapTabletToDisplay)
        
        
        # inserting all widgets in place
        hbox01.pack_start(label01)
        hbox01.pack_start(dropDown01)
        hbox02.pack_start(label02)
        hbox02.pack_start(dropDown02)
        hbox03.pack_start(button_apply)
        # hbox03.pack_start(button_cancel)
        # hbox03.pack_start(button_reset)
        hbox03.pack_start(button_exit)
	vbox.pack_start(hbox01)
        vbox.pack_start(hbox02)
        vbox.pack_start(hbox03)
        self.window.add(vbox)
        self.window.show_all()

        # store convenient handle to drop down boxes
        self.window.dropDown01 = dropDown01
        self.window.dropDown02 = dropDown02

    def destroyDummyWindow(self, callback_data=None):
        # close the popup window, app will still be docked on top menu bar.
	self.window.destroy()
    
    def main(self):
        gtk.main()


p = PTXConfUI()
p.main()
