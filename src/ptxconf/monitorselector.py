#! /usr/bin/python3
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, Gdk as gdk


class MonitorSelector(gtk.DrawingArea):
    active_mon_style = (0, 0.7, 0)
    mon_style = (0.5, 0.5, 0.5)
    margin = 10
    line_width = 4

    def __init__(self, moninfo=None, active_mon=""):
        super().__init__()
        self.set_size_request(250, 150)

        if moninfo is None:
            moninfo = {}

        self.moninfo = moninfo
        self.active_mon = active_mon

        self.set_events(gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.on_mouse_click)
        self.connect('draw', self.expose)

    def on_mouse_click(self, _, event):
        mon = self._lookup_xy2mon(event.x, event.y)
        if mon is not None:
            self.set_active_mon(mon)

    def set_active_mon(self, mon):
        self.active_mon = mon
        self.queue_draw()

    def get_active_mon(self):
        """returns graphically active monitor - including total desktop space dubbed display"""
        return self.active_mon

    def monitor_space_px(self):
        total_w = 0.0
        total_h = 0.0
        for m in self.moninfo:
            w = self.moninfo[m]['w']
            x = self.moninfo[m]['x']
            h = self.moninfo[m]['h']
            y = self.moninfo[m]['y']
            if (w + x) > total_w:
                total_w = w + x
            if (h + y) > total_h:
                total_h = h + y
        return total_w, total_h

    def _lookup_xy2mon(self, x, y):
        mon_rectangles = self._get_mon_rectangles()
        for mon in mon_rectangles:
            if mon != "display":
                mx, my, mw, mh = mon_rectangles[mon]
                if mx < x < mx + mw and my < y < my + mh:
                    # then mouse click on monitor
                    return mon
        return "display"

    def _get_mon_rectangles(self):
        size_area = self.size_request()

        w, h = size_area.width, size_area.height

        mons_tw, mons_th = self.monitor_space_px()
        margin = self.margin

        margin_shrink_x = (w - 2.0 * margin) / w
        margin_shrink_y = (h - 2.0 * margin) / h

        w_wo_margins = w * margin_shrink_x
        h_wo_margins = h * margin_shrink_y

        mons_aspect = float(mons_th) / mons_tw
        draw_aspect = float(h_wo_margins) / w_wo_margins

        if mons_aspect < draw_aspect:
            margin_shrink = margin_shrink_x
            scale = float(w) / mons_tw
        else:
            margin_shrink = margin_shrink_y
            scale = float(h) / mons_th

        cent_x = (w_wo_margins - mons_tw * scale * margin_shrink) / 2.0
        cent_y = (h_wo_margins - mons_th * scale * margin_shrink) / 2.0

        mon_rectangles = {}
        for mon in self.moninfo:
            mw = float(self.moninfo[mon]['w']) * scale * margin_shrink
            mh = float(self.moninfo[mon]['h']) * scale * margin_shrink
            mx = float(self.moninfo[mon]['x']) * scale * margin_shrink + margin + cent_x
            my = float(self.moninfo[mon]['y']) * scale * margin_shrink + margin + cent_y
            mon_rectangles[mon] = (mx, my, mw, mh)
        # finally add total display rectangle
        mw = float(mons_tw) * scale * margin_shrink
        mh = float(mons_th) * scale * margin_shrink
        mx = 0.0 + margin + cent_x
        my = 0.0 + margin + cent_y
        mon_rectangles["display"] = (mx, my, mw, mh)
        return mon_rectangles

    # https://pygobject.readthedocs.io/en/latest/guide/cairo_integration.html
    def expose(self, _, cairo):
        mon_rectangles = self._get_mon_rectangles()
        for mon in mon_rectangles:
            if mon == self.active_mon:
                cairo.set_source_rgb(*self.active_mon_style)
            else:
                cairo.set_source_rgb(*self.mon_style)
            cairo.set_line_width(self.line_width)
            x, y, w, h = mon_rectangles[mon]
            lw = self.line_width
            if mon != "display":
                # Note: inset rectangles inset by line width so they don't overlap
                cairo.rectangle(x + lw, y + lw, w - lw, h - lw)
                cairo.stroke()
                cairo.set_font_size(12)
                tx, ty, tw, th, tdx, tdy = cairo.text_extents(mon)
                cairo.move_to(x + w / 2 - tw / 2, y + h / 2 + th / 2)
                cairo.show_text(mon)
            else:
                # draw total display/desktop with different line/no text
                cairo.set_line_width(self.line_width / 2)
                cairo.rectangle(x, y, w + lw, h + lw)
                cairo.stroke()
