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
import advwebbrowser
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
        sboxSizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        
        gridListBoxes = wx.GridBagSizer(2,1)
        sboxSizer.Add(gridListBoxes, 1, wx.ALL|wx.EXPAND, 5)
        row = 0
        for n, name in enumerate(["browser","url"]):
            hSizerBtns = wx.BoxSizer(wx.HORIZONTAL)
            labels = ["add","up","down","edit","delete"]
            if name == "browser":
                labels.append("open")
            for label in labels:
                img = wx.Image("icons/{0}.png".format(label.lower().replace(" ", "")))
                img = img.Rescale(32,32, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
                btn = wx.Button(panel, label=label, name=name, style=wx.BU_EXACTFIT|wx.BU_NOTEXT)
                btn.Bind(wx.EVT_BUTTON, self.OnButton)
                btn.SetBitmap(bmp)
                hSizerBtns.Add(btn, 0, wx.ALL|wx.EXPAND, 5)
            gridListBoxes.Add(hSizerBtns, pos=(row,n), flag=wx.ALL|wx.EXPAND, border=5)   
        
        row += 1
        self.browserList = base.BaseList(panel)
        self.browserList.SetSingleStyle(wx.LC_EDIT_LABELS)
        self.browserList.SetSingleStyle(wx.LC_SINGLE_SEL, add=False)
        self.browserList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivated)
        self.browserList.InsertColumn(0, "Browsers")
        gridListBoxes.Add(self.browserList, pos=(row,0), flag=wx.ALL|wx.EXPAND, border=5)
        
        self.urlPresetList = base.BaseList(panel)
        self.urlPresetList.SetSingleStyle(wx.LC_EDIT_LABELS)
        self.urlPresetList.SetSingleStyle(wx.LC_SINGLE_SEL, add=False)
        self.urlPresetList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivated)
        self.urlPresetList.InsertColumn(0, "URLs")
        gridListBoxes.Add(self.urlPresetList, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        gridListBoxes.AddGrowableRow(1)
        gridListBoxes.AddGrowableCol(0)
        gridListBoxes.AddGrowableCol(1)
        
        row += 1
        for n, label in enumerate(["Set Browser Path", "Set URL Path"]):
            btn = wx.Button(panel, label=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            gridListBoxes.Add(btn, pos=(row,n), flag=wx.ALL|wx.ALIGN_RIGHT, border=5)  
        
        grid = wx.GridBagSizer(5,5)
        row = 0
        lbl = wx.StaticText(panel, label="Browser Path:")
        self.textBrowser = wx.TextCtrl(panel)
        btnAdd = wx.Button(panel, label="Add To Browsers")
        btnAdd.Bind(wx.EVT_BUTTON, self.OnButton)
        self.chkNewWin = wx.CheckBox(panel, label="New Window")
        self.chkAutoraise = wx.CheckBox(panel, label="Autoraise")
        self.chkAutoraise.SetValue(1)
        grid.Add(lbl, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.textBrowser, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnAdd, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.chkNewWin, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.chkAutoraise, pos=(row,4), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lbl = wx.StaticText(panel, label="Browser Type:")
        browsers = [b for b in advwebbrowser.klasses.keys()]
        self.cboxBrowserClass = wx.ComboBox(panel, choices=browsers, style=wx.CB_READONLY)
        grid.Add(lbl, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxBrowserClass, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lblCmd = wx.StaticText(panel, label="URL:")
        self.textUrl = wx.TextCtrl(panel)
        btnAdd = wx.Button(panel, label="Add To URL")
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
        sboxSizer.Add(grid, 0, wx.ALL|wx.EXPAND, 2)
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
        sizer.Add(sboxSizer, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)

        w, h = sizer.Fit(self)
        self.SetMinSize((w*2, h*1.5))
        self.SetSize((w*2, h*1.5))
        
    def FindBrowserDialog(self):
        dlg = wx.FileDialog(self, 
                            defaultDir="",
                            message="Find Browser",
                            style=wx.FD_DEFAULT_STYLE|wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
            
        path = dlg.GetPath()
        self.browserList.Append([path])
        
    def GetBrowserPresets(self):
        idx = 0
        items = []
        for x in range(self.browserList.GetItemCount()):
            items.append(self.browserList.GetItemText(x))
        return items   
        
    def GetUrlPresets(self):
        idx = 0
        items = []
        for x in range(self.urlPresetList.GetItemCount()):
            items.append(self.urlPresetList.GetItemText(x))
        return items   
        
    def GetValue(self):
        data = []
        data.append(("browser", self.textBrowser.GetValue()))
        data.append(("browserclass", self.cboxBrowserClass.GetValue()))
        data.append(("url", self.textUrl.GetValue()))
        data.append(("autoraise", self.chkNewWin.GetValue()))
        data.append(("newwindow", self.chkAutoraise.GetValue()))

        return str(data)

    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()
        
        if e.GetName() == "browser":
            lc = self.browserList
        elif e.GetName() == "url":
            lc = self.urlPresetList
            
        if label == "add":
            item = lc.Append([""])
            lc.Select(item)
            lc.EditLabel(item)
        elif label == "Add To Browsers":
            self.browserList.Append([self.textBrowser.GetValue()])   
        elif label == "Add To URL":
            self.urlPresetList.Append([self.textUrl.GetValue()])
        elif label == "Cancel":
            self.SavePresets()
            self.EndModal(id)
        elif label == "Clear":
            self.textUrl.SetValue("")
        elif label == "delete":
            lc.DeleteSelected()
        elif label == "down":
            lc.MoveSelectedItemsDown()
        elif label == "edit":
            self.OnListItemActivated(lc)
        elif label == "Ok":
            self.SavePresets()
            self.EndModal(id)
        elif label == "open":
            self.FindBrowserDialog()
        elif label == "Reset":
            if self.resetValue:
                self.SetValue(self.resetValue)
        elif label == "Set Browser Path":
            selected = self.browserList.GetFirstSelected()
            if selected == -1:
                return
            self.textBrowser.SetValue(self.browserList.GetItemText(selected))
        elif label == "Set URL Path":
            selected = self.urlPresetList.GetFirstSelected()
            if selected == -1:
                return
            self.textUrl.SetValue(self.urlPresetList.GetItemText(selected))
        elif label == "up":
            lc.MoveSelectedItemsUp()
    
    def OnListItemActivated(self, event=None):
        try:
            e = event.GetEventObject()
        except:
            e = event 
        selected = e.GetFirstSelected()
        if selected == -1:
            return
        e.EditLabel(selected)
        
    def SavePresets(self):
        data = {"openUrlPresets": self.GetUrlPresets(),
                "browserPresets": self.GetBrowserPresets()}
        self.parent.UpdateSettingsDict(data)
        
    def SetCommandFromList(self):
        selected = self.urlPresetList.GetFirstSelected()
        if selected == -1:
            return
        self.textUrl.SetValue(self.urlPresetList.GetItemText(selected))
        
    def SetBrowserPresets(self, browsers):
        for b in reversed(browsers):
            self.browserList.InsertItem(0, b)
            
    def SetUrlPresets(self, presets):
        for p in reversed(presets):
            self.urlPresetList.InsertItem(0, p)
        
    def SetValue(self, data):
        
        if not self.resetValue:
            self.resetValue = data 
            
        for arg, func, default in (
            ["browser", self.textBrowser.SetValue, ""],
            ["browserclass", self.cboxBrowserClass.SetValue, "Generic"],
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