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

class OpenURL(wx.Dialog):

    def __init__(self, parent):

        wx.Dialog.__init__(self,
                           parent,
                           title="Open URL")

        # self._variables = variables
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)

        row = 0

        lbl = wx.StaticText(panel, label="Browser:")
        choices = ["system default"]
        browsers = ['mozilla',
                    'firefox',
                    'netscape',
                    'galeon',
                    'epiphany',
                    'skipstone',
                    'kfmclient',
                    'konqueror',
                    'kfm',
                    'mosaic',
                    'opera',
                    'grail',
                    'links',
                    'elinks',
                    'lynx',
                    'w3m',
                    'windows-default',
                    'macosx',
                    'safari',
                    'google-chrome',
                    'chrome',
                    'chromium',
                    'chromium-browser']
        choices.extend(sorted(browsers))
        self.cbox_browsers = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        self.cbox_browsers.SetSelection(0)

        grid.Add(lbl, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cbox_browsers, pos=(row,1), span=(0,3), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1

        lbl = wx.StaticText(panel, label="url:")
        self.text_url = wx.TextCtrl(panel)

        grid.Add(lbl, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.text_url, pos=(row,1), span=(0,3), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        self.chk_new_win = wx.CheckBox(panel, label="New Window")
        self.chk_autoraise = wx.CheckBox(panel, label="Autoraise")
        self.chk_autoraise.SetValue(1)
        grid.Add(self.chk_new_win, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.chk_autoraise, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

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

    def SetValue(self, data):
        browser = data["browser"]
        self.cbox_browsers.SetStringSelection(browser)

        url = data["url"]
        self.text_url.SetValue(url)

        newwindow = data["newwindow"]
        autoraise = data["autoraise"]
        self.chk_new_win.SetValue(newwindow)
        self.chk_autoraise.SetValue(autoraise)

    def GetValue(self):
        data = []
        data.append(("browser", self.cbox_browsers.GetValue()))
        data.append(("url", self.text_url.GetValue()))
        data.append(("autoraise", self.chk_new_win.GetValue()))
        data.append(("newwindow", self.chk_autoraise.GetValue()))

        return str(data)
