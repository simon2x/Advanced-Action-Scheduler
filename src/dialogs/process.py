# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler> 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. 
"""

import base
import logging
import platform
import wx
    
class NewProcess(wx.Dialog):

    def __init__(self, parent, title="New Process"):

        wx.Dialog.__init__(self, parent, title=title)
        
        self.parent = parent
        self.resetValue = None
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)

        row = 0
        self.historyList = base.BaseList(panel)
        self.historyList.SetSingleStyle(wx.LC_EDIT_LABELS)
        self.historyList.SetSingleStyle(wx.LC_SINGLE_SEL, add=False)
        self.historyList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnHistoryListItemSelection)
        self.historyList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnHistoryListItemActivated)
        self.historyList.InsertColumn(0, "Command Presets")
        grid.Add(self.historyList, pos=(row,0), span=(2,5), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableRow(row)
        
        row += 2
        hSizerBtns = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["add","up","down","edit","delete"]:
            img = wx.Image("icons/{0}.png".format(label.lower().replace(" ", "")))
            img = img.Rescale(32,32, wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img)
            btn = wx.Button(panel, label=label, name=label, style=wx.BU_EXACTFIT|wx.BU_NOTEXT)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            btn.SetBitmap(bmp)
            hSizerBtns.Add(btn, 0, wx.ALL|wx.EXPAND, 5)
        grid.Add(hSizerBtns, pos=(row,0), span=(0,3), flag=wx.ALL|wx.EXPAND, border=5)   
        
        btnSet = wx.Button(panel, label="Set")
        btnSet.Bind(wx.EVT_BUTTON, self.OnButton)
        grid.Add(btnSet, pos=(row,4), flag=wx.ALL|wx.EXPAND, border=5)   
        
        row += 1
        lblCmd = wx.StaticText(panel, label="Command:")
        self.cboxCmd = wx.TextCtrl(panel)
        btnAdd = wx.Button(panel, label="Add To Preset")
        btnAdd.Bind(wx.EVT_BUTTON, self.OnButton)
        btnReset = wx.Button(panel, label="Reset")
        btnReset.Bind(wx.EVT_BUTTON, self.OnButton)
        btnClear = wx.Button(panel, label="Clear")
        btnClear.Bind(wx.EVT_BUTTON, self.OnButton)
        
        grid.Add(lblCmd, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxCmd, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnAdd, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnReset, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnClear, pos=(row,4), flag=wx.ALL, border=5)
        
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
        sizer.Add(sboxSizer, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 2)

        panel.SetSizer(sizer)

        w, h = sizer.Fit(self)
        self.SetMinSize((w*2, h*1.5))
        self.SetSize((w*2, h*1.5))
        
    def GetHistoryList(self):
        idx = 0
        items = []
        for x in range(self.historyList.GetItemCount()):
            items.append(self.historyList.GetItemText(x))
        return items    
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "add":
            item = self.historyList.Append([""])
            self.historyList.Select(item)
            self.historyList.EditLabel(item)
        elif label == "Add To Preset":
            self.historyList.Append([self.cboxCmd.GetValue()])       
        elif label == "Cancel":
            data = {"newProcessPresets":self.GetHistoryList()}
            self.parent.UpdateSettingsDict(data)
            self.EndModal(id)
        elif label == "Clear":
            value = self.cboxCmd.SetValue("")    
        elif label == "delete":
            self.historyList.DeleteSelected()
        elif label == "down":
            self.historyList.MoveSelectedItemsDown()
        elif label == "edit":
            self.OnHistoryListItemActivated()
        elif label == "Ok":
            data = {"newProcessPresets": self.GetHistoryList()}
            self.parent.UpdateSettingsDict(data)
            self.EndModal(id)
        elif label == "Reset":
            if self.resetValue:
                self.SetValue(self.resetValue)
        elif label == "Set":
            self.SetCommandFromList()
        elif label == "up":
            self.historyList.MoveSelectedItemsUp()
            
    def GetValue(self):
        data = []
        data.append(("cmd", self.cboxCmd.GetValue()))
        return str(data)
        
    def OnHistoryListItemActivated(self, event=None):
        selected = self.historyList.GetFirstSelected()
        if selected == -1:
            return
        self.historyList.EditLabel(selected)
        
    def OnHistoryListItemSelection(self, event):
        print(self.historyList.GetFirstSelected())

    def SetCommandFromList(self):
        selected = self.historyList.GetFirstSelected()
        if selected == -1:
            return
        self.cboxCmd.SetValue(self.historyList.GetItemText(selected))
        
    def SetHistoryList(self, history):
        for h in reversed(history):
            self.historyList.InsertItem(0, h)
        
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