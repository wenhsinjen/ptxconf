#! /usr/bin/python3
from os.path import realpath
from signal import SIGINT, SIG_DFL, signal

from confcontroller import ConfController
from monitorselector import MonitorSelector

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk as gtk

try:
    from gi.repository import AppIndicator3 as AppIndicator
except:
    from gi.repository import AppIndicator


class PTXConfUI(gtk.Window):
    # get full path of icon

    def __init__(self):
        super().__init__()

        self.icon_path = realpath("icon/iconStyle03_256.png")
        self.set_icon_from_file(self.icon_path)

        # create systray interface
        self.systray = self._create_systray()

        # construct menu
        self.menu = self._create_menubar()
        self.menu.show_all()

        # attach menu to system tray
        self.systray.set_menu(self.menu)

        # create controller
        self.myConf = ConfController()

    # def resetAllConfig(self, callback_data=None):
    #    self.myConf.resetAllDeviceConfig()

    def _create_systray(self):
        # self.systray = appindicator.Indicator( "testname", iconpath, appindicator.CATEGORY_APPLICATION_STATUS)
        systray = AppIndicator.Indicator.new(
            id="ptxconf",
            icon_name=self.icon_path,
            category=AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )

        systray.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        return systray

    def _create_menubar(self):
        menu = gtk.Menu()

        menu_item = gtk.MenuItem()
        menu_item.set_label("configure")
        menu_item.connect("activate", self._create_ui)
        menu.append(menu_item)

        menu_item = gtk.MenuItem()
        menu_item.set_label("exit")
        menu_item.connect("activate", self.exit_program)
        menu.append(menu_item)

        return menu

    def getActiveInput(self):
        a = self.ptDropdown.get_active_text()
        b = self.ptDropdown.get_active()
        if b > 0:
            return a

    def getSelectedMonitor(self, callback_data=None):
        a = self.monitorDropdown.get_active_text()
        b = self.monitorDropdown.get_active()
        if b > 0:
            return a

    def mapTabletToMonitor(self, callback_data=None):
        # find ids for the right input device
        pen = self.getActiveInput()
        # get the display width, screen_width and screen_offset for CTMGenerator function to calculate matrix
        monitor = self.getSelectedMonitor()
        # call API with these settings
        self.myConf.setPT2Monitor(pen, monitor)

    def _create_ui(self, callback_data=None):
        # first refresh all monitor and touch/pen information
        self.myConf.refresh()

        # This creates a popup window for more detailed configuration if user find necessary.
        # Still incomplete at the moment.
        self.present()  # get window on top level and get focus
        self.set_position(gtk.WindowPosition.CENTER)
        self.set_border_width(20)
        self.set_title("PTXConf")
        self.connect("destroy", self.destroyConfigWindow)

        # create elements
        self._create_monitor_select_widget()

        button_apply = gtk.Button().new_with_label("Apply")
        button_close = gtk.Button().new_with_label("Close")

        button_apply.connect("clicked", self.mapTabletToMonitor)
        button_close.connect("clicked", self.destroyConfigWindow)

        # create labels
        label01 = gtk.Label().new_with_mnemonic("pointer device")
        label02 = gtk.Label().new_with_mnemonic("monitor")

        # create top layout
        vbox = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=20)
        vbox.pack_start(self.monitorSelector, expand=True, fill=False, padding=True)

        # create dropdown layout
        grid = gtk.Grid(row_spacing=6, column_spacing=20)
        grid.set_valign(gtk.Align.CENTER)
        grid.set_halign(gtk.Align.START)

        grid.add(label01)
        grid.attach(self.ptDropdown, 1, 0, 2, 1)
        grid.attach_next_to(label02, label01, gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.monitorDropdown, label02, gtk.PositionType.RIGHT, 1, 1)

        vbox.pack_start(grid, expand=False, fill=False, padding=True)

        # create layout for buttons (with spacing between buttons and horizontal CENTER alignment)
        hboxForButtons = gtk.Box(orientation=gtk.Orientation.HORIZONTAL, spacing=20)
        hboxForButtons.set_halign(gtk.Align.CENTER)

        hboxForButtons.pack_start(button_apply, expand=False, fill=False, padding=True)
        hboxForButtons.pack_start(button_close, expand=False, fill=False, padding=True)
        vbox.pack_start(hboxForButtons, expand=False, fill=False, padding=True)

        self.add(vbox)
        self.show_all()

    def _create_monitor_select_widget(self):
        # create monitor selector widget
        self.monitorSelector = monitorSelector = MonitorSelector(moninfo=self.myConf.monitorIds)
        monitorSelector.connect('button-press-event', self.monSelectorCallback)
        monitorSelector.connect('button-press-event', self.monSelectorCallback)

        # dropdown menus 1 and 2, users choose what input device map to what monitor.
        # create and set up dropdown menu 1: user select from a list of connected pen input devices.
        self.ptDropdown = ptDropdown = gtk.ComboBoxText()
        ptDropdown.set_tooltip_text("choose an input device to configure")
        # getting the list of names of the input device
        # set up the dropdown selection for input devices
        ptDropdown.append_text('Select input device:')
        for i in self.myConf.penTouchIds:
            ptDropdown.append_text(i)
        ptDropdown.set_active(0)

        # ptDropdown.connect("changed", self.getActiveInput)
        # create and set up dropdown menu 2: user select from a list of connected display/output devices.
        self.monitorDropdown = monitorDropdown = gtk.ComboBoxText()
        monitorDropdown.set_tooltip_text("choose a monitor to map the input to")
        # getting the list of display names
        # set up the dropdown selection for monitors
        monitorDropdown.append_text('Select a monitor:')
        for key in self.myConf.monitorIds.keys():
            monitorDropdown.append_text(key)
        monitorDropdown.set_active(0)

        monitorDropdown.handler_id_changed = monitorDropdown.connect("changed", self.monDropdownCallback)

    def monDropdownCallback(self, callback_data=None):
        # update MonitorSelector
        mon = self.monitorDropdown.get_active_text()
        if mon in self.monitorSelector.moninfo:
            self.monitorSelector.set_active_mon(mon)

    def monSelectorCallback(self, widget, event):
        monSelection = widget.get_active_mon()
        selected_monitorDropdown_item = self.monitorDropdown.get_active_text()

        # if different than drop down, update drop down
        if monSelection != selected_monitorDropdown_item:
            # lookup this monitor index in drop down and set it...
            idx = self.myConf.monitorIds.get(monSelection).get("id")
            # careful to disable dropdown changed callback while doing this
            hid = self.monitorDropdown.handler_id_changed
            self.monitorDropdown.handler_block(hid)
            self.monitorDropdown.set_active(idx)
            self.monitorDropdown.handler_unblock(hid)

    def destroyConfigWindow(self, _):
        # close the popup window, app will still be docked on top menu bar.
        self.destroy()

    def exit_program(self, _):
        # This function kills the program PTXConf.
        # Can be called from 2 places, 1 from the appindicator dropdown menu "Exit",
        # another from the config popup window "Exit" button.
        gtk.main_quit()

    def main(self):
        gtk.main()

    # def quit(self, menu=None):
    #     self.running = False
    #     self.exit_program(None)


def main():
    # if program started in terminal one can safely exit the program.
    signal(SIGINT, SIG_DFL)
    app = PTXConfUI()
    app.main()  # start window


if __name__ == "__main__":
    main()
