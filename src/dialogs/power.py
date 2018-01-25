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
        data.append(("action", self.cboxPower.GetValue()))
        data.append(("alert", self.spinAlert.GetValue()))
        data.append(("primary", self.chkPrimary.GetValue()))
        return str(data)
        
    def SetValue(self, data):
        for arg, func, default in (
            ["action", self.cboxPower.SetValue, "Shutdown"],
            ["alert", self.spinAlert.SetValue, "60"],
            ["primary", self.chkPrimary.SetValue, False],
            ):
            
            try:
                func(data[arg])
            except Exception as e:
                print(e)
                func(default)
        
class PowerAlertDialog(wx.Frame):  
    
    def __init__(self):                    
        wx.Frame.__init__(self,
                          parent=None,
                          style=wx.SIMPLE_BORDER|wx.STAY_ON_TOP)        
        
        self.actionMsg = {
            "Shutdown": ("Shutting Down", wx.SHUTDOWN_POWEROFF),
            "Shutdown (force)": ("(Force) Shutting Down", wx.SHUTDOWN_FORCE),
            "Restart": ("Restarting", wx.SHUTDOWN_REBOOT),
            "Logoff": ("Logging Off", wx.SHUTDOWN_LOGOFF),
        }        
        
        self.SetTitle("Advanced Action Scheduler: Power")
        self.panel = panel = wx.Panel(self)    
        self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
        self.message = wx.StaticText(panel, label="")
        font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, True)
        self.message.SetFont(font)
        button = wx.Button(panel, wx.ID_CANCEL, label="Cancel")
        button.Bind(wx.EVT_BUTTON, self.OnHide)
        sizer.Add(self.message, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        sizer.Add(button, 0, wx.ALL|wx.EXPAND, 5)
        panel.SetSizerAndFit(sizer)
        self.Fit()
        self.Centre()
        w, h = self.GetSize()
        self.SetMinSize(self.GetSize())
        
        self.Raise()
        self.Show()
        self.Center()
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        
    def OnHide(self, event):
        self.Hide()
        
    def OnTimer(self, event):
        self.timeout -= 1
        message = "{0}: {1} seconds".format(self.actionMsg[self.action][0], self.timeout)
        self.message.SetLabel(message)
        if self.timeout == 0:
            wx.Shutdown(flags=self.flags)
            self.Hide()
            
        self.panel.Fit()
        self.Fit()
        self.CentreInRect()
        
    def CentreInRect(self):
        w, h = self.GetSize()
        x, y = int(self.center_x-(w/2)), int(self.center_y-(h/2))        
        if self.GetPosition() != (x, y):
            self.SetPosition((x, y))
        
    def SetContainingRect(self, rect):
        x1, y1, x2, y2 = rect
        self.center_x, self.center_y = x1 + (x2/2), y1 + (y2/2)
    
    def SetValue(self, kwargs):
        try:
            self.timeout = int(kwargs["alert"])
            if self.timeout < 10:
                self.timeout = 60
        except:
            self.timeout = 60
         
        self.action = kwargs["action"]
        self.flags = self.actionMsg[self.action][1]
        
        self.timer.Start(1000)
        
#