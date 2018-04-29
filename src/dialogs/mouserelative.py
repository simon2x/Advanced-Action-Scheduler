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
from ast import literal_eval as make_tuple

PLATFORM = platform.system()
if PLATFORM == "Windows":
    from win import windowmanager as winman
elif PLATFORM == "Linux":
    from linux import windowmanager as winman
    
class FindPosition(wx.Frame):

    def __init__(self, parent):

        wx.Frame.__init__(self,
                          parent=None,
                          style=wx.NO_BORDER)
        
        self.SetTitle("Relative Position Finder")
        self.relativePos = None                 
        self.bounds = None
        # self.SetSize((25, 25))
        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._position = wx.StaticText(panel, label="(0,0)", )
        sizer.Add(self._position, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTRE)

        panel.SetSizer(sizer)

        self._position.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

        panel.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        panel.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        panel.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        # panel.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

        self.SetMinSize((90, 60))
        self.SetSize((90, 60))

        # this is important, otherwise the captionless dialog is always maximised
        self.SetMaxSize((90, 60))

        self.Move(wx.GetMousePosition()-(45, 30))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        
        self._position.SetForegroundColour("white")
        self.SetBackgroundColour("blue")

    def GetValue(self):
        print(self.relativePos)
        return self.relativePos
    
    def OnLeftUp(self, event):
        self.Close()
    
    def OnKeyUp(self, event):
        key = event.GetKeyCode()
        print(key)
        if key == wx.WXK_ESCAPE:
            self.Close()
        if key == wx.WXK_RETURN:
            self.Close()

    def OnRightUp(self, event):
        self.Destroy()
        
    def OnTimer(self, event):
        self.Raise()
        
        x1, y1, w, h = self.bounds
        # check if in bounds        
        x, y = wx.GetMousePosition()        
        if x in range(x1, x1+w) and y in range(y1, y1+h):
            relX = round((x - x1)/w * 100, 2)
            relY = round((y - y1)/h * 100, 2)
            self.relativePos = relX, relY
        else:
            relX = "n/a"
            relY = "n/a"            
            
        self.Move(wx.GetMousePosition()-(45, 30))

        text = "{0}, {1}".format(relX, relY)
        self._position.SetLabel(text)

    def SetBounds(self, x1, y1, w, h):
        self.bounds = [x1, y1, w, h]
        # we start timer once bounds have been set
        self.timer.Start(1)
        
