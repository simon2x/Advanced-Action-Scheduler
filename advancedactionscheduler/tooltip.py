#!/usr/bin/python3
# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler>
Released subject to the GNU Public License

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import wx


class ToolTip(wx.Frame):

    def __init__(self, parent):
        style = wx.SIMPLE_BORDER|wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR
        wx.Frame.__init__(self, parent=parent, style=style)

        self.panel = panel = wx.Panel(self)
        self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
        self._message = wx.StaticText(panel, label="")
        self._message.SetFont(self.font)

        sizer.Add(self._message, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        panel.SetSizerAndFit(sizer)
        self.Fit()
        self.Centre()
        w, h = self.GetSize()
        self.SetMinSize(self.GetSize())

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

        self.SetBackgroundColour("yellow")

    @property
    def font(self):
        return wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False)

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self.SetPosition(wx.GetMousePosition() + (25, 15))
        self._message.SetLabel(value)
        self.panel.Fit()
        self.Fit()
        self.Show()
        # self.Raise()
        self.trans = 70
        self.coolDown = False
        self.SetTransparent(self.trans)
        self.timer.Start(100)

    def OnLeftUp(self, event):
        self.Hide()
        self.timer.Stop()

    def OnTimer(self, event):
        if self.coolDown is True:
            self.trans -= 5
            if self.trans == 50:
                self.Hide()
                self.timer.Stop()
        else:
            self.trans += 10
        self.SetTransparent(self.trans)

        if self.trans == 250 and self.coolDown is False:
            self.coolDown = True
