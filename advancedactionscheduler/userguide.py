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
import wx.html2
import base
import wx.html
from wx.lib.agw import hyperlink

__title__ = "Advanced Action Scheduler"

DELIMITER = " ➡ "

RESERVEDHOTKEYS = [
    "CTRL+E",
    "CTRL+I",
    "CTRL+N",
    "CTRL+O",
    "CTRL+S",
    "CTRL+SHIFT+S",
    "CTRL+W",
    "CTRL+T",
    "CTRL+V",
    "CTRL+C",
    "CTRL+X",
    "CTRL+A"
]

FUNCTIONS = [
    "CloseWindow",
    "Control",
    "Delay",
    # "KillProcess",
    "IfWindowOpen",
    "IfWindowNotOpen",
    "MouseClickAbsolute",
    "MouseClickRelative",
    "NewProcess",
    "OpenURL",
    "Power",
    "StopSchedule",
    "StartSchedule",
    "SwitchWindow"
]

ACTIONTREE = [
    ['0', {'checked': 1, 'columns': {'0': "Schedule1 - Our first schedule"},
           'expanded': True, 'selected': False}],
    ['0,0', {'checked': 1, 'columns': {'0': "Action 1 - The first action of Schedule1 is executed"},
             'expanded': False, 'selected': False}],
    ['0,1', {'checked': 1, 'columns': {'0': "Action 2 - The second action of Schedule1 is executed"},
             'expanded': True, 'selected': False}],
    ['0,1,0', {'checked': 1, 'columns': {'0': "Child of Action 2 - The third action executed"},
               'expanded': False, 'selected': False}],
    ['0,2', {'checked': 1, 'columns': {'0': "Action 3 - The fourth (and last) action of Schedule1 is executed"},
             'expanded': False, 'selected': False}],
    ['1', {'checked': 1, 'columns': {'0': "Schedule2 - Another schedule"},
           'expanded': True, 'selected': False}],
    ['1,0', {'checked': 0, 'columns': {'0': "Action 1 - Action is not executed"},
             'expanded': True, 'selected': False}],
    ['1,0,0', {'checked': 1, 'columns': {'0': "Child of Action 1 - Not executed as parent (Action 1) is unchecked"},
               'expanded': False, 'selected': False}],
    ['1,1', {'checked': 1, 'columns': {'0': "Action 1 - The first (and last) of Schedule2 action to be executed"},
             'expanded': False, 'selected': False}],
]


LAYOUTS = {
    "Introduction": [("html", "introduction"), ],
    "Getting Started": [("html", "gettingstarted"), ],
    "Actions": [("html", "actions"), ("tree", {"schedules": ACTIONTREE})],
    "Supported Actions": [("html", "supportedactions"), ],
    "Enabling The Schedule Manager": [("html", "schedulemanager"), ],
    "Support": [],
    "Shortcut Keys": [("html", "shortcutkeys"), ],
}

CONTENTS = [
    ("Introduction",),
    ("Getting Started",),
    ("Actions",),
    ("Supported Actions",),
    ("Enabling The Schedule Manager",),

    ("Support",),
    # ("Shortcut Keys",),

]

import wx.dataview
import os
CWD = os.getcwd()


class UserGuideFrame(wx.Frame):

    def __init__(self, parent=None):

        self._title = "User Guide - Advanced Action Scheduler"

        wx.Frame.__init__(self,
                          parent=parent,
                          style=wx.DEFAULT_FRAME_STYLE,
                          title=self._title)

        self.SetIcon(wx.Icon("icons/icon.png"))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.splitter = wx.SplitterWindow(panel)

        leftPanel = wx.Panel(self.splitter)
        leftSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.contentsList = base.BaseList(leftPanel)
        self.contentsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnContentsSelect)
        self.contentsList.InsertColumn(0, "Contents")
        for x in CONTENTS:
            self.contentsList.Append(x)

        leftSizer.Add(self.contentsList, 1, wx.ALL|wx.EXPAND, 5)
        leftPanel.SetSizer(leftSizer)

        self.rightPanel = wx.Panel(self.splitter)
        self.rightSizer = wx.BoxSizer(wx.VERTICAL)
        self.rightPanel.SetSizer(self.rightSizer)

        self.splitter.SplitVertically(leftPanel, self.rightPanel)
        self.splitter.SetSashGravity(0.3)

        sizer.Add(self.splitter, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        sizer.Fit(self)

        self.SetSize((800, 600))

        self.timerPreview = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnLivePreview, self.timerPreview)
        # self.timerPreview.Start(1500)

        self.contentsList.Select(0)
        self.OnContentsSelect()

    @property
    def contentSelection(self):
        return self.contentsList.GetFirstSelected()

    def contentSelectionText(self):
        return self.contentsList.GetItemText(self.contentSelection)

    def OnContentsSelect(self, event=None):
        self.rightSizer.Clear(delete_windows=True)
        if self.contentSelection == -1:
            return
        layout = LAYOUTS[self.contentSelectionText()]

        for contentType, content in layout:

            if contentType == "html":
                html = wx.html2.WebView.New(self.rightPanel)
                html.EnableContextMenu(False)
                html.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, lambda x: -1)
                html.Bind(wx.EVT_LEFT_UP, lambda x: -1)
                html.Bind(wx.EVT_LEFT_UP, lambda x: -1)
                html.LoadURL("file://{0}/docs/userguide/en/{1}.html".format(CWD, content))
                self.rightSizer.Add(html, 1, wx.ALL|wx.EXPAND, 5)

            elif contentType == "text":
                text = wx.TextCtrl(self.rightPanel, value=content,
                                   style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH|wx.BORDER_NONE)
                self.rightSizer.Add(text, 1, wx.ALL|wx.EXPAND, 5)

            elif contentType == "tree":
                tree = base.TreeListCtrl(self.rightPanel)
                tree.AppendColumn("Schedule")
                tree.Bind(wx.EVT_CHAR, lambda x: 0)
                tree.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.OnTreeCheck)
                tree.SetTree(content["schedules"])
                self.rightSizer.Add(tree, 1, wx.ALL|wx.EXPAND, 5)

        if self.contentSelectionText() == "Support":
            text = wx.StaticText(self.rightPanel)
            t = ("If you encounter any issues or would like to submit a feature request,"
                 + "head over to the SourceForge homepage or the Github homepage")
            text.SetLabel(t)
            self.rightSizer.Add(text, 0, wx.ALL|wx.EXPAND, 5)

            g = "https://github.com/swprojects/Advanced-Action-Scheduler"
            link = hyperlink.HyperLinkCtrl(self.rightPanel, label="Github Page", URL=g)
            self.rightSizer.Add(link, 0, wx.ALL|wx.EXPAND, 5)

            s = "https://sourceforge.net/projects/advanced-action-scheduler/"
            link = hyperlink.HyperLinkCtrl(self.rightPanel, label="SourceForge Page", URL=s)
            self.rightSizer.Add(link, 0, wx.ALL|wx.EXPAND, 5)

        self.rightSizer.Layout()

    def OnTreeCheck(self, event):
        e = event.GetEventObject()
        s = e.GetSelection()
        chk = e.GetCheckedState(s)
        if chk == 1:
            e.CheckItem(s, 0)
        else:
            e.CheckItem(s, 1)

    def OnLivePreview(self, event):
        self.OnContentsSelect()


if __name__ == "__main__":
    app = wx.App()
    mainFrame = UserGuideFrame()
    mainFrame.Show()
    app.MainLoop()
