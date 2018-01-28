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
import sys
import wx
import wx.lib.agw.floatspin as floatspin

PLATFORM = platform.system()
if PLATFORM == "Windows":
    from win import windowmanager as winman
elif PLATFORM == "Linux":
    from linux import windowmanager as winman
    
class WindowDialog(wx.Dialog):

    def __init__(self, parent, title=""):

        wx.Dialog.__init__(self,
                           parent,
                           title=title)

        # self._variables = variables
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5,5)

        row = 0

        lblFunction = wx.StaticText(panel, label="Window:")
        choices = []
        choices.extend(winman.GetWindowList())
        self.cboxWindow = wx.ComboBox(panel, choices=choices)
        btnRefresh = wx.Button(panel, label="Refresh")
        btnRefresh.Bind(wx.EVT_BUTTON, self.OnButton)

        grid.Add(lblFunction, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxWindow, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnRefresh, pos=(row,3), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lblMatch = wx.StaticText(panel, label="Condition:")
        choices = ["Match Both Window Class And Title",
                   "Match Window Class Only",
                   "Match Window Title Only"]
        self.cboxMatch = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        self.cboxMatch.SetSelection(0)
        grid.Add(lblMatch, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxMatch, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        cboxMatchesLabel = wx.StaticText(panel, label="Matches:")
        self.cboxMatches = floatspin.FloatSpin(panel, min_val=0)
        self.cboxMatches.SetDigits(0)
        if title in ["If Window Open", "If Window Not Open"]:
            self.cboxMatches.SetValue(1)
            self.cboxMatches.Disable()
        cboxMatchesLabel2 = wx.StaticText(panel, label="If 0: Execute Action On All Matches")
        grid.Add(cboxMatchesLabel, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxMatches, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(cboxMatchesLabel2, pos=(row,2), flag=wx.ALL|wx.ALIGN_CENTRE|wx.ALIGN_LEFT, border=5)
        
        row += 1
        self.chkMatchTitleCase = wx.CheckBox(panel, label="Match Case (Title)")
        self.chkMatchTitle = wx.CheckBox(panel, label="Match Whole Title")
        self.chkMatchTitleCase.SetValue(True)
        self.chkMatchTitle.SetValue(True)
        grid.Add(self.chkMatchTitleCase, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.chkMatchTitle, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        grid.AddGrowableCol(1)

        sboxSizer.AddSpacer(10)
        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 2)
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
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 2)

        panel.SetSizer(sizer)

        w, h = sizer.Fit(self)
        
        try:
            icon = wx.Icon("images/ifwindowopen.png")
            self.SetIcon(icon)
        except Exception as e:
            print(e)

    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "Cancel":
            self.EndModal(id)
        elif label == "Ok":
            self.EndModal(id)
        elif label == "Refresh":
            value = self.cboxWindow.GetValue()
            self.cboxWindow.Clear()
            choices = []
            choices.extend(winman.GetWindowList())
            self.cboxWindow.Append(choices)
            self.cboxWindow.SetValue(value)

    def SetValue(self, data):        
        for arg, func, default in (
            ["window", self.cboxWindow.SetValue, ""],
            ["matchcondition", self.cboxMatch.SetSelection, True],
            ["matchcase", self.chkMatchTitleCase.SetValue, True],
            ["matchstring", self.chkMatchTitle.SetValue, True],
            ["matches", self.cboxMatches.SetValue, 0]):
            
            try:
                func(data[arg])
            except Exception as e:
                print(e)
                func(default)
        
    def GetValue(self):
        data = []
        data.append(("window", self.cboxWindow.GetValue()))
        data.append(("matchcondition", self.cboxMatch.GetSelection()))
        data.append(("matchcase", self.chkMatchTitleCase.GetValue()))
        data.append(("matchstring", self.chkMatchTitle.GetValue()))
        data.append(("matches", self.cboxMatches.GetValue()))
        
        return str(data)
