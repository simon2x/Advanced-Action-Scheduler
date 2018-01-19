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
import sys
import wx

class OpenURL(wx.Dialog):

    def __init__(self, parent):

        wx.Dialog.__init__(self,
                           parent,
                           title="Open URL")

        self.resetValue = None                   
        self.parent = parent
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)

        row = 0
        self.urlPresetList = base.BaseList(panel)
        self.urlPresetList.SetSingleStyle(wx.LC_EDIT_LABELS)
        self.urlPresetList.SetSingleStyle(wx.LC_SINGLE_SEL, add=False)
        self.urlPresetList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnUrlPresetListItemSelection)
        self.urlPresetList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnUrlPresetListItemActivated)
        self.urlPresetList.InsertColumn(0, "URL Presets")
        grid.Add(self.urlPresetList, pos=(row,0), span=(2,5), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableRow(0)
        
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
        lbl = wx.StaticText(panel, label="Browser:")
        choices = ["system default"]
        browsers = ['mozilla',
                    'firefox',
                    'epiphany',
                    'konqueror',
                    'opera',
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
        self.cboxBrowsers = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        self.cboxBrowsers.SetSelection(0)
        self.chkNewWin = wx.CheckBox(panel, label="New Window")
        self.chkAutoraise = wx.CheckBox(panel, label="Autoraise")
        self.chkAutoraise.SetValue(1)
        grid.Add(lbl, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxBrowsers, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.chkNewWin, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.chkAutoraise, pos=(row,4), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lblCmd = wx.StaticText(panel, label="URL:")
        self.textUrl = wx.TextCtrl(panel)
        btnAdd = wx.Button(panel, label="Add To Preset")
        btnAdd.Bind(wx.EVT_BUTTON, self.OnButton)
        btnReset = wx.Button(panel, label="Reset")
        btnReset.Bind(wx.EVT_BUTTON, self.OnButton)
        btnClear = wx.Button(panel, label="Clear")
        btnClear.Bind(wx.EVT_BUTTON, self.OnButton)
        
        grid.Add(lblCmd, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.textUrl, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnAdd, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnReset, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnClear, pos=(row,4), flag=wx.ALL, border=5)
        
        grid.AddGrowableCol(1)

        sboxSizer.AddSpacer(10)
        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 2)
        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btnCancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btnAdd = wx.Button(panel, label="Ok", id=wx.ID_OK)
        self.btnAdd.Bind(wx.EVT_BUTTON, self.OnButton)
        # self.btnAdd.Disable()
        hsizer.Add(btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(self.btnAdd, 0, wx.ALL|wx.EXPAND, 5)

        #add to main sizer
        sizer.Add(sboxSizer, 1, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 2)

        panel.SetSizer(sizer)

        w, h = sizer.Fit(self)
        self.SetMinSize((w*2, h*1.5))
        self.SetSize((w*2, h*1.5))
        
    def GetUrlPresetList(self):
        idx = 0
        items = []
        for x in range(self.urlPresetList.GetItemCount()):
            items.append(self.urlPresetList.GetItemText(x))
        return items    
        
    def GetValue(self):
        data = []
        data.append(("browser", self.cboxBrowsers.GetValue()))
        data.append(("url", self.textUrl.GetValue()))
        data.append(("autoraise", self.chkNewWin.GetValue()))
        data.append(("newwindow", self.chkAutoraise.GetValue()))

        return str(data)

    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "add":
            item = self.urlPresetList.Append([""])
            self.urlPresetList.Select(item)
            self.urlPresetList.EditLabel(item)
        elif label == "Add To Preset":
            self.urlPresetList.Append([self.textUrl.GetValue()])       
        elif label == "Cancel":
            data = {"openUrlPresets":self.GetUrlPresetList()}
            self.parent.UpdateSettingsDict(data)
            self.EndModal(id)
        elif label == "Clear":
            value = self.textUrl.SetValue("")    
        elif label == "delete":
            self.urlPresetList.DeleteSelected()
        elif label == "down":
            self.urlPresetList.MoveSelectedItemsDown()
        elif label == "edit":
            self.OnUrlPresetListItemActivated()
        elif label == "Ok":
            data = {"openUrlPresets": self.GetUrlPresetList()}
            self.parent.UpdateSettingsDict(data)
            self.EndModal(id)
        elif label == "Reset":
            if self.resetValue:
                self.SetValue(self.resetValue)
        elif label == "Set":
            self.SetCommandFromList()
        elif label == "up":
            self.urlPresetList.MoveSelectedItemsUp()
    
    def OnUrlPresetListItemActivated(self, event=None):
        selected = self.urlPresetList.GetFirstSelected()
        if selected == -1:
            return
        self.urlPresetList.EditLabel(selected)
        
    def OnUrlPresetListItemSelection(self, event):
        print(self.urlPresetList.GetFirstSelected())

    def SetCommandFromList(self):
        selected = self.urlPresetList.GetFirstSelected()
        if selected == -1:
            return
        self.textUrl.SetValue(self.urlPresetList.GetItemText(selected))
        
    def SetUrlPresetList(self, history):
        for h in reversed(history):
            self.urlPresetList.InsertItem(0, h)
        
    def SetValue(self, data):
        
        if not self.resetValue:
            self.resetValue = data 
            
        for arg, func, default in (
            ["browser", self.cboxBrowsers.SetValue, ""],
            ["url", self.textUrl.SetValue, ""],
            ["newwindow", self.chkNewWin.SetValue, ""],
            ["autoraise", self.chkAutoraise.SetValue, ""],
            ):
            
            try:
                func(data[arg])
            except Exception as e:
                print(e)
                func(default)
                
#               