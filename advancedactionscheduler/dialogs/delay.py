# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler> 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. 
"""

import wx
import base
import wx.lib.agw.floatspin as floatspin

class AddDelay(wx.Dialog):

    def __init__(self, parent):

        wx.Dialog.__init__(self,
                           parent,
                           title="Add Delay")

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)

        row = 0
        self.spinDelay = floatspin.FloatSpin(panel, min_val=0, max_val=10000, digits=5, increment=0.1)
        self.labelDelay = wx.StaticText(panel, label="seconds")
        grid.Add(self.spinDelay, pos=(row,1), span=(2,2), flag=wx.ALL|wx.ALIGN_BOTTOM, border=5)
        grid.Add(self.labelDelay, pos=(row,3), span=(2,2), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)

        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 10)
        sboxSizer.AddSpacer(10)

        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btnCancel.Bind(wx.EVT_BUTTON, self.OnButton)
        btnConfirm = wx.Button(panel, label="Confirm", id=wx.ID_OK)
        btnConfirm.Bind(wx.EVT_BUTTON, self.OnButton)
        hsizer.Add(btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(btnConfirm, 0, wx.ALL|wx.EXPAND, 5)

        #add to main sizer
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)
        w, h = sizer.Fit(self)

        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        
        try:
            icon = wx.Icon("images/delay.png")
            self.SetIcon(icon)
        except Exception as e:
            print(e)

    def GetValue(self):
        data = [("delay", str(self.spinDelay.GetValue()))]
        data = str(data)
        return data
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "Cancel":
            self.EndModal(id)
        elif label == "Confirm":
            self.EndModal(id)
            
    def OnKeyUp(self, event):
        key = event.GetKeyCode()
        print(event)
        if key == wx.KEY_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        
    def SetValue(self, data):
        try:
            self.spinDelay.SetValue(float(data["delay"]))
        except Exception as e:
            print(e)