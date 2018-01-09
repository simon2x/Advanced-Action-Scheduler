import logging
import sys
import time
import wx
import base

DELIMITER = " ➡ "

class AddSchedule(wx.Dialog):

    def __init__(self, parent, blacklist=[]):

        wx.Dialog.__init__(self,
                           parent,
                           title="Add New Schedule")

        self.blacklist = blacklist
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        labelName = wx.StaticText(panel, label="Schedule Name:")
        self.textName = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.textName.Bind(wx.EVT_TEXT_ENTER, self.OnScheduleNameEnter)
        self.textName.Bind(wx.EVT_TEXT, self.OnScheduleNameEdit)
        self.labelError = wx.StaticText(panel, label="")
        hSizer.Add(labelName, 0, wx.ALL|wx.ALIGN_CENTRE, 5)
        hSizer.Add(self.textName, 0, wx.ALL|wx.ALIGN_BOTTOM, 5)
        hSizer.Add(self.labelError, 0, wx.ALL|wx.ALIGN_CENTRE, 5)
        sboxSizer.Add(hSizer, 0, wx.ALL|wx.EXPAND, 5)

        hSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.dayOfWeek = {}
        self._dayOfWeek = ["mon","tue","wed","thu","fri","sat","sun"]
        grid = wx.GridSizer(cols=1)
        for label in self._dayOfWeek:
            self.dayOfWeek[label] = wx.Button(panel, label=str(label), name="0", size=(36,22))
            self.dayOfWeek[label].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.dayOfWeek[label], 0, wx.ALL, 0)
        hSizer.Add(grid, 0, wx.ALL, 2)

        self.hours = {}
        grid = wx.GridSizer(cols=4)
        for x in range(24):
            self.hours[x] = wx.Button(panel, label=str(x), name="0", size=(22,22))
            self.hours[x].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.hours[x], 0, wx.ALL, 0)
        hSizer.Add(grid, 0, wx.ALL, 2)

        self.mins = {}
        grid = wx.GridSizer(cols=10)
        for x in range(60):
            self.mins[x] = wx.Button(panel, label=str(x), name="0", size=(22,22))
            self.mins[x].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.mins[x], 0, wx.ALL, 0)
        hSizer.Add(grid, 1, wx.ALL, 2)

        self.secs = {}
        grid = wx.GridSizer(cols=10)
        for x in range(60):
            self.secs[x] = wx.Button(panel, label=str(x), name="0", size=(22,22))
            self.secs[x].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.secs[x], 0, wx.ALL, 0)
        hSizer.Add(grid, 1, wx.ALL, 2)

        sboxSizer.Add(hSizer, 0, wx.ALL, 5)

        #-----
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btnOk = wx.Button(panel, label="Ok", id=wx.ID_OK)
        self.btnOk.Bind(wx.EVT_BUTTON, self.OnButton)
        hSizer.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hSizer.Add(self.btnOk, 0, wx.ALL|wx.EXPAND, 5)

        #add to main sizer
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hSizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)

        w, h = sizer.Fit(self)

        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass

    def GetValue(self):

        data = []
        name = self.textName.GetValue()

        dayofweek = []
        for day in self._dayOfWeek:
            if self.dayOfWeek[day].GetName() != "1":
                continue
            dayofweek.append(day)
        if dayofweek != []:
            data.append(("dow", dayofweek))

        hours = []
        for btn in self.hours.values():
            if btn.GetName() != "1":
                continue
            hour = btn.GetLabel()
            hours.append(hour)
        hours = sorted(hours)
        if hours != []:
            data.append(("h", hours))

        mins = []
        for btn in self.mins.values():
            if btn.GetName() != "1":
                continue
            min = btn.GetLabel()
            mins.append(min)
        mins = sorted(mins)
        if mins != []:
            data.append(("m", mins))

        secs = []
        for btn in self.secs.values():
            if btn.GetName() != "1":
                continue
            sec = btn.GetLabel()
            secs.append(sec)
        secs = sorted(secs)
        if secs != []:
            data.append(("s", secs))

        # print( data )
        if data == []:
            # default if no value
            data = [("h", "0"), ("s", "0")]

        return (name, str(data))
        
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "Cancel":
            self.EndModal(id)
        elif label == "Ok":
            self.EndModal(id)
    
    def OnScheduleNameEdit(self, event):
        e = event.GetEventObject()
        value = e.GetValue()
        if value == "":
            m = "" # leave message empty 
        elif value in self.blacklist:
            m = "Name already exists"
        elif not value.replace("_","").isalnum():
            m = "Name can be 0-9/A-Z. Underscores allowed"
        else:
            self.btnOk.Enable() 
            return
        
        self.labelError.SetLabel(m)
            
            
        self.btnOk.Disable()    
            
    def OnScheduleNameEnter(self, event):
        e = event.GetEventObject()
        id = e.GetId()
        if not self.btnOk.IsEnabled():
            return
        self.EndModal(id)
        
    def OnTimeButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        name = e.GetName()
        if name == "1":
            e.SetName("0")
            e.SetBackgroundColour("default")
        else:
            e.SetName("1")
            e.SetBackgroundColour("green")

    def SetScheduleName(self, value):
        self.textName.SetValue(value)
        
    def SetValue(self, value):
        params = value

        if "name" in params:
            self.textName.SetValue(params["name"])

        if "dow" in params:
            for day in params["dow"]:
                self.dayOfWeek[day].SetName("1")
                self.dayOfWeek[day].SetBackgroundColour("green")

        if "h" in params:
            for h in params["h"]:
                h = int(h)
                self.hours[h].SetName("1")
                self.hours[h].SetBackgroundColour("green")

        if "m" in params:
            for m in params["m"]:
                m = int(m)
                self.mins[m].SetName("1")
                self.mins[m].SetBackgroundColour("green")

        if "s" in params:
            for s in params["s"]:
                s = int(s)
                self.secs[s].SetName("1")
                self.secs[s].SetBackgroundColour("green")

class ScheduleDialog(wx.Dialog):

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

        lbl_function = wx.StaticText(panel, label="Schedule Name:")
        choices = []
        self.cbox_schedule = wx.ComboBox(panel, choices=choices)
        # self.cbox_schedule.Bind(wx.EVT_COMBOBOX, self.OnFunctionSelection)

        grid.Add(lbl_function, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cbox_schedule, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableCol(1)

        sboxSizer.AddSpacer(10)
        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 2)
        #-----
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btnOk = wx.Button(panel, label="Ok", id=wx.ID_OK)
        self.btnOk.Bind(wx.EVT_BUTTON, self.OnButton)
        # self.btnOk.Disable()
        hSizer.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hSizer.Add(self.btnOk, 0, wx.ALL|wx.EXPAND, 5)

        #add to main sizer
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hSizer, 0, wx.ALL|wx.EXPAND, 2)

        panel.SetSizer(sizer)

        w, h = sizer.Fit(self)

        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass

    def OnFunctionSelection(self, event):
        self.btnOk.Enable()

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
        name = data["schedule"]
        self.cbox_schedule.SetValue(name)

    def GetValue(self):
        data = ("schedule", self.cbox_schedule.GetValue())
        data = str([data])

        return data

class StartSchedule(ScheduleDialog):

    def __init__(self, parent):

        ScheduleDialog.__init__(self, parent, "Start Schedule")

class StopSchedule(ScheduleDialog):

    def __init__(self, parent):

        ScheduleDialog.__init__(self, parent, "Stop Schedule")