class MouseClickRelative(wx.Dialog):

    def __init__(self, parent):

        wx.Dialog.__init__(self,
                           parent,
                           title="Mouse Click Relative")

        self.resetValue = None 
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        grid = wx.GridBagSizer(5,5)

        row = 0

        lblFunction = wx.StaticText(panel, label="Window:")
        choices = []
        choices.extend(winman.GetWindowList())
        self.cboxWindow = wx.ComboBox(panel, choices=choices)
        btnRefresh = wx.Button(panel, label="Refresh")
        btnRefresh.Bind(wx.EVT_BUTTON, self.OnButton)

        grid.Add(lblFunction, pos=(row,0), flag=wx.ALL|wx.EXPAND|wx.ALIGN_BOTTOM, border=5)
        grid.Add(self.cboxWindow, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(btnRefresh, pos=(row,3), flag=wx.ALL|wx.EXPAND)

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
        
        row += 1
        self.chkResize = wx.CheckBox(panel, label="Resize Window")
        self.chkResize.SetValue(True)
        grid.Add(self.chkResize, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lblOffsetX = wx.StaticText(panel, label="Offset (x):")
        self.spinOffsetX = wx.SpinCtrl(panel, min=-10000, max=10000)
        grid.Add(lblOffsetX, pos=(row,1), flag=wx.ALL|wx.EXPAND|wx.ALIGN_BOTTOM, border=5)
        grid.Add(self.spinOffsetX, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lblOffsetY = wx.StaticText(panel, label="Offset (y):")
        self.spinOffsetY = wx.SpinCtrl(panel, min=-10000, max=10000)
        grid.Add(lblOffsetY, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinOffsetY, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lblOffsetX = wx.StaticText(panel, label="Width (w):")
        self.spinW = wx.SpinCtrl(panel, min=0, max=10000)
        grid.Add(lblOffsetX, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinW, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)
        
        row += 1
        lblOffsetY = wx.StaticText(panel, label="Height (h):")
        self.spinH = wx.SpinCtrl(panel, min=0, max=10000)
        grid.Add(lblOffsetY, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinH, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lblX = wx.StaticText(panel, label="% of Width:")
        self.spinX = floatspin.FloatSpin(panel, min_val=0, max_val=100, digits=2)
        grid.Add(lblX, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinX, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        row += 1
        lblY = wx.StaticText(panel, label="% of Height:")
        self.spinY = floatspin.FloatSpin(panel, min_val=0, max_val=100, digits=2)
        grid.Add(lblY, pos=(row,1), flag=wx.ALL|wx.EXPAND, border=5)
        grid.Add(self.spinY, pos=(row,2), flag=wx.ALL|wx.EXPAND, border=5)

        grid.AddGrowableCol(1)
        
        hsizerBtns = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Reset Values",
                      "Get Window Pos",
                      "Get Window Size",
                      "Get Window Pos + Size"]:
            btn = wx.Button(panel, label=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            hsizerBtns.Add(btn, 1, wx.ALL|wx.EXPAND, 5)
            
        hsizerBtns2 = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Set Window Pos",
                      "Set Window Size",
                      "Set Window Pos + Size",
                      "Find Position"]:
            btn = wx.Button(panel, label=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
            hsizerBtns2.Add(btn, 1, wx.ALL|wx.EXPAND, 5)    
                
        sboxSizer.AddSpacer(10)
        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 5)
        sboxSizer.Add(hsizerBtns, 0, wx.ALL|wx.EXPAND, 5)
        sboxSizer.Add(hsizerBtns2, 0, wx.ALL|wx.EXPAND, 5)
        
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
        sizer.Fit(self)
        
        try:
            icon = wx.Icon("images/mouseclickrelative.png")
            self.SetIcon(icon)
        except Exception as e:
            print(e)
            
    def EndModal(self, id):
        if id == wx.ID_OK:
            self.GetParent().SetSelectedScheduleItem("MouseClickRelative", self.GetValue())
        self.Destroy()
            
    def FindPosition(self): 
        try:
            title, win_class = make_tuple(self.cboxWindow.GetValue())
            winman.SetForegroundWindow(title, win_class)
        except:
            # if we can't switch to window then we can't find a
            # relative position
            return 
            
        finder = FindPosition(self)
        def on_finder_close(event):
            try:
                x, y = finder.GetValue()
                logging.info("Got relative position: %s" % str((x,y)))
                self.spinX.SetValue(float(x))
                self.spinY.SetValue(float(y))
            except Exception as e:
                print(e)
                
            finder.Hide()
            self.Show()
            self.SetFocus()
            
        self.Hide()
        finder.Bind(wx.EVT_CLOSE, on_finder_close)        
        x1 = self.spinOffsetX.GetValue()
        y1 = self.spinOffsetY.GetValue()
        w = self.spinW.GetValue()
        h = self.spinH.GetValue()
        finder.SetBounds(x1, y1, w, h)        
        finder.Show()
        finder.SetFocus()
    
    def GetMatchKwargs(self):
        return {
            "matchcondition": self.cboxMatch.GetSelection(),
            "matchcase": self.chkMatchTitleCase.GetValue(),
            "matchstring": self.chkMatchTitle.GetValue(),
            "matches": int(self.cboxMatches.GetValue()),
        }
        
    def GetValue(self):
        data = []
        data.append(("window", self.cboxWindow.GetValue()))
        data.append(("matchcondition", self.cboxMatch.GetSelection()))
        data.append(("matchcase", self.chkMatchTitleCase.GetValue()))
        data.append(("matchstring", self.chkMatchTitle.GetValue()))
        data.append(("matches", int(self.cboxMatches.GetValue())))
        data.append(("resize", self.chkResize.GetValue()))
        data.append(("offsetx", self.spinOffsetX.GetValue()))
        data.append(("offsety", self.spinOffsetY.GetValue()))
        data.append(("width", self.spinW.GetValue()))
        data.append(("height", self.spinH.GetValue()))
        data.append(("%width", self.spinX.GetValue()))
        data.append(("%height", self.spinY.GetValue()))

        return str(data)
    
    def GetWindowPos(self):
        rect = self.GetWindowRect()
        if not rect:
            return
        x1, y1, x2, y2 = rect
        w = x2 - x1
        h = y2 - y1
        
        self.spinOffsetX.SetValue(x1)
        self.spinOffsetY.SetValue(y1)
        self.Raise()
        
    def GetWindowRect(self):
        try:
            progName, title = make_tuple(self.cboxWindow.GetValue())
        except: 
            return
            
        kwargs = self.GetMatchKwargs()
        handles = winman.GetHandles(progName, title, **kwargs)
        if not handles:
            return
            
        for handle in handles:
            x1, y1, x2, y2 = winman.GetWindowRect(handle)
            return x1, y1, x2, y2
    
    def GetWindowPosAndSize(self):
        rect = self.GetWindowRect()
        if not rect:
            return
        x1, y1, x2, y2 = rect
        w = x2 - x1
        h = y2 - y1
        
        self.spinOffsetX.SetValue(x1)
        self.spinOffsetY.SetValue(y1)
        self.spinW.SetValue(w)
        self.spinH.SetValue(h)
        self.Raise()
        
    def GetWindowSize(self):
        rect = self.GetWindowRect()
        if not rect:
            return
        x1, y1, x2, y2 = rect
        w = x2 - x1
        h = y2 - y1
        
        self.spinW.SetValue(w)
        self.spinH.SetValue(h)
        self.Raise()
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "Cancel":
            self.EndModal(id)
        elif label == "Find Position":
            self.FindPosition() 
        elif label == "Get Window Pos":
            self.GetWindowPos() 
        elif label == "Get Window Pos + Size":
            self.GetWindowPosAndSize()    
        elif label == "Get Window Size":
            self.GetWindowSize()  
        elif label == "Ok":
            self.EndModal(id)    
        elif label == "Refresh":
            self.RefreshWindowList()  
        elif label == "Reset Values":
            self.ResetValues()
        elif label == "Set Window Pos":
            self.SetWindowPos()
        elif label == "Set Window Pos + Size":
            self.SetWindowPosAndSize()     
        elif label == "Set Window Size":
            self.SetWindowSize()             

    def RefreshWindowList(self):
        """ 
        In Windows, retrieve a list of titles.
        In Linux, retrieve a tuple list of (title, winClass)
        """
        value = self.cboxWindow.GetValue()
        self.cboxWindow.Clear()
        choices = []
        choices.extend(winman.GetWindowList())
        self.cboxWindow.Append(choices)
        self.cboxWindow.SetValue(value)
        
    def ResetValues(self):
        self.SetValue(self.resetValue)
        
    def SetValue(self, data):
        
        if not self.resetValue:
            self.resetValue = data 
            
        for arg, func, default in (
            ["window", self.cboxWindow.SetValue, ""],
            ["matchcondition", self.cboxMatch.SetSelection, 0],
            ["matchcase", self.chkMatchTitleCase.SetValue, True],
            ["matchstring", self.chkMatchTitle.SetValue, True],
            ["matches", self.cboxMatches.SetValue, 0],
            ["resize", self.chkResize.SetValue, True],
            ["offsetx", self.spinOffsetX.SetValue, 0],
            ["offsety", self.spinOffsetY.SetValue, 0],
            ["width", self.spinW.SetValue, 0],
            ["height", self.spinH.SetValue, 0],
            ["%width", self.spinX.SetValue, 0],
            ["%height", self.spinY.SetValue, 0]):
            
            try:
                func(data[arg])
            except Exception as e:
                print(e)
                func(default)
        
    def SetWindowPos(self):
        x1 = self.spinOffsetX.GetValue()
        y1 = self.spinOffsetY.GetValue()
        
        try:
            progName, title = make_tuple(self.cboxWindow.GetValue())
        except:
            return
        kwargs = self.GetMatchKwargs()
        handles = winman.GetHandles(progName, title, **kwargs)
        if not handles:
            return
            
        for handle in handles:
            try:
                winman.MoveWindow(handle, x1, y1, None, None)
            except Exception as e:
                print(e)
                return
            
        self.Raise()
        
    def SetWindowPosAndSize(self):
        x1 = self.spinOffsetX.GetValue()
        y1 = self.spinOffsetY.GetValue()
        w = self.spinW.GetValue()
        h = self.spinH.GetValue()
        x2 = x1 + w
        y2 = y1 + h
        
        try:
            progName, title = make_tuple(self.cboxWindow.GetValue())
        except:
            return
        kwargs = self.GetMatchKwargs()    
        handles = winman.GetHandles(progName, title, **kwargs)
        if not handles:
            return
            
        for handle in handles:
            try:
                winman.MoveWindow(handle, x1, y1, w, h)
            except Exception as e:
                print(e)
                return
            
        self.Raise()
        
    def SetWindowSize(self):
        x1 = self.spinOffsetX.GetValue()
        y1 = self.spinOffsetY.GetValue()
        w = self.spinW.GetValue()
        h = self.spinH.GetValue()
        
        try:
            progName, title = make_tuple(self.cboxWindow.GetValue())
        except:
            return
        kwargs = self.GetMatchKwargs()    
        handles = winman.GetHandles(progName, title, **kwargs)
        if not handles:
            return
            
        for handle in handles:
            try:
                winman.SetWindowSize(handle, w, h)
            except Exception as e:
                print(e)
                return
            
        self.Raise()
#        
