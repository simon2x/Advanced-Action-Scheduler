#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) <2017> <Advanced Action Scheduler>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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

import base

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
             "KillProcess",
             "IfWindowOpen",
             "IfWindowNotOpen",
             "MouseClickAbsolute",
             "MouseClickRelative",
             "OpenURL",
             "Power",
             "StopSchedule",
             "StartSchedule",
             "SwitchWindow"]
             
class Main(wx.Frame):

    def __init__(self):

        self._title = "Advanced Action Scheduler 0.1"

        wx.Frame.__init__(self,
                          parent=None,
                          title=self._title)

        self._data = {}
        self._menus = {}
        self._redo_stack = []
        self._undo_stack = []
        self._schedmgr = schedulemanager.Manager(self)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        #-----
        self.CreateMenu()
        self.CreateToolbar()
        self.CreateStatusBar()

        #-----
        self.splitter = wx.SplitterWindow(self)

        leftpanel = wx.Panel(self.splitter)
        leftsizer = wx.BoxSizer(wx.VERTICAL)

        self.groupList = base.TreeListCtrl(leftpanel)
        # self.groupList.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.OnGroupItemSelected)
        self.groupList.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.OnGroupItemSelected)
        self.groupList.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.OnGroupItemChecked)
        self.groupList.AppendColumn("Group")
        self.groupList_root = self.groupList.GetRootItem()

        leftsizer.Add(self.groupList, 1, wx.ALL|wx.EXPAND, 5)
        leftpanel.SetSizer(leftsizer)

        # ----- rhs layout -----

        nbpanel = wx.Panel(self.splitter)
        self.notebook = wx.Notebook(nbpanel)
        nbsizer = wx.BoxSizer(wx.VERTICAL)
        nbsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 2)

        # the schedule panel/tab page
        schedpanel = wx.Panel(self.notebook)
        schedsizer = wx.BoxSizer(wx.VERTICAL)

        # -----
        hsizer_functions = wx.WrapSizer(wx.HORIZONTAL)
        for label in ["Add Schedule", "Up", "Down", "Edit", "Toggle", "Delete"]:
            btn = wx.Button(schedpanel, label=label, size=(-1, -1), style=wx.BU_EXACTFIT|wx.BU_NOTEXT)
            img = wx.Image("icons/{0}.png".format(label.lower().replace(" ", "")))
            img = img.Rescale(32,32, wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img)
            if label == "Edit":
                btn.Bind(wx.EVT_BUTTON, self.OnEdit)
            else:
                btn.Bind(wx.EVT_BUTTON, self.OnButton)
            if label in ["Delete"]:
                hsizer_functions.AddStretchSpacer()

            btn.SetBitmap(bmp)

            tooltip = wx.ToolTip(label)
            btn.SetToolTip(tooltip)
            hsizer_functions.Add(btn, 0, wx.ALL|wx.EXPAND, 2)
        schedsizer.Add(hsizer_functions, 0, wx.ALL|wx.EXPAND, 2)

        schedsizer.Add(wx.StaticLine(schedpanel), 0, wx.ALL|wx.EXPAND, 2)

        # -----
        hsizer_functions2 = wx.BoxSizer(wx.HORIZONTAL)

        self.cbox_functions = wx.ComboBox(schedpanel, style=wx.CB_READONLY, choices=FUNCTIONS)
        self.cbox_functions.SetSelection(0)
        self.cbox_functions.Bind(wx.EVT_COMBOBOX, self.OnComboboxFunction)

        btn_addfn = wx.Button(schedpanel, label="Add Function", size=(-1, -1))
        btn_addfn.Bind(wx.EVT_BUTTON, self.OnButton)

        hsizer_functions2.Add(self.cbox_functions, 0, wx.ALL|wx.CENTRE, 5)
        hsizer_functions2.Add(btn_addfn, 0, wx.ALL|wx.CENTRE, 5)

        schedsizer.Add(hsizer_functions2, 0, wx.ALL, 0)

        # schedsizer.Add(wx.StaticLine(schedpanel), 0, wx.ALL|wx.EXPAND, 0)

        # -----

        self.splitter2 = wx.SplitterWindow(schedpanel)

        self.schedList = base.TreeListCtrl(self.splitter2, style=wx.dataview.TL_CHECKBOX)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.OnScheduleTreeActivated)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.OnScheduleTreeSelectionChanged)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.OnScheduleTreeItemChecked)
        self.schedList.AppendColumn("Schedule")

        infopanel = wx.Panel(self.splitter2)
        infopanelsizer = wx.BoxSizer(wx.VERTICAL)
        self.info_sched = wx.TextCtrl(infopanel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH)

        infopanelsizer.Add(self.info_sched, 1, wx.ALL|wx.EXPAND, 0)
        infopanel.SetSizer(infopanelsizer)

        self.splitter2.SplitHorizontally(self.schedList, infopanel)
        self.splitter2.SetSashGravity(0.8)

        schedsizer.Add(self.splitter2, 1, wx.ALL|wx.EXPAND, 5)
        schedpanel.SetSizer(schedsizer)

        # the schedule manager panel/tab page
        mgrpanel = wx.Panel(self.notebook)
        mgrsizer = wx.BoxSizer(wx.VERTICAL)
        mgrpanel.SetSizer(mgrsizer)

        mgrhsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.chkboxes = {}
        for lbl in ["All","Schedules","Actions","Errors"]:
            chkbox = wx.CheckBox(mgrpanel, label=lbl)
            self.chkboxes[lbl] = chkbox
            mgrhsizer.Add(chkbox, 0, wx.ALL, 5)
        self.chkboxes["All"].SetValue(True)
        mgrsizer.Add(mgrhsizer, 0, wx.ALL, 0)

        self.schedlog = base.BaseList(mgrpanel)
        self.schedlog.InsertColumn(0, "#")
        self.schedlog.InsertColumn(1, "Time")
        self.schedlog.InsertColumn(2, "Message")
        mgrsizer.Add(self.schedlog, 1, wx.ALL|wx.EXPAND, 0)

        self.notebook.AddPage(schedpanel, "Schedules")
        self.notebook.AddPage(mgrpanel, "Manager")

        nbpanel.SetSizer(nbsizer)

        self.splitter.SplitVertically(leftpanel, nbpanel)
        self.splitter.SetSashGravity(0.2)

        self.SetMinSize((700, 600))
        self.SetSize((700, 600))

        #-----
        self.Show()

        #load settings
        try:
            with open("schedules2.json", 'r') as file:
                fileData = json.load(file)

            self.SetGroupTree(fileData)
            # for k,v in self._data.items():
                # name = self._data[k]["name"]
                # item = self.groupList.AppendItem(self.groupList_root, name)
                # self.groupList.SetItemData(item, k)
                # checked = v["checked"]
                # if checked == 1:
                    # self.groupList.CheckItem(item)

            file.close()
        except FileNotFoundError:
            logging.info("FileNotFoundError: creating new schedules file")
            with open("schedules.json", 'w') as file:
                pass

        except json.JSONDecodeError:
            logging.info("JSONDecodeError: creating new schedules file")
            with open("schedules.json", 'w') as file:
                pass

        self.groupList.Select(self.groupList.GetFirstItem())

    def AppendLogMessage(self, message):
        """ append log message to schedule messenger list """
        i = self.schedlog.GetItemCount()
        self.schedlog.Append([str(i)] + message)

    def CreateMenu(self):
        menubar = wx.MenuBar()

        menu_file = wx.Menu()
        file_menus = [("New", "New Schedule File"),
                      ("Open...", "Open Schedule File"),
                      ("Import", "Import Schedule File"),
                      ("Export", "Export Schedule File"),
                      ("Preferences", "Open Preferences..."),
                      ("Exit", "Exit Program")]
        for item, help_str in file_menus:
            self._menus[item] = menu_file.Append(wx.ID_ANY, item, help_str)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])

            if item == "Preferences":
                menu_file.AppendSeparator()

        menu_help = wx.Menu()
        help_menus = [("Check for updates", "Check for updates (Not Yet Implemented)"),
                      ("About", "Import Images From Folder")]
        for item, help_str in help_menus:
            self._menus[item] = menu_help.Append(wx.ID_ANY, item, help_str)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])

        menubar.Append(menu_file, "&File")
        menubar.Append(menu_help, "&Help")

        self.SetMenuBar(menubar)

    def CreateToolbar(self):
        # toolbar = wx.ToolBar(self, style=wx.TB_TEXT|wx.TB_FLAT)
        # toolbar = wx.ToolBar(self, style=wx.TB_TEXT)
        toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        # toolbar.AddTool(wx.ID _ANY, "t")#,  wx.BitmapFromBuffer(wx.ART_FILE_OPEN))
        toolbar.SetToolBitmapSize((48,48))
        # toolbar.SetToolBitmapSize((48,48))
        toolbar.SetBackgroundColour("white")
        for label, help, state, wxId in [  
            ("Save", "Save", True, wx.ID_SAVE),
            ("Add Group", "Add Group", True, wx.ID_ADD),
            ("Remove Group", "Remove Selected Group", False, wx.ID_REMOVE),
            ("Undo", "Undo", False, wx.ID_UNDO),
            ("Redo", "Redo", False, wx.ID_REDO),
            ("Enable Schedule Manager", "Enable Schedule Manager", True, wx.ID_ANY),
            ("Settings", "Settings", True, wx.ID_ANY)]:

            try:
                img = wx.Image("icons/{0}.png".format(label.lower().replace(" ", "")))
                img.Rescale(48,48, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
                tool = toolbar.AddTool(wxId, label=label, bitmap=bmp, shortHelp=help)
            except:
                bmp = wx.Bitmap(48,48)
                tool = toolbar.AddTool(wxId, label=label, bitmap=bmp, shortHelp=help)
            self.Bind(wx.EVT_TOOL, self.OnToolBar, tool)
            
            tool.Enable(state)
            
            if label == "Save":
                toolbar.AddSeparator()  
            elif label == "Redo":
                toolbar.AddSeparator()
            elif label == "Enable Schedule Manager":
                toolbar.AddStretchableSpace()

        toolbar.Realize()
        self.toolbar = toolbar
        self.SetToolBar(toolbar)

    def DoRedo(self):
        print(self._redo_stack)
        # can we redo?
        try:
            state = self._redo_stack[-1]
            # self._undo_stack.append(state)
            del self._redo_stack[-1]
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
                state = self._undo_stack[-1]
                # self._redo_stack.append(state)
                del self._undo_stack[-1]
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
    
    def DisableScheduleManager(self):
        tool = e.FindById(id)
        tool.SetLabel("Disable Schedule Manager")
        e.SetToolShortHelp(id, "Disable Schedule Manager")

        img = wx.Image("icons/disableschedulemanager.png")
        img = img.Rescale(48,48, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.Bitmap(img)
        e.SetToolNormalBitmap(id, bmp)

        self._schedmgr.SetSchedules(self._data)
        self._schedmgr.Start()

        # switch to the manager when schedules are started
        self.notebook.SetSelection(1)
        
    def EnableScheduleManager(self):
        tool = e.FindById(id)
        tool.SetLabel("Enable Schedule Manager")
        e.SetToolShortHelp(id, "Enable Schedule Manager")

        img = wx.Image("icons/enableschedulemanager.png")
        img = img.Rescale(48,48, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.Bitmap(img)
        e.SetToolNormalBitmap(id, bmp)

        self._schedmgr.Stop()
        
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

    def GetGroupListIndex(self, item):
        """ only way to finding existing item in self._data by comparing TreeListItem """
        for dataItem in self._data.keys():
            if dataItem == item:
                return dataItem
        return -1

    def GetScheduleNames(self):
        """ return toplevel items"""
        schedules = []
        item = self.schedList.GetFirstItem()
        while item.IsOk():
            if self.schedList.GetCheckedState(item) == 1:
                schedules.append(self.schedList.GetItemText(item, 0).split(DELIMITER)[0])
            item = self.schedList.GetNextSibling(item)

        return schedules

    def GetSchedulePreviousSibling(self, item):
        """ get previous sibling of argument item """

        tree = self.schedList
        tree.SetItemData(item, True)

        # iterate through items until item data returns True
        parent = tree.GetItemParent(item)
        sibling = tree.GetFirstChild(parent)
        item_data = tree.GetItemData(sibling)
        # already first child, then return None
        if item_data:
            tree.SetItemData(item, None)
            return None

        while not item_data:
            next = tree.GetNextSibling(sibling)
            item_data = tree.GetItemData(next)
            if item_data:
                break
            sibling = next

        previous = sibling
        tree.SetItemData(item, None)

        return previous
    
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

    def GetScheduleTree(self):
        """ retrieve tree structure, used for saving data """
        data = self.schedList.GetTree()
        return data
    
    def GetScheduleSubTree(self, item):
        """ return the sub tree of schedule item """
        tree = self.schedList

        selection = item

        # we stop when item depth is the same as the selected item
        # i.e. a sibling
        selected_depth = self.GetItemDepth(item)

        data = {}
        count = tree.GetColumnCount()
        depth = selected_depth
        index = "0"

        while item.IsOk():

            d = self.GetItemDepth(item)

            # have we reached sibling
            if selected_depth == d and "0" in data:
                break

            # selected item is first item
            if d == selected_depth:
                pass

            # sibling of previous item
            elif d == depth:
                next = int(index[-1]) + 1
                del index[-1]
                index.append(str(next))
                index = ",".join(index)

            # a child of previous item
            elif d > depth:
                index += ",0"

            # sibling of parent
            elif d < depth:
                index = index.split(",")[:depth]
                # increment last element
                next = int(index[-1]) + 1
                del index[-1]
                index.append(str(next))
                index = ",".join(index)

            # print(index)
            depth = d
            item_data = {}
            item_data["data"] = tree.GetItemText(item, 0)
            item_data["checked"] = tree.GetCheckedState(item)
            item_data["expanded"] = tree.IsExpanded(item)
            item_data["selected"] = tree.IsSelected(item)

            data[index] = item_data

            item = tree.GetNextItem(item)

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
    
    def InsertSubTree(self, previous, data):
        """ insert sub tree after previous item """

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
                parent = tree.GetItemParent(previous)
                item = tree.InsertItem(parent, previous, value["0"])
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
    
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()

        if label == "Add Function":
            self.OnComboboxFunction()

        elif label == "Add Schedule":
            self.ShowAddScheduleDialog()
                
        elif label == "Delete":
            self.ShowDeleteScheduleItemDialog()            

        elif label == "Toggle":
            selection = self.schedList.GetSelection()
            checked = self.schedList.GetCheckedState(selection)
            if checked == 1:
                self.schedList.UncheckItem(selection)
            else:
                self.schedList.CheckItem(selection)

            self.SaveStateToUndoStack()

            self.GetScheduleTreeAndWriteData()

        elif label == "Up":
            """ move then item up by moving the previous item down """

            # valid item selection?
            selection = self.schedList.GetSelection()
            if not selection.IsOk():
                return

            # can item the moved up?
            previous = self.GetSchedulePreviousSibling(selection)
            if not previous:
                logging.info("previous item is not OK. selection already at the top?")
                return

            self.SaveStateToUndoStack()

            subtree = self.GetScheduleSubTree(previous)
            self.schedList.DeleteItem(previous)
            self.InsertSubTree(selection, subtree)

            self.GetScheduleTreeAndWriteData()

        elif label == "Down":

            # valid item selection?
            selection = self.schedList.GetSelection()
            if not selection.IsOk():
                return

            # can item the moved down?
            next = self.schedList.GetNextSibling(selection)
            if not next.IsOk():
                return

            self.SaveStateToUndoStack()

            subtree = self.GetScheduleSubTree(selection)
            self.schedList.DeleteItem(selection)
            self.InsertSubTree(next, subtree)

            self.GetScheduleTreeAndWriteData()

        # finally, clear the redo stack
        self._redo_stack = []

    def OnClose(self, event):
        # save data before exiting
        self.WriteData()
        event.Skip()

    def OnComboboxFunction(self, event=None):
        """ selecting a combobox option automatically raises a corresponding dialog """

        schedSel = self.schedList.GetSelection()
        if not schedSel.IsOk():
            return
            
        index = self.cbox_functions.GetSelection()
        if index == -1:
            return
        label = self.cbox_functions.GetStringSelection()
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
        for n, (j, k) in enumerate(self._data[groupSel]):
            if j == schedSelIdx:
                break 
                
        self._data[groupSel].insert(n+1, (idx, {'columns': {"0": value}, 
                                              'expanded': False, 
                                              'selected': True, 
                                              'checked': 1}))
        
        self.schedList.Select(newItem)
        self.schedList.CheckItem(newItem)
        self.schedList.Expand(newItem)
        self.schedList.SetFocus()
        
    def OnEdit(self, event):
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
            dlg = self.GetDialog(newName)
            dlg.SetValue(params)
            if dlg.ShowModal() != wx.ID_OK:
                return
            value = dlg.GetValue()
            value = newName + DELIMITER + value
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
        self.info_sched.SetValue(value)    

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
        self.schedList.DeleteAllItems()
        groupSel = self.groupList.GetSelection()
        for item, data in self._data.items():
            if groupSel != item:
                continue
            self.toolbar.FindById(wx.ID_REMOVE).Enable(True)  
            self.toolbar.Realize()
            self.SetScheduleTree(data)
            return
        
        self.toolbar.FindById(wx.ID_REMOVE).Enable(False)
        self.toolbar.Realize()
        # # click the information text
        # self.info_sched.SetValue("")

    def OnListItemActivated(self, event):
        self.OnAddFunction()

    def OnMenu(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        label = e.GetLabel(id)

        if label == "About":
            message = ("Created by Simon Wu\n"
                     + "Licensed under the terms of the MIT Licence\n")


            dlg = wx.MessageDialog(self,
                                   message,
                                   caption=self._title)
            dlg.ShowModal()

        elif label == "Check for updates":
            message = "not yet implemented"

            dlg = wx.MessageDialog(self,
                                   message,
                                   caption="Checking for updates...")

            dlg.ShowModal()

        elif label == "Exit":
            self.Close()

        elif label == "Export":
            self.SaveFileAs()

        elif label == "Import":
            self.SaveFile()

        elif label == "New":
            self.CreateNewEditor()

        elif label == "Open...":
            self.OpenFile()

    def OnScheduleTreeActivated(self, event):
        e = event.GetEventObject()

    def OnScheduleTreeSelectionChanged(self, event=None):
        """ update the schedule item information """

        selection = self.schedList.GetSelection()

        # logging.info("Schedule tree items selected: %s" % str(selection))
        try:
            text = self.schedList.GetItemText(selection)
            self.info_sched.SetValue(text)
        except:
            self.info_sched.SetValue("")

    def OnScheduleTreeItemChecked(self, event):
        """ here we just save the new tree """
        self.GetScheduleTreeAndWriteData()

    def OnToolBar(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        tool = e.FindById(id)
        label = tool.GetLabel()
        logging.info("OnToolBar event: %s" % label)

        if label == "Add Group":
            self.ShowAddGroupDialog()   
        elif label == "Disable Schedule Manager":
            self.DisableScheduleManager()
        elif label == "Enable Schedule Manager":
            self.EnableScheduleManager()
        elif label == "Remove Group":
            self.ShowRemoveGroupDialog()        
        elif label == "Redo":
            self.DoRedo()
        elif label == "Save":
            self.SaveData()    
        elif label == "Undo":
            self.DoUndo()
        
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
        print("saving data")
        
    def SaveStateToRedoStack(self):
        """ append current data to undo stack """
        groupIdx = self.groupList.GetFirstSelected()

        # create a copy of data
        data = {}
        for k,v in self._data.items():
            data[k] = dict(v)

        state = {"data": data, "groupIdx": groupIdx}
        self._redo_stack.append(state)

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

        self._undo_stack.append(state)

        self.WriteData()
    
    def SetGroupTree(self, data):
        """ set the group list tree """
        for idx in sorted([int(x) for x in data.keys()]):
            item = self.groupList.AppendItemToRoot(data[str(idx)]["columns"]["0"])
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

            self._redo_stack = []
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

        schedules = self.GetScheduleTree()
        groupSel = self.groupList.GetSelection()
        for item, data in self._data.items():
            if groupSel != item:
                continue
            self._data[groupSel] = schedules
                
    def ShowDeleteScheduleItemDialog(self):   
        index = self.schedList.GetSelection()
        if not index.IsOk():
            return

        dlg = wx.MessageDialog(self, 
                               "Confirm delete", 
                               "Delete schedule list item?",
                               style=wx.YES_NO)
        if dlg.ShowModal() == wx.ID_NO:
            return

        self.SaveStateToUndoStack()

        self.schedList.DeleteItem(self.schedList.GetSelection())
        self.GetScheduleTreeAndWriteData()

        # self.OnScheduleTreeSelectionChanged()
            
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

        self._redo_stack = []
        self.WriteData()
        
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