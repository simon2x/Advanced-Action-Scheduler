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
import os
from wx.lib.agw import hyperlink
from version import __version__


__title__ = "Advanced Action Scheduler"


class AboutDialog(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent,
                          style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_NO_TASKBAR|wx.STAY_ON_TOP,
                          title=__title__)

        self.SetIcon(wx.Icon("icons/icon.png"))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox1 = wx.StaticBox(panel, label="")
        sboxSizer1 = wx.StaticBoxSizer(sbox1, wx.HORIZONTAL)
        grid = wx.GridSizer(cols=2)
        grid.Add(wx.StaticText(panel, label="Homepage:"), 0, wx.ALL, 5)
        g = "https://gitlab.com/swprojects/Advanced-Action-Scheduler"
        link = hyperlink.HyperLinkCtrl(panel, label=g, URL=g)
        grid.Add(link, 1, wx.ALL|wx.EXPAND, 5)
        grid.Add(wx.StaticText(panel, label="Version:"), 0, wx.ALL, 5)
        version = "v" + __version__
        grid.Add(wx.StaticText(panel, label=version), 0, wx.ALL, 5)

        sboxSizer1.Add(grid, 1, wx.ALL|wx.EXPAND, 5)

        sbox2 = wx.StaticBox(panel, label="License")
        sboxSizer2 = wx.StaticBoxSizer(sbox2, wx.VERTICAL)

        style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_CENTRE
        licenseText = wx.TextCtrl(panel, style=style)
        cwd = os.getcwd()
        lpath = os.path.join(cwd, "LICENSE")
        with open(lpath) as file:
            for line in file:
                licenseText.AppendText(line)
        sboxSizer2.Add(licenseText, 1, wx.ALL|wx.EXPAND, 5)

        sizer.Add(sboxSizer1, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sboxSizer2, 1, wx.ALL|wx.EXPAND, 5)

        panel.SetSizerAndFit(sizer)
        self.Fit()
        self.Centre()
        w, h = self.GetSize()
        self.SetSize(w, h * 2)
        self.SetMinSize(self.GetSize())
        self.SetMaxSize(self.GetSize())

        self.Raise()
        self.Show()

        self.Bind(wx.EVT_CHAR_HOOK, self.OnChar)

    def OnChar(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Destroy()
