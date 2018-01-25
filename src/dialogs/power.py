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
import time
import wx
import base

class AddPower(wx.Dialog):

    def __init__(self, parent, title="Add Power Action"):
    
        wx.Dialog.__init__(self,
                           parent,
                           title=title)
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbox = wx.StaticBox(panel, label="")        
        sboxSizerWarn = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        warning = ("All other schedules will be stopped")
        lblWarn = wx.StaticText(panel, label=warning)
        sboxSizerWarn.Add(lblWarn, 0, flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        
        sbox = wx.StaticBox(panel, label="")        
        sboxSizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        grid = wx.GridBagSizer(5,5)
        row = 0
        lblFunction = wx.StaticText(panel, label="Power action:")
        choices = ["Shutdown",
                   "Shutdown (Force)", 
                   "Restart",
                   "Logoff"]
        self.cboxPower = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        self.cboxPower.SetSelection(0)
        grid.Add(lblFunction, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxPower, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lblQuick = wx.StaticText(panel, label="Quick Alert Set:")
        choices = ["10 Seconds", 
                   "20 Seconds", 
                   "30 Seconds", 
                   "1 Minute",
                   "2 Minutes", 
                   "3 Minutes",
                   "5 Minutes",
                   "10 Minutes"]
        self.cboxQuick = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        self.cboxQuick.Bind(wx.EVT_COMBOBOX, self.OnQuickSelect)
        grid.Add(lblQuick, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxQuick, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lblAlert = wx.StaticText(panel, label="Alert Duration (s):")
        self.spinAlert = wx.SpinCtrl(panel, min=10, max=10000, value="60")
        grid.Add(lblAlert, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.spinAlert, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableCol(1)
        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 5)
        
        self.chkPrimary = wx.CheckBox(panel, label="Show alert on primary display only")
        sboxSizer.Add(self.chkPrimary, 0, wx.ALL|wx.EXPAND, 5)
        
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btnCancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btnAdd = wx.Button(panel, label="Ok", id=wx.ID_OK)
        self.btnAdd.Bind(wx.EVT_BUTTON, self.OnButton)
        hsizer.Add(btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(self.btnAdd, 0, wx.ALL|wx.EXPAND, 5)
                        
        #add to main sizer
        sizer.Add(sboxSizerWarn, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)
        
        panel.SetSizer(sizer)  
        w, h = sizer.Fit(self)
        self.SetSize(w*1.5, h)
            
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if label == "Cancel":
            self.EndModal(id)            
        elif label == "Ok":            
            self.EndModal(id)

    def OnQuickSelect(self, event):
        e = event.GetEventObject()
        value = e.GetValue()
        
        if value.endswith(" Seconds"):
            value = value.strip(" Seconds")
        elif value.endswith(" Minutes"):
            value = int(value.strip(" Minutes")) * 60
            value = str(value)
        elif value == "1 Minute":
            value = "60"
        
        self.spinAlert.SetValue(value)
            
        
    def GetValue(self):
        data = []
