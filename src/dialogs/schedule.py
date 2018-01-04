
import logging
import sys
import time
import wx
import base

class AddSchedule(wx.Dialog):

    def __init__(self, parent):

        wx.Dialog.__init__(self,
                           parent,
                           title="Add New Schedule")

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)



        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        lbl_name = wx.StaticText(panel, label="Schedule Name:", style=wx.TE_PROCESS_ENTER)
        self.text_name = wx.TextCtrl(panel)
        self.text_name.Bind(wx.EVT_TEXT_ENTER, self.OnFunctionEnter)
        hsizer.Add(lbl_name, 0, wx.ALL|wx.ALIGN_CENTRE, 5)
        hsizer.Add(self.text_name, 0, wx.ALL|wx.ALIGN_BOTTOM, 5)
        sbox_sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.day_of_week = {}
        self._day_of_week = ["mon","tue","wed","thu","fri","sat","sun"]
        grid = wx.GridSizer(cols=1)
        for label in self._day_of_week:
            self.day_of_week[label] = wx.Button(panel, label=str(label), name="0", size=(36,22))
            self.day_of_week[label].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.day_of_week[label], 0, wx.ALL, 0)
        hsizer.Add(grid, 0, wx.ALL, 2)

        self.hours = {}
        grid = wx.GridSizer(cols=4)
        for x in range(24):
            self.hours[x] = wx.Button(panel, label=str(x), name="0", size=(22,22))
            self.hours[x].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.hours[x], 0, wx.ALL, 0)
        hsizer.Add(grid, 0, wx.ALL, 2)

        self.mins = {}
        grid = wx.GridSizer(cols=10)
        for x in range(60):
            self.mins[x] = wx.Button(panel, label=str(x), name="0", size=(22,22))
            self.mins[x].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.mins[x], 0, wx.ALL, 0)
        hsizer.Add(grid, 1, wx.ALL, 2)

        self.secs = {}
        grid = wx.GridSizer(cols=10)
        for x in range(60):
            self.secs[x] = wx.Button(panel, label=str(x), name="0", size=(22,22))
            self.secs[x].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.secs[x], 0, wx.ALL, 0)
        hsizer.Add(grid, 1, wx.ALL, 2)

        sbox_sizer.Add(hsizer, 0, wx.ALL, 5)



        #-----
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddStretchSpacer()
        btn_cancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btn_add = wx.Button(panel, label="Add", id=wx.ID_OK)
        self.btn_add.Bind(wx.EVT_BUTTON, self.OnButton)
        hsizer.Add(btn_cancel, 0, wx.ALL|wx.EXPAND, 5)
        hsizer.Add(self.btn_add, 0, wx.ALL|wx.EXPAND, 5)

        #add to main sizer
        sizer.Add(sbox_sizer, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)

        w, h = sizer.Fit(self)

        try:
            self.SetIcon(theme.GetIcon("psu_png"))
        except:
            pass

    def OnFunctionChange(self, event):
        e = event.GetEventObject()
        value = e.GetValue()
        # e.SetValue(value.replace(" ", ""))

        if e.GetValue() == "":
            self.btn_add.Disable()
        elif e.GetValue().lower() in ["setup","main"]:
            self.btn_add.Disable()
        else:
            self.btn_add.Enable()

    def OnFunctionEnter(self, event):
        e = event.GetEventObject()
        value = e.GetValue()
        if value == "":
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

    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        id = e.GetId()

        if label == "Cancel":
            self.EndModal(id)
        elif label == "Add":
            if self.text_name.GetValue() != "":
                self.EndModal(id)

    def SetValue(self, value):
        params = value

        if "name" in params:
            self.text_name.SetValue(params["name"])

        if "dow" in params:
            for day in params["dow"]:
                self.day_of_week[day].SetName("1")
                self.day_of_week[day].SetBackgroundColour("green")

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

    def GetValue(self):

        data = []
        name = self.text_name.GetValue()

        dayofweek = []
        for day in self._day_of_week:
            if self.day_of_week[day].GetName() != "1":
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

class ScheduleDialog(wx.Dialog):

    def __init__(self, parent, title=""):

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

        lbl_function = wx.StaticText(panel, label="Schedule Name:")
        choices = []
        self.cbox_schedule = wx.ComboBox(panel, choices=choices)
        # self.cbox_schedule.Bind(wx.EVT_COMBOBOX, self.OnFunctionSelection)

        grid.Add(lbl_function, pos=(row,0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cbox_schedule, pos=(row,1), span=(0,2), flag=wx.ALL|wx.EXPAND, border=5)
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

    def OnFunctionSelection(self, event):
        self.btn_add.Enable()

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
