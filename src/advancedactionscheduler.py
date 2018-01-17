#!/usr/bin/python
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

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from ast import literal_eval as make_tuple

import psutil
import json
import logging
import dialogs
import platform
import sys
import time
import wx
import os
import os.path
import subprocess
import schedulemanager
import wx.dataview #for TreeListCtrl
import wx.lib.agw.aui as aui

from dialogs import *
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub
from wx.lib.agw import hyperlink

import base

__version__ = 0.1
__title__ = "Advanced Action Scheduler"

PLATFORM = platform.system()
if PLATFORM == "Windows":
    pass
elif PLATFORM == "Linux":
    pass

#----- logging -----#
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create file handler which logs even debug messages
#fh = logging.FileHandler('ssc.log')
fh = logging.StreamHandler()
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

#------------------------------------------------#

DELIMITER = " ➡ "
FUNCTIONS = ["CloseWindow",
             "Delay",
             # "KillProcess",
             "IfWindowOpen",
             "IfWindowNotOpen",
             "MouseClickAbsolute",
             "MouseClickRelative",
             "OpenURL",
             "Power",
             "StopSchedule",
             "StartSchedule",
             "SwitchWindow"]
  
DEFAULTCONFIG = {
    "currentFile": False, # the currently opened schedule file
    "fileList": [], # recently opened schedule files
    "fileListCount": 5, # number of recently opened files to keep in history
    "schedManagerLogCount": 10, # number of logs before clearing table
    "schedManagerSwitchTab": True, # auto switch to Manager tab when schedules enabled
    "windowPos": False, # the last window position
    "windowSize": False, # the last window size
}

