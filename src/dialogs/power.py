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
        
        # self._variables = variables
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbox = wx.StaticBox(panel, label="")        
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)
        
        row = 0
        
        lbl_function = wx.StaticText(panel, label="Power action:")
        choices = ["Shutdown",
                   "Shutdown (Force)", 
                   "Restart", 
                   "Standby",
                   "Hibernate",
                   "Logoff"]
        self.cbox_power = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        self.cbox_power.SetSelection(0)
        
        grid.Add(lbl_function, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cbox_power, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        
        lbl_alert = wx.StaticText(panel, label="Alert Duration (s):")
        choices = [str(x) for x in range(15,120,15)]
        self.cbox_alert = wx.ComboBox(panel, choices=choices)
        self.cbox_alert.SetSelection(0)
        
        grid.Add(lbl_alert, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cbox_alert, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        
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
        
        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass
            
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if label == "Cancel":
            self.EndModal(id)            
        elif label == "Ok":            
            self.EndModal(id)

    def GetValue(self, data):
        value = {}
    
    def SetValue(self, data):
        name = data["action"]
        self.cbox_power.SetValue(name)
        alert = data["alert"]
        self.cbox_alert.SetValue(alert)
        
    def GetValue(self):        
        data = []
        data.append(("action", self.cbox_power.GetValue()))
        try:
            #check whether value is integer as well as nonzero value
            if int(self.cbox_power.GetValue()) == 0:
                value = "15"
            else:
                value = self.cbox_power.GetValue()
            alert = ("alert", value)
        except:
            alert = ("alert", "15")
        data.append(alert)
        
        data = str(data)
                
        return data