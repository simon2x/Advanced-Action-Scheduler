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
import wx
from ast import literal_eval as make_tuple

DELIMITER = " ➡ "


class AddSchedule(wx.Dialog):

    def __init__(self, parent, blacklist=[]):

        wx.Dialog.__init__(self,
                           parent,
                           title="Add New Schedule")

        self.blacklist = blacklist
        self.resetValue = None

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
        hSizer.Add(self.textName, 2, wx.ALL|wx.ALIGN_BOTTOM, 5)
        hSizer.Add(self.labelError, 2, wx.ALL|wx.ALIGN_CENTRE, 5)
        sboxSizer.Add(hSizer, 0, wx.ALL|wx.EXPAND, 5)

        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dayOfWeek = {}
        self._dayOfWeek = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        vsizer = wx.BoxSizer(wx.VERTICAL)
        labelDay = wx.StaticText(panel, label="Days")
        grid = wx.GridSizer(cols=1)
        vsizer.Add(labelDay, 0, wx.ALL|wx.ALIGN_CENTRE, 2)
        for label in self._dayOfWeek:
            self.dayOfWeek[label] = wx.Button(panel, label=str(label), name="0", size=(56, 32))
            self.dayOfWeek[label].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.dayOfWeek[label], 0, wx.ALL, 0)
        vsizer.Add(grid, 0, wx.ALL, 2)
        hSizer.Add(vsizer, 0, wx.ALL, 2)

        self.hours = {}
        vsizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(cols=4)
        labelHour = wx.StaticText(panel, label="Hours")
        vsizer.Add(labelHour, 0, wx.ALL|wx.ALIGN_CENTRE, 2)
        for x in range(24):
            self.hours[x] = wx.Button(panel, label=str(x), name="0", size=(32, 32))
            self.hours[x].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.hours[x], 0, wx.ALL, 0)
        vsizer.Add(grid, 0, wx.ALL, 2)
        hSizer.Add(vsizer, 0, wx.ALL, 2)

        self.mins = {}
        vsizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(cols=10)
        labelMin = wx.StaticText(panel, label="Minutes")
        vsizer.Add(labelMin, 0, wx.ALL|wx.ALIGN_CENTRE, 2)
        for x in range(60):
            self.mins[x] = wx.Button(panel, label=str(x), name="0", size=(32, 32))
            self.mins[x].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.mins[x], 0, wx.ALL, 0)
        vsizer.Add(grid, 0, wx.ALL, 2)
        hSizer.Add(vsizer, 0, wx.ALL, 2)

        self.secs = {}
        vsizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(cols=10)
        labelSec = wx.StaticText(panel, label="Seconds")
        vsizer.Add(labelSec, 0, wx.ALL|wx.ALIGN_CENTRE, 2)
        for x in range(60):
            self.secs[x] = wx.Button(panel, label=str(x), name="0", size=(32, 32))
            self.secs[x].Bind(wx.EVT_BUTTON, self.OnTimeButton)
            grid.Add(self.secs[x], 0, wx.ALL, 0)
        vsizer.Add(grid, 0, wx.ALL, 2)
        hSizer.Add(vsizer, 0, wx.ALL, 2)

        sboxSizer.Add(hSizer, 0, wx.ALL, 5)

        hSizerClear = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Day", "Hour", "Minute", "Second"]:
            btn = wx.Button(panel, label="Clear {0}".format(label), name=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButtonClear)
            hSizerClear.Add(btn, 0, wx.ALL|wx.EXPAND, 5)

        hSizerEvery = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Day", "Hour", "Minute", "Second"]:
            btn = wx.Button(panel, label="Every {0}".format(label), name=label)
            btn.Bind(wx.EVT_BUTTON, self.OnButtonSetAll)
            hSizerEvery.Add(btn, 0, wx.ALL|wx.EXPAND, 5)

        # -----
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnReset = wx.Button(panel, label="Reset")
        btnReset.Bind(wx.EVT_BUTTON, self.OnButtonReset)
        hSizer.Add(btnReset, 0, wx.ALL|wx.EXPAND, 5)
        hSizer.AddStretchSpacer()
        btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btnCancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btnOk = wx.Button(panel, label="Ok", id=wx.ID_OK)
        self.btnOk.Bind(wx.EVT_BUTTON, self.OnButton)
        hSizer.Add(btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hSizer.Add(self.btnOk, 0, wx.ALL|wx.EXPAND, 5)

        # add to main sizer
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hSizerClear, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hSizerEvery, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hSizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)
        w, h = sizer.Fit(self)

        try:
            icon = wx.Icon("images/schedule.png")
            self.SetIcon(icon)
        except Exception as e:
            logging.info(e)

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

    def OnButtonClear(self, event):
        e = event.GetEventObject()
        name = e.GetName()

        _, currentParams = self.GetValue()
        currentParams = {j: k for j, k in make_tuple(currentParams)}
        if name == "Days":
            p = self.dayOfWeek
        elif name == "Hours":
            p = self.hours
        elif name == "Minutes":
            p = self.mins
        elif name == "Seconds":
            p = self.secs

        for q in p:
            p[q].SetName("0")
            p[q].SetBackgroundColour("default")

    def OnButtonReset(self, event):
        """ clear all buttons and, if applicable, revert to original values """
        for p in [self.dayOfWeek, self.hours, self.mins, self.secs]:
            for q in p:
                p[q].SetName("0")
                p[q].SetBackgroundColour("default")

        if self.resetValue:
            self.SetValue(self.resetValue)

    def OnButtonSetAll(self, event):
        """ set all buttons on """
        e = event.GetEventObject()
        label = e.GetLabel()
        if "Day" in label:
            t = self.dayOfWeek
        elif "Hour" in label:
            t = self.hours
        elif "Minute" in label:
            t = self.mins
        elif "Second" in label:
            t = self.secs

        for btn in t.values():
            btn.SetName("1")
            btn.SetBackgroundColour("green")

        if self.resetValue:
            self.SetValue(self.resetValue)

    def OnScheduleNameEdit(self, event):
        e = event.GetEventObject()
        value = e.GetValue()
        if value == "":
            m = ""  # leave message empty
        elif value in self.blacklist:
            m = "Name already exists"
        elif not value.replace("_", "").isalnum():
            m = "Name can be 0-9, A-Z. Underscores allowed"
        else:
            self.btnOk.Enable()
            self.labelError.SetLabel("")
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

        if not self.resetValue:
            self.resetValue = value

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

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        grid = wx.GridBagSizer(5, 5)

        row = 0

        lblFunction = wx.StaticText(panel, label="Schedule Name:")
        choices = []
        self.cboxSched = wx.ComboBox(panel, choices=choices)
        self.cboxSched.Bind(wx.EVT_TEXT, self.OnScheduleNameEdit)

        grid.Add(lblFunction, pos=(row, 0), flag=wx.ALL|wx.ALIGN_CENTRE, border=5)
        grid.Add(self.cboxSched, pos=(row, 1), span=(0, 2), flag=wx.ALL|wx.EXPAND, border=5)
        grid.AddGrowableCol(1)

        sboxSizer.AddSpacer(10)
        sboxSizer.Add(grid, 1, wx.ALL|wx.EXPAND, 5)
        # -----
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.AddStretchSpacer()
        btnCancel = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btnCancel.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btnOk = wx.Button(panel, label="Ok", id=wx.ID_OK)
        self.btnOk.Bind(wx.EVT_BUTTON, self.OnButton)
        self.btnOk.Disable()
        hSizer.Add(btnCancel, 0, wx.ALL|wx.EXPAND, 5)
        hSizer.Add(self.btnOk, 0, wx.ALL|wx.EXPAND, 5)

        # add to main sizer
        sizer.Add(sboxSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hSizer, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)
        w, h = sizer.Fit(self)
        size = (w * 1.5, h)
        self.SetMinSize(size)
        self.SetSize(size)

    def GetValue(self):
        data = ("schedule", self.cboxSched.GetValue())
        data = str([data])

        return data

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

    def OnScheduleNameEdit(self, event):
        e = event.GetEventObject()
        value = e.GetValue()
        if value == "":
            pass
        elif not value.replace("_", "").isalnum():
            pass
        else:
            self.btnOk.Enable()
            return

        self.btnOk.Disable()

    def SetScheduleNames(self, schedules):
        for s in schedules:
            self.cboxSched.Append(s)

    def SetValue(self, data):
        try:
            name = data["schedule"]
            self.cboxSched.SetValue(name)
        except Exception as e:
            logging.debug(e)


class StartSchedule(ScheduleDialog):

    def __init__(self, parent):

        ScheduleDialog.__init__(self, parent, "Start Schedule")

        try:
            icon = wx.Icon("images/startschedule.png")
            self.SetIcon(icon)
        except Exception as e:
            print(e)


class StopSchedule(ScheduleDialog):

    def __init__(self, parent):

        ScheduleDialog.__init__(self, parent, "Stop Schedule")

        try:
            icon = wx.Icon("images/stopschedule.png")
            self.SetIcon(icon)
        except Exception as e:
            logging.debug(e)
