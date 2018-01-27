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
    
class AddControl(wx.Dialog):

    def __init__(self, parent, title="Add Control Action"):
    
        wx.Dialog.__init__(self, parent, title=title)
        
        panel = wx.Panel(self) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbox = wx.StaticBox(panel, label="")        
        sboxSizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        grid = wx.GridBagSizer(5,5)
        row = 0
        lblFunction = wx.StaticText(panel, label="Control action:")
        choices = ["END",
                   "Disable Schedule Manager"]
        self.cboxControl = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        self.cboxControl.SetSelection(0)
        grid.Add(lblFunction, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxControl, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 5)
        
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
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)
        
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
        
    def GetValue(self):
        data = []
        data.append(("action", self.cboxControl.GetValue()))
        return str(data)
        
    def SetValue(self, data):
        for arg, func, default in (
            ["action", self.cboxControl.SetValue, "Return"],
            ):
            
            try:
                func(data[arg])
            except Exception as e:
                print(e)
                func(default)
        
#