# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler> 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. 
"""

import logging
import sys
import wx
import windowmanager
import wx.lib.agw.floatspin as floatspin
from ast import literal_eval as make_tuple


class FindPosition(wx.Frame):

    def __init__(self, parent, rect):

        wx.Frame.__init__(self,
                          parent=None,
                          style=wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR|wx.NO_BORDER)

        # window rect for determining in/out of bound area
        self._rect = rect

        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._position = wx.StaticText(panel, label="(0,0)")
        sizer.Add(self._position, 0, wx.ALL, 25)

        panel.SetSizer(sizer)

        panel.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        panel.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        panel.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        panel.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

        self.Move(wx.GetMousePosition())
        self.SetMinSize((100, 80))
        self.SetSize((100, 80))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(1)


    def OnKillFocus(self, event):
        self.Destroy()

    def OnRightUp(self, event):
        self.Destroy()

    def GetValue(self):
        return self._relative_position

    def SetValue(self, position):
        self._relative_position = position
        self.Refresh()

    def OnLeftUp(self, event):
        x, y = event.GetPosition()
        w, h = self.GetClientSize()
        x = x/w * 100
        y = y/h * 100
        x = round(x,2)
        y = round(y,2)
        self._relative_position = (x,y)
        self.Close()

    def GetRelativePosition(self):
        cur_x, cur_y = wx.GetMousePosition()
        off_x, off_y, w, h = self._rect

        print( self._rect)
        if cur_x < off_x or cur_y < off_y:
            return None

        adj_y = 52/2 # why adjustqm
        if cur_x > off_x+w or cur_y > off_y+h+adj_y:
            return None


        rel_x = ((cur_x-off_x)/(w-off_x))*100
        rel_y = ((cur_y-off_y)/(h-off_y))*100
        print(rel_x, rel_y)

        return rel_x, rel_y

    def OnKeyUp(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.Close()
        if key == wx.WXK_RETURN:
            self.Close()

    def OnTimer(self, event):
        self.Move(wx.GetMousePosition())
        try:
            rel_x, rel_y = self.GetRelativePosition()
        except:
            self._position.SetLabel("n/a")
            return

        print((rel_x, rel_y))
        text = "%d, %d" % (rel_x, rel_y)
        self._position.SetLabel(text)

class MouseClickRelative(wx.Dialog):

    def __init__(self, parent):

        wx.Dialog.__init__(self,
                           parent,
                           title="Mouse Click Relative")

        # self._variables = variables
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)

        row = 0

        lbl_function = wx.StaticText(panel, label="Window:")
        choices = []
        choices.extend(windowmanager.GetWindowList())
        self.cbox_window = wx.ComboBox(panel, choices=choices)
        btn_refresh = wx.Button(panel, label="Refresh")
        btn_refresh.Bind(wx.EVT_BUTTON, self.OnButton)

        grid.Add(lbl_function, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cbox_window, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btn_refresh, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        self.chk_match_case = wx.CheckBox(panel, label="Match Case")
        self.chk_match_case.SetValue(True)
        self.chk_resize = wx.CheckBox(panel, label="Resize Window")
        self.chk_resize.SetValue(True)
        grid.Add(self.chk_match_case, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.chk_resize, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lbl_offsetx = wx.StaticText(panel, label="Offset (w):")
        self.spin_offsetx = wx.SpinCtrl(panel, min=0, max=5000)
        grid.Add(lbl_offsetx, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_offsetx, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lbl_offsety = wx.StaticText(panel, label="Offset (y):")
        self.spin_offsety = wx.SpinCtrl(panel, min=0, max=5000)
        grid.Add(lbl_offsety, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_offsety, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lbl_offsetx = wx.StaticText(panel, label="Width (x):")
        self.spin_w = wx.SpinCtrl(panel, min=0, max=5000)
        btn_get = wx.Button(panel, label="Get Window Size")
        btn_get.Bind(wx.EVT_BUTTON, self.OnButton)
        grid.Add(lbl_offsetx, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_w, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btn_get, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lbl_offsety = wx.StaticText(panel, label="Height (h):")
        self.spin_h = wx.SpinCtrl(panel, min=0, max=5000)
        btn_set = wx.Button(panel, label="Set Window Size")
        btn_set.Bind(wx.EVT_BUTTON, self.OnButton)
        grid.Add(lbl_offsety, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_h, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btn_set, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)


        row += 1
        lbl_x = wx.StaticText(panel, label="x (%w):")
        self.spin_x = floatspin.FloatSpin(panel, min_val=0, max_val=100)
        self.spin_x.SetDigits(2)
        grid.Add(lbl_x, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_x, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lbl_y = wx.StaticText(panel, label="y (%h):")
        self.spin_y = floatspin.FloatSpin(panel, min_val=0, max_val=100)
        self.spin_y.SetDigits(2)
        btn_find = wx.Button(panel, label="Find Position")
        btn_find.Bind(wx.EVT_BUTTON, self.OnButton)
        grid.Add(lbl_y, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spin_y, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btn_find, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)

        grid.AddGrowableCol(1)

        sbox_sizer.AddSpacer(10)
        sbox_sizer.Add(grid, 1, wx.ALL|wx.EXPAND, 2)
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btn_add = wx.Button(panel, label="Ok", id=wx.ID_OK)
        self.btn_add.Bind(wx.EVT_BUTTON, self.OnButton)
        # self.btn_add.Disable()
        hsizer.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(self.btn_add, 0, wx.ALL|wx.EXPAND, 5)

        #add to main sizer
        sizer.Add(sbox_sizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 2)

        panel.SetSizer(sizer)

        w, h = sizer.Fit(self)

    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "Get Window Size":
            title, winclass = make_tuple(self.cbox_window.GetValue())

            try:
                offw, offh, w, h = windowmanager.GetWindowRect(title, winclass)
            except TypeError as e:
                logging.info(e)
                return

            self.spin_offsetx.SetValue(offw)
            self.spin_offsety.SetValue(offh)
            self.spin_w.SetValue(w)
            self.spin_h.SetValue(h)

            self.Raise()

        elif label == "Set Window Size":
            title, win_class = make_tuple(self.cbox_window.GetValue())

            offw = self.spin_offsetx.GetValue()
            offh = self.spin_offsety.GetValue()
            w = self.spin_w.GetValue()
            h = self.spin_h.GetValue()
            windowmanager.SetWindowSize(title, win_class, offw, offh, w, h)

            self.Raise()

        elif label == "Find Position":
            title, win_class = make_tuple(self.cbox_window.GetValue())
            offw = self.spin_offsetx.GetValue()
            offh = self.spin_offsety.GetValue()
            w = self.spin_w.GetValue()
            h = self.spin_h.GetValue()

            # resize the target window
            # windowmanager.SetWindowSize(title, win_class, offw, offh, w, h)

            rect = [offw, offh, w, h]
            finder = FindPosition(self, rect)
            def on_finder_close(event):
                x, y = finder.GetValue()
                logging.info("Got relative position: %s" % str((x,y)))
                self.spin_x.SetValue(x)
                self.spin_y.SetValue(y)
                event.Skip()
                finder.Destroy()
                self.SetFocus()

            finder.Bind(wx.EVT_CLOSE, on_finder_close)

            # finder.SetSize((w,h))
            # finder.SetPosition((offw,offh))
            x, y = self.spin_x.GetValue(), self.spin_y.GetValue()
            finder.SetValue((x,y))
            finder.Show()
            finder.SetFocus()

        elif label == "Cancel":
            self.EndModal(id)
        elif label == "Ok":
            self.EndModal(id)
        elif label == "Refresh":
            value = self.cbox_window.GetValue()
            self.cbox_window.Clear()
            choices = []
            choices.extend(windowmanager.GetWindowList())
            self.cbox_window.Append(choices)
            self.cbox_window.SetValue(value)

    def SetValue(self, data):
        window = data["window"]
        self.cbox_window.SetValue(window)

        case = data["matchcase"]
        resize = data["resize"]
        self.chk_match_case.SetValue(case)
        self.chk_resize.SetValue(resize)

        offsetx = data["offsetx"]
        offsety = data["offsety"]
        self.spin_offsetx.SetValue(offsetx)
        self.spin_offsety.SetValue(offsety)

        width = data["width"]
        height = data["height"]
        self.spin_w.SetValue(width)
        self.spin_h.SetValue(height)

        x = data["x"]
        y = data["y"]
        self.spin_x.SetValue(x)
        self.spin_y.SetValue(y)

    def GetValue(self):
        data = []
        data.append(("window", self.cbox_window.GetValue()))
        data.append(("matchcase", self.chk_match_case.GetValue()))
        data.append(("resize", self.chk_resize.GetValue()))

        data.append(("offsetx", self.spin_offsetx.GetValue()))
        data.append(("offsety", self.spin_offsety.GetValue()))
        data.append(("width", self.spin_w.GetValue()))
        data.append(("height", self.spin_h.GetValue()))
        data.append(("x", self.spin_x.GetValue()))
        data.append(("y", self.spin_y.GetValue()))

        return str(data)

# if __name__ == "__main__":
    # app = wx.App()
    # frame = wx.Frame()
    # dialog = MouseClickRelative(frame)
    # app.Mainloop()