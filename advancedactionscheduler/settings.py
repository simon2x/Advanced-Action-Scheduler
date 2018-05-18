#!/usr/bin/python3
# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler>
Released subject to the GNU Public License

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import wx


class SettingsFrame(wx.Frame):

    def __init__(self, parent):

        self._title = "Settings"

        wx.Frame.__init__(self,
                          parent=parent,
                          style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_NO_TASKBAR|wx.STAY_ON_TOP,
                          title=self._title)

        self.SetIcon(wx.Icon("icons/icon.png"))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sbox = wx.StaticBox(panel, label="")
        sboxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        gridBag = wx.GridBagSizer(5, 5)

        row = 0
        self.chkShowTray = wx.CheckBox(panel, label="Show Tray Icon")
        gridBag.Add(self.chkShowTray, pos=(row, 0), flag=wx.ALL, border=5)

        row += 1
        self.chkShowSplash = wx.CheckBox(panel, label="Show Splash Screen")
        gridBag.Add(self.chkShowSplash, pos=(row, 0), flag=wx.ALL, border=5)

        row += 1
        lblTrayLeft = wx.StaticText(panel, label="On Tray Icon Left Click")
        trayChoices = ["Do Nothing", "Show/Hide Main Window", "Enable/Disable Schedule Manager",
                       "Show Tray Menu"]
        self.cboxTrayLeft = wx.ComboBox(panel, choices=trayChoices, style=wx.CB_READONLY)
        gridBag.Add(lblTrayLeft, pos=(row, 0), flag=wx.ALL, border=5)
        gridBag.Add(self.cboxTrayLeft, pos=(row, 1), flag=wx.ALL, border=5)

        row += 1
        lblTrayLeft = wx.StaticText(panel, label="On Tray Icon Left Double Click")
        self.cboxTrayLeftDouble = wx.ComboBox(panel, choices=trayChoices, style=wx.CB_READONLY)
        gridBag.Add(lblTrayLeft, pos=(row, 0), flag=wx.ALL, border=5)
        gridBag.Add(self.cboxTrayLeftDouble, pos=(row, 1), flag=wx.ALL, border=5)

        row += 1
        lblToolbarSize = wx.StaticText(panel, label="Maximum Toolbar Icon Size")
        choices = ["16", "32", "48", "64", "128", "256"]
        self.cboxToolbarSize = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        gridBag.Add(lblToolbarSize, pos=(row, 0), flag=wx.ALL, border=5)
        gridBag.Add(self.cboxToolbarSize, pos=(row, 1), flag=wx.ALL, border=5)

        row += 1
        self.chkLoadLastFile = wx.CheckBox(panel, label="Load Last Opened File")
        gridBag.Add(self.chkLoadLastFile, pos=(row, 0), flag=wx.ALL, border=5)

        row += 1
        self.chkRecentFiles = wx.CheckBox(panel, label="Remember Recently Opened Files")
        gridBag.Add(self.chkRecentFiles, pos=(row, 0), flag=wx.ALL, border=5)

        row += 1
        lbl = "Automatically Switch To Schedules Tab On Group Selection"
        self.chkGroupSelectionSwitch = wx.CheckBox(panel, label=lbl)
        gridBag.Add(self.chkGroupSelectionSwitch, pos=(row, 0), flag=wx.ALL, border=5)

        row += 1
        self.chkSchedMgrSwitch = wx.CheckBox(panel, label="Automatically Switch To Manager Tab On Enable")
        gridBag.Add(self.chkSchedMgrSwitch, pos=(row, 0), flag=wx.ALL, border=5)

        row += 1
        lblSchedMgrLogCount = wx.StaticText(panel, label="Schedule Manager Log Count")
        self.schedMgrLogCount = wx.SpinCtrl(panel, min=-1, max=1000)
        gridBag.Add(lblSchedMgrLogCount, pos=(row, 0), flag=wx.ALL, border=5)
        gridBag.Add(self.schedMgrLogCount, pos=(row, 1), flag=wx.ALL, border=5)

        row += 1
        lbl = wx.StaticText(panel, label="Maximum Undo History")
        self.maxUndoCount = wx.SpinCtrl(panel, min=0, max=1000)
        gridBag.Add(lbl, pos=(row, 0), flag=wx.ALL, border=5)
        gridBag.Add(self.maxUndoCount, pos=(row, 1), flag=wx.ALL, border=5)

        row += 1
        lblSchedMgrHotkey = wx.StaticText(panel, label="Toggle Schedule Manager Hotkey")
        self.schedMgrHotkey = wx.TextCtrl(panel)
        # self.schedMgrHotkey.Bind(wx.EVT_TEXT, self.OnHotkeyText)
        self.schedMgrHotkey.Bind(wx.EVT_CHAR_HOOK, self.OnHotkeyEdit)
        gridBag.Add(lblSchedMgrHotkey, pos=(row, 0), flag=wx.ALL, border=5)
        gridBag.Add(self.schedMgrHotkey, pos=(row, 1), flag=wx.ALL, border=5)

        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(panel, label="Cancel", id=wx.ID_CANCEL)
        btn.Bind(wx.EVT_BUTTON, self.OnButton)
        hSizer.Add(btn, flag=wx.ALL, border=5)
        btn = wx.Button(panel, label="Ok", id=wx.ID_OK)
        btn.Bind(wx.EVT_BUTTON, self.OnButton)
        hSizer.Add(btn, flag=wx.ALL, border=5)

        sboxSizer.Add(gridBag, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sboxSizer, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(hSizer, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        panel.SetSizer(sizer)
        sizer.Fit(self)

        self.SetMinSize(self.GetSize())
        self.SetMaxSize(self.GetSize())

        self.SetDefaults()

        self.Bind(wx.EVT_CHAR_HOOK, self.OnChar)

    def GetValue(self):
        data = {}
        data["groupSelectionSwitchTab"] = self.chkGroupSelectionSwitch.GetValue()
        data["showTrayIcon"] = self.chkShowTray.GetValue()
        data["showSplashScreen"] = self.chkShowSplash.GetValue()
        data["onTrayIconLeft"] = self.cboxTrayLeft.GetSelection()
        data["onTrayIconLeftDouble"] = self.cboxTrayLeftDouble.GetSelection()
        data["toolbarSize"] = self.cboxToolbarSize.GetValue()
        data["loadLastFile"] = self.chkLoadLastFile.GetValue()
        data["keepFileList"] = self.chkRecentFiles.GetValue()
        data["schedManagerSwitchTab"] = self.chkSchedMgrSwitch.GetValue()
        data["schedManagerLogCount"] = self.schedMgrLogCount.GetValue()
        data["maxUndoCount"] = self.maxUndoCount.GetValue()
        data["toggleSchedManHotkey"] = self.schedMgrHotkey.GetValue().upper()
        return data

    def OnButton(self, event):
        e = event.GetEventObject()
        id = e.GetId()
        if id == wx.ID_CANCEL:
            self.Destroy()
        elif id == wx.ID_OK:
            self.GetParent().UpdateSettingsDict(self.GetValue())
            self.Destroy()

    def OnChar(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Destroy()

    def OnHotkeyEdit(self, event):
        keycode = event.GetKeyCode()

        if keycode == wx.WXK_ESCAPE:
            self.schedMgrHotkey.SetValue("")
            return
        elif keycode == wx.WXK_RETURN:
            self.schedMgrHotkey.SetValue("")
            return

        if keycode in [wx.WXK_SHIFT, wx.WXK_RAW_CONTROL, wx.WXK_ALT]:
            return

        char = "%c" % keycode
        if keycode == wx.WXK_NONE:
            return
        if keycode == wx.WXK_SPACE:
            char = "SPACE"
        elif not char.isalnum():
            return

        if keycode in FUNCTIONKEYS:
            char = FUNCTIONKEYS[keycode]

        hotkey = []
        if event.CmdDown():
            hotkey.append("CTRL")
        if event.AltDown():
            hotkey.append("ALT")
        if event.ShiftDown():
            hotkey.append("SHIFT")
        hotkey.append(char)

        hotkey = "+".join(hotkey)
        if hotkey in RESERVEDHOTKEYS:
            return

        # combination of two or more keys?
        # but we allow function key as a standalone hotkey without combination
        if "+" not in hotkey and hotkey not in FUNCTIONKEYS.values():
            return
        self.schedMgrHotkey.SetValue(hotkey)

    def SetDefaults(self):
        self.cboxTrayLeft.SetSelection(0)
        self.cboxTrayLeftDouble.SetSelection(0)
        self.chkShowSplash.SetValue(True)
        self.cboxToolbarSize.SetValue("48")
        self.chkShowTray.SetValue(True)
        self.chkLoadLastFile.SetValue(True)
        self.chkRecentFiles.SetValue(True)
        self.chkSchedMgrSwitch.SetValue(True)
        self.schedMgrLogCount.SetValue(100)
        self.schedMgrHotkey.SetValue("")

    def SetValue(self, data):
        for arg, func, default in (
                ["toolbarSize", self.cboxToolbarSize.SetValue, "48"],
                ["showSplashScreen", self.chkShowSplash.SetValue, True],
                ["showTrayIcon", self.chkShowTray.SetValue, True],
                ["onTrayIconLeft", self.cboxTrayLeft.SetSelection, 0],
                ["onTrayIconLeftDouble", self.cboxTrayLeftDouble.SetSelection, 0],
                ["loadLastFile", self.chkLoadLastFile.SetValue, False],
                ["keepFileList", self.chkRecentFiles.SetValue, True],
                ["schedManagerSwitchTab", self.chkSchedMgrSwitch.SetValue, True],
                ["groupSelectionSwitchTab", self.chkGroupSelectionSwitch.SetValue, True],
                ["schedManagerLogCount", self.schedMgrLogCount.SetValue, 100],
                ["maxUndoCount", self.maxUndoCount.SetValue, 20],
                ["toggleSchedManHotkey", self.schedMgrHotkey.SetValue, ""]):

            try:
                func(data[arg])
            except Exception as e:
                # print(e)
                func(default)

