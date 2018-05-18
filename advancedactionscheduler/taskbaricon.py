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
import wx.adv
from version import __version__


class TaskBarIcon(wx.adv.TaskBarIcon):

    def __init__(self, parent):
        wx.adv.TaskBarIcon.__init__(self)

        self.leftClickCount = 0
        self.isWaiting = False

        self.parent = parent
        self.parent.taskBarIcon = self

        self.iconNormal = wx.Icon(wx.Bitmap("icons/iconnormal.png"))
        self.iconRunning = wx.Icon(wx.Bitmap("icons/iconrunning.png"))

        self.tooltip = "{0} {1}".format("Advanced Action Scheduler", __version__)
        self.SetTrayIcon(running=False)
        self.trayMenu = self.CreateTrayMenu()
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_UP, self.OnTrayLeft)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, self.OnTrayRight)

    @property
    def appConfig(self):
        return self.parent.GetAppConfig()

    def CreateMenuItem(self, trayMenu, label, func):
        item = wx.MenuItem(trayMenu, -1, label)
        trayMenu.Bind(wx.EVT_MENU, func, id=item.GetId())
        trayMenu.Append(item)
        return item

    def CreateTrayMenu(self):
        trayMenu = wx.Menu()
        self.CreateMenuItem(trayMenu, "Advanced Action Scheduler", self.ShowMainWindow)
        self.CreateMenuItem(trayMenu, "Settings", self.OnSettings)
        self.CreateMenuItem(trayMenu, "About", self.OnAbout)
        trayMenu.AppendSeparator()
        self.CreateMenuItem(trayMenu, "Exit", self.parent.OnClose)
        return trayMenu

    def OnAbout(self, event):
        self.parent.ShowAboutDialog()

    def OnSettings(self, event):
        self.parent.ShowSettingsDialog()

    def DoTrayAction(self, action):

        # show/hide window
        if action == 1:
            if self.parent.IsShown():
                self.parent.Hide()
            else:
                self.parent.Show()
                self.parent.Raise()

        # toggle schedule manager
        elif action == 2:
            self.parent.ToggleScheduleManager()

        # show menu
        elif action == 3:
            self.PopupMenu(self.trayMenu)

    def IsDouble(self):

        if self.leftClickCount == 1:
            self.DoTrayAction(self.appConfig["onTrayIconLeft"])

        else:
            self.DoTrayAction(self.appConfig["onTrayIconLeftDouble"])

        self.leftClickCount = 0
        self.isWaiting = False

    def OnTrayLeft(self, event=None, double=False):
        """
        This is a bit of a hacky way of wx.adv.taskBarIcon registering
        single and double click separately.

        Binding EVT_TASKBAR_LEFT_UP and EVT_TASKBAR_LEFT_DCLICK
        and double clicking would raise EVT_TASKBAR_LEFT_DCLICK
        once and EVT_TASKBAR_LEFT_UP twice.

        So instead, I just bind EVT_TASKBAR_LEFT_UP and catch
        and increment left click count. If more than one within
        a short period of time, we assume double click behaviour.
        """

        self.leftClickCount += 1
        if self.isWaiting:
            return
        self.isWaiting = True
        wx.CallLater(200, self.IsDouble)

    def OnTrayLeftDouble(self, event):
        self.isDouble = True
        self.OnTrayLeft(double=True)
        self.isDouble = False

    def OnTrayRight(self, event):
        self.PopupMenu(self.trayMenu)

    def RemoveTray(self, event=None):
        self.RemoveIcon()
        self.Destroy()

    def SetTrayIcon(self, running):
        if running:
            self.SetIcon(self.iconRunning, self.tooltip)
        else:
            self.SetIcon(self.iconNormal, self.tooltip)

    def ShowMainWindow(self, event=None):
        self.parent.Show()
        self.parent.Raise()
        self.parent.SetFocus()
