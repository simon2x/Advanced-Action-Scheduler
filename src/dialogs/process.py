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
import wx
    
class NewProcess(wx.Dialog):

    def __init__(self, parent, title="New Process"):

        wx.Dialog.__init__(self, parent, title=title)
        
        self.resetValue = None
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)

        row = 0
        lblCmd = wx.StaticText(panel, label="Command:")
        self.cboxCmd = wx.ComboBox(panel)
        btnReset = wx.Button(panel, label="Reset")
        btnReset.Bind(wx.EVT_BUTTON, self.OnButton)

        grid.Add(lblCmd, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxCmd, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnReset, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        btnClear = wx.Button(panel, label="Clear")
        btnClear.Bind(wx.EVT_BUTTON, self.OnButton)
        grid.Add(btnClear, pos=(row,3), flag=wx.ALL, border=5)
        
        grid.AddGrowableCol(1)

        sboxSizer.AddSpacer(10)
        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 5)
        
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btnCancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btnOk = wx.Button(panel, label="Ok", id=wx.ID_OK)
        self.btnOk.Bind(wx.EVT_BUTTON, self.OnButton)
        
        hsizer.Add(btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(self.btnOk, 0, wx.ALL|wx.EXPAND, 5)

        #add to main sizer
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 2)

        panel.SetSizer(sizer)

        w, h = sizer.Fit(self)
        self.SetMinSize((w*2, h))
        self.SetSize((w*2, h))
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "Cancel":
            self.EndModal(id)
        elif label == "Clear":
            value = self.cboxCmd.SetValue("")    
        elif label == "Ok":
            self.EndModal(id)
        elif label == "Reset":
            if self.resetValue:
                self.SetValue(self.resetValue)
                self.SetFocus(self.cboxCmd)

    def GetValue(self):
        data = []
        data.append(("cmd", self.cboxCmd.GetValue()))
        return str(data)
        
    def SetValue(self, data):
        
        if not self.resetValue:
            self.resetValue = data 
            
        for arg, func, default in (
            ["cmd", self.cboxCmd.SetValue, ""],
            ):
            
            try:
                func(data[arg])
            except Exception as e:
                print(e)
                func(default)
        
        if self.cboxCmd.IsListEmpty():
            return