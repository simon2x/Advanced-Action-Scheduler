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
import platform
import sys
import wx
import windowmanager

PLATFORM = platform.system()
if PLATFORM == "Windows":
    from windowmanager import windows as winman
elif PLATFORM == "Linux":
    from windowmanager import linux as winman
    
class WindowDialog(wx.Dialog):

    def __init__(self, parent, title=""):

        wx.Dialog.__init__(self,
                           parent,
                           title=title)

        # self._variables = variables
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)

        row = 0

        lbl_function = wx.StaticText(panel, label="Window:")
        choices = []
        choices.extend(winman.GetWindowList())
        self.cbox_window = wx.ComboBox(panel, choices=choices)
        btn_refresh = wx.Button(panel, label="Refresh")
        btn_refresh.Bind(wx.EVT_BUTTON, self.OnButton)

        grid.Add(lbl_function, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cbox_window, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btn_refresh, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        self.chk_match_case = wx.CheckBox(panel, label="Match Case")
        self.chk_match_string = wx.CheckBox(panel, label="Match Whole String")
        self.chk_match_case.SetValue(True)
        self.chk_match_string.SetValue(True)
        grid.Add(self.chk_match_case, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.chk_match_string, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

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

        if label == "Cancel":
            self.EndModal(id)
        elif label == "Ok":
            self.EndModal(id)
        elif label == "Refresh":
            value = self.cbox_window.GetValue()
            self.cbox_window.Clear()
            choices = []
            choices.extend(winman.GetWindowList())
            self.cbox_window.Append(choices)
            self.cbox_window.SetValue(value)

    def SetValue(self, data):
        window = data["window"]
        self.cbox_window.SetValue(window)

        case = data["matchcase"]
        string = data["matchstring"]
        self.chk_match_case.SetValue(case)
        self.chk_match_string.SetValue(string)

    def GetValue(self):
        data = []
        data.append(("window", self.cbox_window.GetValue()))
        data.append(("matchcase", self.chk_match_case.GetValue()))
        data.append(("matchstring", self.chk_match_string.GetValue()))

        return str(data)