class AboutDialog(wx.Frame):  
    
    def __init__(self, parent):                    
        wx.Frame.__init__(self,
                          parent,
                          -1, 
                          title=__title__)
                        
        panel = wx.Panel(self)    
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbox1 = wx.StaticBox(panel, label="")
        sboxSizer1 = wx.StaticBoxSizer(sbox1, wx.HORIZONTAL)
        grid = wx.GridSizer(cols=2)
        grid.Add(wx.StaticText(panel, label="Author:"), 0, wx.ALL, 5)
        link = hyperlink.HyperLinkCtrl(panel, label="www.sanawu.com", URL="www.sanawu.com")
        grid.Add(link, 0, wx.ALL|wx.EXPAND, 5)
        grid.Add(wx.StaticText(panel, label="Github:"), 0, wx.ALL, 5)
        g = "https://github.com/swprojects/Advanced-Action-Scheduler"
        link = hyperlink.HyperLinkCtrl(panel, label=g, URL=g)
        grid.Add(link, 1, wx.ALL|wx.EXPAND, 5)
        grid.Add(wx.StaticText(panel, label="Version:"), 0, wx.ALL, 5)
        grid.Add(wx.StaticText(panel, label=str(__version__)), 0, wx.ALL, 5)
        
        sboxSizer1.Add(grid, 1, wx.ALL|wx.EXPAND, 5)
        
        sbox2 = wx.StaticBox(panel, label="License")
        sboxSizer2 = wx.StaticBoxSizer(sbox2, wx.VERTICAL)  
              
        style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_CENTRE
        licenseText = wx.TextCtrl(panel, style=style)
        cwd = os.getcwd()
        lpath = os.path.join(cwd, "LICENSE")
        with open(lpath) as file:
            for line in file:
                licenseText.AppendText(line)
        sboxSizer2.Add(licenseText, 1, wx.ALL|wx.EXPAND, 5)
        
        sizer.Add(sboxSizer1, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(sboxSizer2, 1, wx.ALL|wx.EXPAND, 5)
        
        panel.SetSizerAndFit(sizer)
        self.Fit()
        self.Centre()
        self.SetMinSize((600, 400))
        self.SetSize((600, 400))
        self.Show()
        
class SettingsFrame(wx.Frame):

    def __init__(self, parent):

        self._title = "Settings"

        wx.Frame.__init__(self,
                          parent=parent,
                          title=self._title)
                          
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        
class Main(wx.Frame):

    def __init__(self):

        self._title = "{0} {1}".format(__title__, __version__)

        wx.Frame.__init__(self,
                          parent=None,
                          title=self._title)

        self._appConfig = DEFAULTCONFIG 
        self._aboutDialog = None
        self._settingsDialog = None
        self._data = {}
        self._menus = {}
        self._redoStack = []
        self._undoStack = []
        self._schedManager = schedulemanager.Manager(self)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        #-----
        self.CreateMenu()
        self.CreateToolbar()
        self.CreateStatusBar()
        self.SetIcon(wx.Icon("icons/icon.png"))

        #-----
        self.splitter = wx.SplitterWindow(self)

        leftPanel = wx.Panel(self.splitter)
        leftSizer = wx.BoxSizer(wx.VERTICAL)

        self.groupList = base.TreeListCtrl(leftPanel)
        self.groupList.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.OnGroupItemSelected)
        self.groupList.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.OnGroupItemChecked)
        self.groupList.AppendColumn("Group")
        self.groupList_root = self.groupList.GetRootItem()

        leftSizer.Add(self.groupList, 1, wx.ALL|wx.EXPAND, 5)
        leftPanel.SetSizer(leftSizer)

        # ----- rhs layout -----

        nbPanel = wx.Panel(self.splitter)
        self.notebook = wx.Notebook(nbPanel)
        nbSizer = wx.BoxSizer(wx.VERTICAL)
        nbSizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 2)

        # the schedule panel/tab page
        schedPanel = wx.Panel(self.notebook)
        schedSizer = wx.BoxSizer(wx.VERTICAL)

        # -----
        hSizerFunctions = wx.WrapSizer(wx.HORIZONTAL)
        self.schedBtns = {}
        for label in ["Add Schedule", "Up", "Down", "Edit", "Toggle", "Delete"]:
            btn = wx.Button(schedPanel, label=label, name=label, size=(-1, -1), style=wx.BU_EXACTFIT|wx.BU_NOTEXT)
            btn.Disable()
            self.schedBtns[label] = btn
            img = wx.Image("icons/{0}.png".format(label.lower().replace(" ", "")))
            img = img.Rescale(32,32, wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img)
            if label == "Edit":
                btn.Bind(wx.EVT_BUTTON, self.OnScheduleItemEdit)
            else:
                btn.Bind(wx.EVT_BUTTON, self.OnScheduleToolBar)
            if label in ["Delete"]:
                hSizerFunctions.AddStretchSpacer()

            btn.SetBitmap(bmp)

            tooltip = wx.ToolTip(label)
            btn.SetToolTip(tooltip)
            hSizerFunctions.Add(btn, 0, wx.ALL|wx.EXPAND, 2)
        schedSizer.Add(hSizerFunctions, 0, wx.ALL|wx.EXPAND, 2)

        schedSizer.Add(wx.StaticLine(schedPanel), 0, wx.ALL|wx.EXPAND, 2)

        # -----
        hSizerFunctions2 = wx.BoxSizer(wx.HORIZONTAL)

        self.cboxFunctions = wx.ComboBox(schedPanel, style=wx.CB_READONLY, choices=FUNCTIONS)
        self.cboxFunctions.SetSelection(0)
        self.cboxFunctions.Bind(wx.EVT_COMBOBOX, self.OnComboboxFunction)

        btnAddFunction = wx.Button(schedPanel, label="Add Function", size=(-1, -1))
        btnAddFunction.Bind(wx.EVT_BUTTON, self.OnScheduleToolBar)

        hSizerFunctions2.Add(self.cboxFunctions, 0, wx.ALL|wx.CENTRE, 5)
        hSizerFunctions2.Add(btnAddFunction, 0, wx.ALL|wx.CENTRE, 5)

        schedSizer.Add(hSizerFunctions2, 0, wx.ALL, 0)

        # schedSizer.Add(wx.StaticLine(schedPanel), 0, wx.ALL|wx.EXPAND, 0)

        # -----

        self.splitter2 = wx.SplitterWindow(schedPanel)

        self.schedList = base.TreeListCtrl(self.splitter2, style=wx.dataview.TL_CHECKBOX)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.OnScheduleTreeActivated)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.OnScheduleTreeSelectionChanged)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.OnScheduleTreeItemChecked)
        self.schedList.AppendColumn("Schedule")

        infoPanel = wx.Panel(self.splitter2)
        infoPanelSizer = wx.BoxSizer(wx.VERTICAL)
        self.infoSched = wx.TextCtrl(infoPanel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH)

        infoPanelSizer.Add(self.infoSched, 1, wx.ALL|wx.EXPAND, 0)
        infoPanel.SetSizer(infoPanelSizer)

        self.splitter2.SplitHorizontally(self.schedList, infoPanel)
        self.splitter2.SetSashGravity(0.8)

        schedSizer.Add(self.splitter2, 1, wx.ALL|wx.EXPAND, 5)
        schedPanel.SetSizer(schedSizer)

        # the schedule manager panel/tab page
        schedManagerPanel = wx.Panel(self.notebook)
        schedManagerSizer = wx.BoxSizer(wx.VERTICAL)
        schedManagerPanel.SetSizer(schedManagerSizer)

        schedManagerHsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.chkBoxes = {}
        for lbl in ["All","Schedules","Actions","Errors"]:
            chkBox = wx.CheckBox(schedManagerPanel, label=lbl)
            self.chkBoxes[lbl] = chkBox
            schedManagerHsizer.Add(chkBox, 0, wx.ALL, 5)
        self.chkBoxes["All"].SetValue(True)
        schedManagerSizer.Add(schedManagerHsizer, 0, wx.ALL, 0)

        self.schedLog = base.BaseList(schedManagerPanel)
        self.schedLog.InsertColumn(0, "#")
        self.schedLog.InsertColumn(1, "Time")
        self.schedLog.InsertColumn(2, "Message")
        schedManagerSizer.Add(self.schedLog, 1, wx.ALL|wx.EXPAND, 0)

        self.notebook.AddPage(schedPanel, "Schedules")
        self.notebook.AddPage(schedManagerPanel, "Manager")

        nbPanel.SetSizer(nbSizer)

        self.splitter.SplitVertically(leftPanel, nbPanel)
        self.splitter.SetSashGravity(0.2)

        self.SetMinSize((700, 600))
        self.SetSize((700, 600))

        #-----
        self.Show()
            
        #load settings
        self.LoadConfig()
        
    def AppendLogMessage(self, message):
        """ append log message to schedule messenger list """
        if self.schedLog.GetItemCount() == self._appConfig["schedManagerLogCount"]:
            self.schedLog.DeleteAllItems()
        i = self.schedLog.GetItemCount()
        self.schedLog.Append([str(i)] + message)

    def ClearUI(self):
        """ clears lists and set toolbar/button states appropriately """
        self.groupList.DeleteAllItems()
        self.schedList.DeleteAllItems()
        self._data = {}
        self._appConfig["currentFile"] = False
        self.UpdateScheduleToolbar()
        self.UpdateTitlebar()
        
    def CloseFile(self):
        dlg = wx.MessageDialog(self,
                               message="Save file before closing?",
                               caption="Close File",
                               style=wx.YES_NO|wx.CANCEL|wx.CANCEL_DEFAULT)
        ret = dlg.ShowModal()                 
        if ret == wx.ID_CANCEL:
            return
        
        if ret == wx.ID_YES:
            self.SaveData()
        
        self.ClearUI()
        
    def CreateMenu(self):
        menubar = wx.MenuBar()

        menuFile = wx.Menu()
        fileMenus = [("New", "New Schedule File", True, wx.ID_ANY),
                     ("Open...", "Open Schedule File", True, wx.ID_ANY),
                     ("Save", "Save Schedule File", True, wx.ID_ANY),
                     ("Save As...", "Save Schedule File As...", True, wx.ID_ANY),
                     ("Close File", "Close Schedule File", True, wx.ID_ANY),
                     ("Import", "Import Schedule File", True, wx.ID_ANY),
                     ("Settings", "Open Settings...", True, wx.ID_ANY),
                     ("Exit", "Exit Program", True, wx.ID_ANY)]
        for item, helpStr, state, wxId in fileMenus:
            self._menus[item] = menuFile.Append(wxId, item, helpStr)
            self._menus[item].Enable(state)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])

            if item == "Import":
                menuFile.AppendSeparator()
            elif item == "Settings":
                menuFile.AppendSeparator()

        menuRun = wx.Menu()
        runMenus = [("Enable Schedule Manager", "Enable Schedule Manager"),
                    ("Disable Schedule Manager", "Disable Schedule Manager")]
        for item, helpStr in runMenus:
            self._menus[item] = menuRun.Append(wx.ID_ANY, item, helpStr)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])
            
        menuHelp = wx.Menu()
        helpMenus = [("Check for updates", "Check for updates (Not Yet Implemented)"),
                     ("About", "Import Images From Folder")]
        for item, helpStr in helpMenus:
            self._menus[item] = menuHelp.Append(wx.ID_ANY, item, helpStr)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])

        menubar.Append(menuFile, "&File")
        menubar.Append(menuRun, "&Run")
        menubar.Append(menuHelp, "&Help")
        self.menubar = menubar
        self.SetMenuBar(menubar)

    def CreateToolbar(self):
        # toolbar = wx.ToolBar(self, style=wx.TB_TEXT|wx.TB_FLAT)
        # toolbar = wx.ToolBar(self, style=wx.TB_TEXT)
        toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        # toolbar.AddTool(wx.ID _ANY, "t")#,  wx.BitmapFromBuffer(wx.ART_FILE_OPEN))
        toolbar.SetToolBitmapSize((48,48))
        # toolbar.SetToolBitmapSize((48,48))
        # toolbar.SetBackgroundColour("white")
        for label, help, state, wxId in [  
            ("New", "New", True, wx.ID_NEW),
            ("Open", "Open", True, wx.ID_OPEN),
            ("Save", "Save", True, wx.ID_SAVE),
            ("Save As...", "Save As...", True, wx.ID_SAVEAS),
            ("Close", "Close", True, wx.ID_CLOSE),
            ("Import", "Import", True, wx.ID_ANY),
            ("Add Group", "Add Group", True, wx.ID_ADD),
            ("Remove Group", "Remove Selected Group", False, wx.ID_REMOVE),
            ("Undo", "Undo", False, wx.ID_UNDO),
            ("Redo", "Redo", False, wx.ID_REDO),
            ("Enable Schedule Manager", "Enable Schedule Manager", True, wx.ID_ANY),
            ("Settings", "Settings", True, wx.ID_ANY)]:

            try:
                img = wx.Image("icons/{0}.png".format(label.lower().replace(" ", "").replace(".","")))
                img.Rescale(48,48, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
                tool = toolbar.AddTool(wxId, label=label, bitmap=bmp, shortHelp=help)
            except:
                bmp = wx.Bitmap(48,48)
                tool = toolbar.AddTool(wxId, label=label, bitmap=bmp, shortHelp=help)
            self.Bind(wx.EVT_TOOL, self.OnToolBar, tool)
            
            tool.Enable(state)
            
            if label == "Close":
                toolbar.AddSeparator()  
            elif label == "Redo":
                toolbar.AddSeparator()
            elif label == "Enable Schedule Manager":
                toolbar.AddStretchableSpace()

        toolbar.Realize()
        self.toolbar = toolbar
        self.SetToolBar(toolbar)

    def DeleteScheduleItem(self):   
        selection = self.schedList.GetSelection()
        if not selection.IsOk():
            return

        self.SaveStateToUndoStack()
        self.schedList.DeleteItem(selection)
        self.UpdateScheduleToolbar()
        self.SaveScheduleTreeToData()
       
    def DisableScheduleManager(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        tool = e.FindById(id)
        tool.SetLabel("Enable Schedule Manager")
        e.SetToolShortHelp(id, "Enable Schedule Manager")

        img = wx.Image("icons/enableschedulemanager.png")
        img = img.Rescale(48,48, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.Bitmap(img)
        e.SetToolNormalBitmap(id, bmp)

        self._schedManager.Stop()
        
    def DoRedo(self):
        print(self._redoStack)
        # can we redo?
        try:
            state = self._redoStack[-1]
            # self._undoStack.append(state)
            del self._redoStack[-1]
        except:
            logging.info("No redo operations are possible")
            return

        self.SaveStateToUndoStack()

        self._data = state["data"]

        self.groupList.DeleteAllItems()
        self.schedList.DeleteAllItems()

        for k,v in self._data.items():
            name = self._data[k]["name"]
            item = self.groupList.InsertItem(int(k), name)
            checked = v["checked"]
            if checked == "True":
                self.groupList.CheckItem(item)

        self.groupList.Select(state["groupIdx"])

        self.WriteData()

    def DoUndo(self):
        # can we undo?
            try:
                state = self._undoStack[-1]
                # self._redoStack.append(state)
                del self._undoStack[-1]
            except:
                logging.info("No undo operations are possible")
                return

            self.SaveStateToRedoStack()

            self._data = state["data"]

            self.groupList.DeleteAllItems()
            self.schedList.DeleteAllItems()

            for k,v in self._data.items():
                name = self._data[k]["name"]
                item = self.groupList.InsertItem(int(k), name)
                checked = v["checked"]
                if checked == "True":
                    self.groupList.CheckItem(item)

            self.groupList.Select(state["groupIdx"])

            self.WriteData()    
    
    def EnableScheduleManager(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        tool = e.FindById(id)
        tool.SetLabel("Disable Schedule Manager")
        e.SetToolShortHelp(id, "Disable Schedule Manager")

        img = wx.Image("icons/disableschedulemanager.png")
        img = img.Rescale(48,48, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.Bitmap(img)
        e.SetToolNormalBitmap(id, bmp)
        
        sendData = {}
        for item, scheds in self._data.items():
            if self.groupList.GetCheckedState(item) == 0:
                continue
            itemText = self.groupList.GetItemText(item)
            sendData[itemText] = scheds
            
        if not sendData:
            return
        self._schedManager.SetSchedules(sendData)
        self._schedManager.Start()

        # switch to the manager when schedules are started
        if self._appConfig["schedManagerSwitchTab"] is True:
            self.notebook.SetSelection(1)
        
    def GetDialog(self, label, value=None):

        if label == "CloseWindow":
            dlg = dialogs.window.WindowDialog(self, title="Close Window")
        elif label == "Delay":
            dlg = dialogs.delay.AddDelay(self)
        elif label == "IfWindowNotOpen":
            dlg = dialogs.window.WindowDialog(self, title="If Window Open")
        elif label == "IfWindowOpen":
            dlg = dialogs.window.WindowDialog(self, title="If Window Not Open")
        elif label == "KillProcess":
            dlg = dialogs.window.WindowDialog(self, title="Kill Process")
        elif label == "SwitchWindow":
            dlg = dialogs.window.WindowDialog(self, title="Switch Window")
        elif label == "MouseClickAbsolute":
            dlg = dialogs.mouseabsolute.MouseClickAbsolute(self)
        elif label == "MouseClickRelative":
            dlg = dialogs.mouserelative.MouseClickRelative(self)
        elif label == "OpenURL":
            dlg = dialogs.browser.OpenURL(self)
        elif label == "Power":
            dlg = power.AddPower(self)
        elif label == "StartSchedule":
            dlg = dialogs.schedule.StartSchedule(self)
        elif label == "StopSchedule":
            dlg = dialogs.schedule.StopSchedule(self)

        if value:
            dlg.SetValue(value)

        return dlg

    def GetDataForJSON(self):
        """ convert data for json dump """ 
        n = 0
        jsonData = {idx:idxData for idx, idxData in self.GetGroupTree()}
        child = self.groupList.GetFirstItem()
        while child.IsOk():
            childText = self.groupList.GetItemText(child)
            for item, itemData in self._data.items():
                if self.groupList.GetItemText(item) != childText:
                    continue
                break
            jsonData[str(n)]["schedules"] = itemData
            n += 1    
            child = self.groupList.GetNextSibling(child)
            
        return jsonData
        
    def GetGroupListIndex(self, item):
        """ only way to finding existing item in self._data by comparing TreeListItem """
        for dataItem in self._data.keys():
            if dataItem == item:
                return dataItem
        return -1
    
    def GetGroupNames(self):
        """ return ordered list of group names """
        groupNames = []
        child = self.groupList.GetFirstItem()
        while child.IsOk():
            groupNames.append(self.groupList.GetItemText(child, col=0))
            child = self.groupList.GetNextSibling(child)
        return groupNames
        
    def GetGroupTree(self):
        """ retrieve tree structure, used for saving data """
        data = self.groupList.GetTree()
        return data

    def GetScheduleNames(self):
        """ return toplevel items"""
        schedules = []
        item = self.schedList.GetFirstItem()
        while item.IsOk():
            if self.schedList.GetCheckedState(item) == 1:
                schedules.append(self.schedList.GetItemText(item, 0).split(DELIMITER)[0])
            item = self.schedList.GetNextSibling(item)

        return schedules

    def GetScheduleTree(self):
        """ retrieve tree structure, used for saving data """
        data = self.schedList.GetTree()
        return data
    
    def GetScheduleTreeAndWriteData(self):
        # save tree to data
        #self.schedList.DeleteAllItems()
        # update schedule list
        groupIdx = self.groupList.GetSelection()

        # checked = self.groupList.GetCheckedState(selection)
        schedules = self.schedList.GetTree()
        self._data[groupIdx]["schedules"] = schedules
        print(self._data)
        self.WriteData()

    def GetTopLevel(self):
        """ return sequence tree top-level """
        try:
            selection = item = self.schedList.GetSelection()
        except:
            return False

        if not selection.IsOk():
            return False

        text = self.schedList.GetItemText(selection)

        # root = self.schedList.GetRootItem()
        # parent = self.schedList.GetItemParent(selection)

        parents = [item]
        # get item parents
        while self.schedList.GetItemParent(item).IsOk():
            parent = self.schedList.GetItemParent(item)
            parents.append(parent)
            item = parent

        parents = [self.schedList.GetItemText(itm) for itm in parents if itm.IsOk()]
        print( parents )
        return parents[-2]
    
    def LoadConfig(self):
        """ load application config and restore config settings """
        try:
            with open("config.json", 'r') as file:
                self._appConfig.update(json.load(file))
        except FileNotFoundError:
            with open("config.json", 'w') as file:
                json.dump(self._appConfig, file, sort_keys=True, indent=2)
        except json.JSONDecodeError:
            with open("config.json", 'w') as file:
                json.dump(self._appConfig, file, sort_keys=True, indent=2)
        
        if os.path.exists(self._appConfig["currentFile"]):
            self.LoadFile(self._appConfig["currentFile"])
        else:
           self._appConfig["currentFile"] = False
           
    def LoadFile(self, filePath):
        try:
            with open(filePath, 'r') as file:
                fileData = json.load(file)

            self.SetGroupTree(fileData)
            self.schedList.DeleteAllItems()
            self._appConfig["currentFile"] = filePath
            self.SaveDataToJSON("config.json", self._appConfig)
            self.UpdateTitlebar()
            
            # self.menubar.Enable(wx.ID_CLOSE, True)
            
        except FileNotFoundError:
            return
        except json.JSONDecodeError:
            # TODO: raise corrupt/invalid file error
            return
    
    def MoveScheduleItemDown(self):
        # valid item selection?
        selection = self.schedList.GetSelection()
        if not selection.IsOk():
            return

        # can item be moved down?
        next = self.schedList.GetNextSibling(selection)
        assert next.IsOk(), "Next item is not valid"
        
        baseIdx = self.schedList.GetItemIndex(selection)
        
        self.SaveStateToUndoStack()
        
        subTree = self.schedList.GetSubTree(selection)
        self.schedList.InsertSubTree(next, subTree)        
        self.schedList.DeleteItem(selection)
                
        # need to reflect these changes in self._data
        groupSel = self.GetGroupListIndex(self.groupList.GetSelection())
        groupScheds = self._data[groupSel]
        
        baseIdxSplitLen = len(baseIdx.split(",")) - 1
        nextBaseIdx = baseIdx.split(",")
        nextBaseIdx[-1] = str(int(nextBaseIdx[-1])+1)
        nextBaseIdx = ",".join(nextBaseIdx)
        
        idxDecr = []
        idxIncr = []
        for n, (idx, idxData) in enumerate(groupScheds):
            if idx.startswith(baseIdx):
                idxSplit = idx.split(",")
                idxSplit[baseIdxSplitLen] = str(int(idxSplit[baseIdxSplitLen])+1)
                idx = ",".join(idxSplit)
                groupScheds[n] = (idx, idxData)
                idxIncr.append(n)
            elif idx.startswith(nextBaseIdx):
                idxSplit = idx.split(",")
                idxSplit[baseIdxSplitLen] = str(int(idxSplit[baseIdxSplitLen])-1)
                idx = ",".join(idxSplit)
                groupScheds[n] = (idx, idxData)
                idxDecr.append(n)
                
        newScheds = groupScheds[:idxIncr[0]]
        for x in idxDecr:
            newScheds.append(groupScheds[x])
        for x in idxIncr:
            newScheds.append(groupScheds[x])
        newScheds += groupScheds[idxDecr[-1]+1:] 
        self._data[groupSel] = newScheds      
        
        self.SaveStateToUndoStack()
        self.schedList.Select(self.schedList.GetNextSibling(next))
        self.UpdateScheduleToolbar()
        # finally, clear the redo stack        
        self._redoStack = []
    
    def MoveScheduleItemUp(self):
        """ move item up by moving the previous item down """

        # valid item selection?
        selection = self.schedList.GetSelection()
        if not selection.IsOk():
            return
        baseIdx = self.schedList.GetItemIndex(selection)
        
        parent = self.schedList.GetItemParent(selection)        
        previous = self.schedList.GetPreviousSibling(selection)
        assert previous.IsOk() is True, "Previous item is not valid"
        self.SaveStateToUndoStack()
        
        prevSubTree = self.schedList.GetSubTree(previous)
        self.schedList.InsertSubTree(selection, prevSubTree)
        self.schedList.DeleteItem(previous)
        
        # need to reflect these changes in self._data
        groupSel = self.GetGroupListIndex(self.groupList.GetSelection())
        groupScheds = self._data[groupSel]
        
        baseIdxSplitLen = len(baseIdx.split(",")) - 1
        prevBaseIdx = baseIdx.split(",")
        prevBaseIdx[-1] = str(int(prevBaseIdx[-1])-1)
        prevBaseIdx = ",".join(prevBaseIdx)
        
        idxDecr = []
        idxIncr = []
        for n, (idx, idxData) in enumerate(groupScheds):
            if idx.startswith(baseIdx):
                idxSplit = idx.split(",")
                idxSplit[baseIdxSplitLen] = str(int(idxSplit[baseIdxSplitLen])-1)
                idx = ",".join(idxSplit)
                groupScheds[n] = (idx, idxData)
                idxDecr.append(n)
            elif idx.startswith(prevBaseIdx):
                idxSplit = idx.split(",")
                idxSplit[baseIdxSplitLen] = str(int(idxSplit[baseIdxSplitLen])+1)
                idx = ",".join(idxSplit)
                groupScheds[n] = (idx, idxData)
                idxIncr.append(n)
                
        print(idxDecr, idxIncr)
        newScheds = groupScheds[:idxIncr[0]]
        for x in idxDecr:
            newScheds.append(groupScheds[x])
        for x in idxIncr:
            newScheds.append(groupScheds[x])
        newScheds += groupScheds[idxDecr[-1]+1:] 
        self._data[groupSel] = newScheds
        
        self.UpdateScheduleToolbar()
         
    def OnClose(self, event):
        # save data before exiting
        self.WriteData()
        event.Skip()

    def OnAboutDialogClose(self, event):
        try:
            self._aboutDialog = None
            event.Skip()
        except Exception as e:
            print(e)
        
    def OnComboboxFunction(self, event=None):
        """ selecting a combobox option automatically raises a corresponding dialog """

        schedSel = self.schedList.GetSelection()
        if not schedSel.IsOk():
            return
            
        index = self.cboxFunctions.GetSelection()
        if index == -1:
            return
        label = self.cboxFunctions.GetStringSelection()
        logging.info("OnComboboxFunction event: %s" % label)
        logging.debug(index)        

        dlg = self.GetDialog(label)
        ret = dlg.ShowModal()
        if ret == wx.ID_CANCEL:
            return

        value = label + DELIMITER + dlg.GetValue()
        newItem = self.schedList.AppendItem(schedSel, value)
        
        schedSelIdx = self.schedList.GetItemIndex(schedSel)
        idx = self.schedList.GetItemIndex(newItem)
        groupSel = self.groupList.GetSelection()
       
        n = 0
        itm = self.schedList.GetFirstItem()
        while itm != newItem and itm.IsOk():
            n += 1
            itm = self.schedList.GetNextItem(itm)
            
        self._data[groupSel].insert(n, (idx, {'columns': {"0": value}, 
                                              'expanded': False, 
                                              'selected': True, 
                                              'checked': 1}))
        
        self.schedList.Select(newItem)
        self.schedList.CheckItem(newItem)
        self.schedList.Expand(newItem)
        self.schedList.SetFocus()
            
    def OnGroupItemChecked(self, event):
        return

    def OnGroupItemKeyDown(self, event):
        key = event.GetKeyCode()
        index = self.groupList.GetSelection()
        # if index == -1:
            # return
        print(key)
        if key == wx.WXK_SPACE:
            self.groupList.CheckItem( index )
            
    def OnGroupItemSelected(self, event):
        """ update schedule list """
        groupSel = self.groupList.GetSelection()
        for item, data in self._data.items():
            print(groupSel==item)
            if groupSel != item:
                continue
            self.toolbar.EnableTool(wx.ID_REMOVE, True)
            self.SetScheduleTree(data)
            
            self.schedBtns["Add Schedule"].Enable()
            return
        
        self.toolbar.EnableTool(wx.ID_REMOVE, False)
        
        self.schedBtns["Add Schedule"].Disable()
        self.UpdateScheduleToolbar()
        # # click the information text
        # self.infoSched.SetValue("")
    
    def OnListItemActivated(self, event):
        self.OnAddFunction()

    def OnMenu(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        label = e.GetLabel(id)

        if label == "About":
            self.ShowAboutDialog()
        elif label == "Close File":
            self.CloseFile()  
        elif label == "Check for updates":
            self.ShowCheckForUpdatesDialog()  
        elif label == "Exit":
            self.Close()
        elif label == "Import":
            self.ShowImportDialog()
        elif label == "New":
            self.CloseFile()
        elif label == "Open...":
            self.OpenFile()
        elif label == "Save As...":
            self.SaveFileAs()  
        elif label == "Settings":
            self.ShowSettingsDialog() 
    
    def OnScheduleItemEdit(self, event=None):
        selection = self.schedList.GetSelection()
        if not selection.IsOk():
            return
        
        itemText = self.schedList.GetItemText(selection, 0)
        name, params = itemText.split(DELIMITER)
        params = make_tuple(params)
        params = {x:y for x,y in params}
        params["name"] = name
        
        # is item top level? i.e. a schedule
        if self.schedList.GetItemParent(selection) == self.schedList.GetRootItem():
            schedNames = [s for s in self.GetScheduleNames() if not s == name]
            dlg = dialogs.schedule.AddSchedule(self, blacklist=schedNames)
            dlg.SetScheduleName(name)
            dlg.SetValue(params)
            if dlg.ShowModal() != wx.ID_OK:
                return
            newName, value = dlg.GetValue()
            value = newName + DELIMITER + value
            self.schedList.SetItemText(selection, 0, value)
        else:
            dlg = self.GetDialog(name)
            dlg.SetValue(params)
            if dlg.ShowModal() != wx.ID_OK:
                return
            value = dlg.GetValue()
            value = name + DELIMITER + value
            self.schedList.SetItemText(selection, 0, value)
                
        idx = self.schedList.GetItemIndex(selection)
        groupSel = self.groupList.GetSelection()
        for n, (j, k) in enumerate(self._data[groupSel]):
            if not j == idx:
                continue 
            self._data[groupSel][n][1]["columns"]["0"] = value
            break
          
        self.schedList.SetFocus()

        # updated information
        self.infoSched.SetValue(value)    

    def OnScheduleToolBar(self, event):
        e = event.GetEventObject()
        name = e.GetName()

        if name == "Add Function":
            self.OnComboboxFunction()

        elif name == "Add Schedule":
            self.ShowAddScheduleDialog()
                
        elif name == "Delete":
            self.DeleteScheduleItem()   
            
        elif name == "Down":
            self.MoveScheduleItemDown()
            
        elif name == "Toggle":
            self.ToggleScheduleSelection()
            
        elif name == "Up":
            self.MoveScheduleItemUp()   
            
    def OnScheduleTreeActivated(self, event):
        self.OnScheduleItemEdit(None)        
        
    def OnScheduleTreeSelectionChanged(self, event=None):
    
        """ update the schedule item information """

        selection = self.schedList.GetSelection()
        # logging.info("Schedule tree items selected: %s" % str(selection))
        try:
            text = self.schedList.GetItemText(selection)
            self.infoSched.SetValue(text)
        except:
            self.infoSched.SetValue("")
            
        self.UpdateScheduleToolbar()    
            
    def OnScheduleTreeItemChecked(self, event):
        selection = self.schedList.GetSelection()
        groupSel = self.GetGroupListIndex(self.groupList.GetSelection())
        idx = self.schedList.GetItemIndex(selection)
        for n, (j, k) in enumerate(self._data[groupSel]):
            if not j == idx:
                continue 
            self._data[groupSel][n][1]["checked"] = self.schedList.GetCheckedState(selection)
            break

    def OnToolBar(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        tool = e.FindById(id)
        label = tool.GetLabel()
        logging.info("OnToolBar event: %s" % label)

        if label == "Add Group":
            self.ShowAddGroupDialog()
        elif label == "Close":
            self.CloseFile()    
        elif label == "Disable Schedule Manager":
            self.DisableScheduleManager(event)
        elif label == "Enable Schedule Manager":
            self.EnableScheduleManager(event)
        elif label == "Import":
            self.ShowImportDialog()    
        elif label == "New":
            self.CloseFile()
        elif label == "Open":
            self.OpenFile()    
        elif label == "Remove Group":
            self.ShowRemoveGroupDialog()        
        elif label == "Redo":
            self.DoRedo()
        elif label == "Save":
            self.SaveData()
        elif label == "Save As...":
            self.SaveFileAs() 
        elif label == "Settings":
            self.ShowSettingsDialog()   
        elif label == "Undo":
            self.DoUndo()
        
    def OpenFile(self):
        
        # ask if user wants to save first
        dlg = wx.MessageDialog(self,
                               message="Save file before closing?",
                               caption="Close File",
                               style=wx.YES_NO|wx.CANCEL|wx.CANCEL_DEFAULT)
        ret = dlg.ShowModal()                 
        if ret == wx.ID_CANCEL:
            return
        
        if ret == wx.ID_YES:
            self.SaveData()  
            
        # proceed by opening file
        wildcard = "JSON files (*.json)|*.json;"
        dlg = wx.FileDialog(self, 
                            defaultDir="",
                            message="Open Schedule File", 
                            wildcard=wildcard,
                            style=wx.FD_DEFAULT_STYLE|wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        
        self.ClearUI()        
        path = dlg.GetPath()
        _, file = os.path.split(path)
        self.LoadFile(path)
        
    def PrependSubTree(self, previous, data):
        """ insert sub tree before item """

        items = {}
        expanded_items = []
        tree = self.schedList
        for key in sorted(data.keys()):


            if key == "0":
                parent = None
            else:
                parent = key.split(",")[:-1]
                parent = ",".join(parent)
                parent = items[parent]

            value = data[key]["data"]

            if not parent:
                # parent = tree.GetItemParent(previous)
                # parenti
                item = tree.PrependItem(previous, value["0"])
            else:
                item = tree.AppendItem(parent, value["0"])
            # tree.SetItemText(item, 1, value["1"])
            # tree.SetItemText(item, 2, value["2"])

            checked = data[key]["checked"]
            if checked == 1:
                tree.CheckItem(item)
            selected = data[key]["selected"]
            if selected is True:
                tree.Select(item)
            expanded = data[key]["expanded"]
            if expanded is True:
                expanded_items.append(item)
            items[key] = item

        for item in expanded_items:
            tree.Expand(item)
    
    def SaveData(self):
        jsonData = self.GetDataForJSON()
        if self._appConfig["currentFile"] is not False:
            self.SaveDataToJSON(self._appConfig["currentFile"], jsonData)
            return
            
        wildcard = "JSON files (*.json)|*.json"
        file = wx.FileDialog(self, 
                             defaultDir="",
                             message="Save File", 
                             wildcard=wildcard,
                             style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
        
        if file.ShowModal() == wx.ID_CANCEL:
            return
           
        self._appConfig["currentFile"] = file.GetPath()
        self.SaveDataToJSON("config.json", self._appConfig)
        self.SaveDataToJSON(self._appConfig["currentFile"], jsonData)
        self.UpdateTitlebar()
        
    def SaveDataToJSON(self, filePath, data):    
        with open(filePath, "w") as file:
            json.dump(data, file, sort_keys=True, indent=2)
        
    def SaveFileAs(self):
    
        if self._appConfig["currentFile"]:
            path, name = os.path.split(self._appConfig["currentFile"])
        else:
            path, name = "", ""
            
        wildcard = "JSON files (*.json)|*.json;"
        file = wx.FileDialog(self, 
                             defaultDir=path,
                             defaultFile=name,
                             message="Save Schedule File As...", 
                             wildcard=wildcard,
                             style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        
        if file.ShowModal() == wx.ID_CANCEL:
            return
        
        jsonData = self.GetDataForJSON()
        self._appConfig["currentFile"] = file.GetPath()
        self.SaveDataToJSON("config.json", self._appConfig)
        self.SaveDataToJSON(file.GetPath(), jsonData)
        self.UpdateTitlebar()
        
    def SaveScheduleTreeToData(self):
        """ cache schedule tree to selected group item in data """
        schedules = self.GetScheduleTree()
        groupSel = self.groupList.GetSelection()
        for item, data in self._data.items():
            if groupSel != item:
                continue
            self._data[groupSel] = schedules
            
    def SaveStateToRedoStack(self):
        """ append current data to undo stack """
        groupIdx = self.groupList.GetFirstSelected()

        # create a copy of data
        data = {}
        for k,v in self._data.items():
            data[k] = dict(v)

        state = {"data": data, "groupIdx": groupIdx}
        self._redoStack.append(state)

        self.WriteData()

    def SaveStateToUndoStack(self):
        """ append current data to undo stack """
        return
        groupIdx = self.groupList.GetFirstSelected()

        # create a copy of data
        data = {}
        for k,v in self._data.items():
            data[k] = dict(v)

        state = {"data": data,
                 "groupIdx": groupIdx}

        self._undoStack.append(state)

        self.WriteData()
    
    def SetGroupTree(self, data):
        """ set the group list tree """
        for idx in sorted([int(x) for x in data.keys()]):
            item = self.groupList.AppendItemToRoot(data[str(idx)]["columns"]["0"])
            self.groupList.CheckItem(item, data[str(idx)]["checked"])
            self._data[item] = data[str(idx)]["schedules"]
        self.groupList.UnselectAll()
        
    def SetScheduleTree(self, data):
        """ set the schedule list tree """
        self.schedList.SetTree(data)

    def SetStatusBar(self, event=None):
        """ update status bar when selecting a tree item on sequence"""
        selection = self.schedList.GetSelection()
        status = self.schedList.GetItemText(selection)
        print( status )
        self.GetTopLevelParent().SetStatusText(status)

        if event:
            event.Skip()     

    def ShowAboutDialog(self):
        if not self._aboutDialog:
            self._aboutDialog = AboutDialog(self)
            self._aboutDialog.Bind(wx.EVT_CLOSE, self.OnAboutDialogClose)
        self._aboutDialog.Show()    
            
    def ShowAddGroupDialog(self):   
        m = "Group Name:"
        
        # find unique group name
        i = 1
        b = "group_"
        uid = b + str(i)
        groupNames = self.GetGroupNames()
        while uid in groupNames:
            i += 1
            uid = b + str(i)
                
        while True:            
            dlg = wx.TextEntryDialog(self, message=m, caption="Add Group", value=uid)
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                return
            elif dlg.GetValue() in groupNames:
                m = "Group Name: ('{0}' already exists)".format(dlg.GetValue())
                continue    
            elif dlg.GetValue() == "":
                m = "Group Name: (Name cannot be empty)"
                continue 
            elif not dlg.GetValue().replace("_","").isalnum():
                m = "Group Name: (Name can only contain 0-9, A-Z. Underscores allowed)"
                continue

            self.SaveStateToUndoStack()
            newName = dlg.GetValue()
            newItem = self.groupList.AppendItemToRoot(newName)
            self.schedList.DeleteAllItems()

            self._data[newItem] = []
            self.WriteData()

            self.groupList.Select(newItem)
            self.groupList.SetFocus()

            self._redoStack = []
            return
            
    def ShowAddScheduleDialog(self):   
    
        # find unique schedule name
        i = 1
        b = "schedule_"
        uid = b + str(i)
        schedNames = self.GetScheduleNames()
        while uid in schedNames:
            i += 1
            uid = b + str(i)
                       
        dlg = dialogs.schedule.AddSchedule(self, blacklist=schedNames)
        dlg.SetScheduleName(uid)
        ret = dlg.ShowModal()
        if ret == wx.ID_CANCEL:
            return
            
        self.SaveStateToUndoStack()

        newName, newValue = dlg.GetValue()
        newItem = self.schedList.AppendItemToRoot(newName + DELIMITER + newValue)

        self.schedList.Select(newItem)
        self.schedList.CheckItem(newItem)
        self.schedList.Expand(newItem)
        self.schedList.SetFocus()
        self.UpdateScheduleToolbar()
        
        self.SaveScheduleTreeToData()
        
    def ShowCheckForUpdatesDialog(self):
        message = "Not yet implemented"
        dlg = wx.MessageDialog(self,
                               message,
                               caption="Checking for updates...")
        dlg.ShowModal()
        
    def ShowImportDialog(self):
        message = "Not yet implemented"
        dlg = wx.MessageDialog(self,
                               message,
                               caption="Import Schedule File")
        dlg.ShowModal()
        
    def ShowRemoveGroupDialog(self):
        groupIdx = self.GetGroupListIndex(self.groupList.GetSelection())
        if groupIdx is None:
            return
                    
        itemText = self.groupList.GetItemText(groupIdx)
        dlg = wx.MessageDialog(self, 
                               "Confirm delete group '{0}'?".format(itemText), 
                               "Delete Group",
                               style=wx.YES_NO)
        if dlg.ShowModal() == wx.ID_NO:
            return
            
        self.SaveStateToUndoStack()

        self.schedList.DeleteAllItems()
        self.groupList.DeleteItem(groupIdx)
        del self._data[groupIdx]
        
        self.toolbar.EnableTool(wx.ID_REMOVE, False)
        self._redoStack = []
        self.WriteData()
        
    def ShowSettingsDialog(self):
        try:
            self._settingsDialog.Show()
        except:
            self._settingsDialog = SettingsFrame(self)
            self._settingsDialog.Show()
            
    def ToggleScheduleSelection(self):
        selection = self.schedList.GetSelection()
        checked = self.schedList.GetCheckedState(selection)
        if checked == 1:
            self.schedList.UncheckItem(selection)
        else:
            self.schedList.CheckItem(selection)

        self.SaveStateToUndoStack()
            
    def UpdateScheduleToolbar(self):
        selection = self.schedList.GetSelection()
        if not selection.IsOk():
            for label, btn in self.schedBtns.items():
                if label == "Add Schedule":
                    continue
                btn.Disable()
            return
            
        self.schedBtns["Edit"].Enable()
        self.schedBtns["Toggle"].Enable()
        self.schedBtns["Delete"].Enable()
         
        if self.schedList.GetNextSibling(selection).IsOk():   
            self.schedBtns["Down"].Enable()
        else:
            self.schedBtns["Down"].Disable()
            
        parent = self.schedList.GetItemParent(selection)    
        if self.schedList.GetFirstChild(parent) != selection:   
            self.schedBtns["Up"].Enable()
        else:
            self.schedBtns["Up"].Disable()
            
    def UpdateTitlebar(self):
        try:
            _, name = os.path.split(self._appConfig["currentFile"])
            self.SetTitle("{0} - {1} {2}".format(name, __title__, __version__))
        except:
            self.SetTitle("{0} {1}".format(__title__, __version__))
            
    def WriteData(self):
        return
        """ write changes to data file"""
        logging.info("data: %s" % str(self._data))

        with open("schedules.json", 'w') as file:
            json.dump(self._data, file, sort_keys=True, indent=2)

if __name__ == "__main__":
    app = wx.App()
    Main()
    app.MainLoop()