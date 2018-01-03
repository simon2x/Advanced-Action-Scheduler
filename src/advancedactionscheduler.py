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
        self.splitter = wx.SplitterWindow(self)
        
        leftpanel = wx.Panel(self.splitter)   
        leftsizer = wx.BoxSizer(wx.VERTICAL)
            
        self.group_list = base.TreeListCtrl(leftpanel)
        # self.group_list.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.OnGroupItemSelected)
        self.group_list.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.OnGroupItemSelected)
        self.group_list.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.OnGroupItemChecked)        
        self.group_list.AppendColumn("Group")
        self.group_list_root = self.group_list.GetRootItem()
        
        leftsizer.Add(self.group_list, 1, wx.ALL|wx.EXPAND, 5)
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
        for label, art in [("Add Schedule", wx.ART_NEW),
                           ("Up", wx.ART_GO_UP),
                           ("Down", wx.ART_GO_DOWN),
                           ("Edit", wx.ART_REPORT_VIEW),
                           ("Toggle", wx.ART_LIST_VIEW),
                           ("Delete", wx.ART_MINUS)]:
            btn = wx.Button(schedpanel, label=label, size=(-1, -1), style=wx.BU_EXACTFIT|wx.BU_NOTEXT)
            bmp = wx.ArtProvider().GetBitmap(art)
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
                      
        self.sched_list = base.TreeListCtrl(self.splitter2, style=wx.dataview.TL_CHECKBOX)
        self.sched_list.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.OnScheduleTreeActivated)
        self.sched_list.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.OnScheduleTreeSelectionChanged)
        self.sched_list.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.OnScheduleTreeItemChecked)        
        self.sched_list.AppendColumn("Schedule")
        
        infopanel = wx.Panel(self.splitter2)
        infopanelsizer = wx.BoxSizer(wx.VERTICAL)
        self.info_sched = wx.TextCtrl(infopanel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH)
        
        infopanelsizer.Add(self.info_sched, 1, wx.ALL|wx.EXPAND, 0)
        infopanel.SetSizer(infopanelsizer)        
        
        self.splitter2.SplitHorizontally(self.sched_list, infopanel)
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
        self.CreateMenu()
        self.CreateToolbar()
        self.CreateStatusBar()
        
        #-----
        self.Show()       
        
        #load settings
        try:
            with open("schedules.json", 'r') as file: 
                self._data = json.load(file)
            
            self.SetGroupTree(self._data)
            # for k,v in self._data.items():
                # name = self._data[k]["name"]
                # item = self.group_list.AppendItem(self.group_list_root, name)
                # self.group_list.SetItemData(item, k)
                # checked = v["checked"]
                # if checked == 1:
                    # self.group_list.CheckItem(item)
            
            file.close()
        except FileNotFoundError:    
            logging.info("FileNotFoundError: creating new schedules file")
            with open("schedules.json", 'w') as file: 
                pass
            
        except json.JSONDecodeError:    
            logging.info("JSONDecodeError: creating new schedules file")
            with open("schedules.json", 'w') as file: 
                pass
        
        # tree.Select(tree.GetFirstItem())
            
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
        for label, help, art in [
            ("Add Group", "Add Group", wx.ART_NEW),
            ("Remove Group", "Remove Selected Group", wx.ART_MINUS),
            ("Undo", "Undo", wx.ART_UNDO),
            ("Redo", "Redo", wx.ART_REDO),
            ("Enable", "Enable Schedule Manager", wx.ART_TICK_MARK)]:
            
            try:
                # bmp = theme.GetBitmap(icon, 48,48)  
                # bmp = theme.GetBitmap(icon, 24,24)  
                bmp = wx.ArtProvider.GetBitmap(art)
                tool = toolbar.AddTool(wx.ID_ANY, label=label, bitmap=bmp, shortHelp=help)
            except:
                bmp = wx.Bitmap(24,24)            
                tool = toolbar.AddTool(wx.ID_ANY, label=label, bitmap=bmp, shortHelp=help)
            self.Bind(wx.EVT_TOOL, self.OnToolBar, tool)
            
            if label == "Redo":
                toolbar.AddSeparator()
                toolbar.AddStretchableSpace()
                toolbar.AddSeparator()
            
        toolbar.Realize()
        self.SetToolBar(toolbar)
          
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
        
    def GetGroupListIndex(self):
        pass
        
    def GetScheduleList(self):
        """ return toplevel items"""
        tree = self.sched_list
        
        schedules = []        
        item = self.sched_list.GetFirstItem()
        while item.IsOk():
            if tree.GetCheckedState(item) == 1:
                schedules.append(tree.GetItemText(item, 0))           
            item = tree.GetNextSibling(item)
            
        return schedules
    
    def GetSchedulePreviousSibling(self, item):
        """ get previous sibling of argument item """
        
        tree = self.sched_list
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
     
    def GetScheduleSubTree(self, item):
        """ return the sub tree of schedule item """
        tree = self.sched_list
        
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
    
    def GetGroupTree(self):
        """ retrieve tree structure, used for saving data """
        data = self.group_list.GetTree()
        return data
        
    def GetScheduleTree(self):
        """ retrieve tree structure, used for saving data """
        data = self.sched_list.GetTree()
        return data
   
    def GetTopLevel(self):
        """ return sequence tree top-level """
        try:
            selection = item = self.sched_list.GetSelection()
        except:
            return False
        
        if not selection.IsOk():    
            return False
            
        text = self.sched_list.GetItemText(selection)
      
        # root = self.sched_list.GetRootItem()
        # parent = self.sched_list.GetItemParent(selection)
        
        parents = [item]
        # get item parents
        while self.sched_list.GetItemParent(item).IsOk():            
            parent = self.sched_list.GetItemParent(item)     
            parents.append(parent)
            item = parent
            
        parents = [self.sched_list.GetItemText(itm) for itm in parents if itm.IsOk()]
        print( parents )
        return parents[-2]
        
    def AppendLogMessage(self, message):
        """ append log message to schedule messenger list """
        i = self.schedlog.GetItemCount()
        self.schedlog.Append([str(i)] + message)
    
    def SetGroupTree(self, data):
        """ set the group list tree """  
        root = self.group_list_root
        for idx in sorted([int(x) for x in data.keys()]):            
            item = self.group_list.AppendItemToRoot(data[str(idx)]["columns"]["0"])        
        
    def SetScheduleTree(self, data):
        """ set the schedule list tree """  
        self.sched_list.SetTree(data)
        
    def SetStatusBar(self, event=None):
        """ update status bar when selecting a tree item on sequence"""
        selection = self.sched_list.GetSelection()
        status = self.sched_list.GetItemText(selection)
        print( status )
        self.GetTopLevelParent().SetStatusText(status)
       
        if event:
            event.Skip()
            
    def InsertSubTree(self, previous, data):        
        """ insert sub tree after previous item """        
        
        items = {}  
        expanded_items = []
        tree = self.sched_list
        
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
            
    def PrependSubTree(self, previous, data):        
        """ insert sub tree before item """        
        
        items = {}  
        expanded_items = []
        tree = self.sched_list
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
    
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        
        if label == "Add Function":
            self.OnComboboxFunction()
                    
        elif label == "Add Schedule":
            dlg = dialogs.schedule.AddSchedule(self)
           
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                return
            
            self.SaveStateToUndoStack()
                            
            name, value = dlg.GetValue()
            newitem = self.sched_list.AppendItemToRoot(name + DELIMITER + value)
            
            self.sched_list.Select(newitem)
            self.sched_list.CheckItem(newitem)
            self.sched_list.Expand(newitem)
            self.sched_list.SetFocus()
            
            schedules = self.GetScheduleTree()
            g_index = self.group_list.GetSelection()
            self._data[g_index]["schedules"] = schedules
            self.WriteData()
    
        elif label == "Delete":
            
            index = self.sched_list.GetSelection()
            if not index.IsOk():
                return
            
            dlg = base.ConfirmDialog(self,
                                     "Confirm delete",
                                     "Delete schedule list item?")
            if dlg.ShowModal() == wx.ID_NO:
                return
                
            self.SaveStateToUndoStack()
                
            self.sched_list.DeleteItem(self.sched_list.GetSelection())            
            self.GetScheduleTreeAndWriteData()
            
            # self.OnScheduleTreeSelectionChanged()
            
        elif label == "Toggle":
            selection = self.sched_list.GetSelection()
            checked = self.sched_list.GetCheckedState(selection)
            if checked == 1:
                self.sched_list.UncheckItem(selection)
            else:
                self.sched_list.CheckItem(selection)  
            
            self.SaveStateToUndoStack()
            
            self.GetScheduleTreeAndWriteData()
            
        elif label == "Up":
            """ move then item up by moving the previous item down """
            
            # valid item selection?
            selection = self.sched_list.GetSelection()             
            if not selection.IsOk():
                return
            
            # can item the moved up?
            previous = self.GetSchedulePreviousSibling(selection)
            if not previous:
                logging.info("previous item is not OK. selection already at the top?")
                return
            
            self.SaveStateToUndoStack()
            
            subtree = self.GetScheduleSubTree(previous)
            self.sched_list.DeleteItem(previous)
            self.InsertSubTree(selection, subtree)
            
            self.GetScheduleTreeAndWriteData()
        
        elif label == "Down":
        
            # valid item selection?
            selection = self.sched_list.GetSelection()             
            if not selection.IsOk():
                return
            
            # can item the moved down?
            next = self.sched_list.GetNextSibling(selection)
            if not next.IsOk():
                return
            
            self.SaveStateToUndoStack()
            
            subtree = self.GetScheduleSubTree(selection)
            self.sched_list.DeleteItem(selection)
            self.InsertSubTree(next, subtree) 

            self.GetScheduleTreeAndWriteData()
            
        # finally, clear the redo stack
        self._redo_stack = []
        
    def OnComboboxFunction(self, event=None):
        """ selecting a combobox option automatically raises a corresponding dialog """        
        
        index = self.cbox_functions.GetSelection()
        if index == -1:
            return
        label = self.cbox_functions.GetStringSelection()
        logging.info("OnComboboxFunction event: %s" % label)
        logging.debug(index)
        
        selection = self.sched_list.GetSelection()
        
        dlg = self.GetDialog(label)
        
        ret = dlg.ShowModal()
        if ret == wx.ID_CANCEL:
            return
        
        value = dlg.GetValue()
        newitem = self.sched_list.AppendItem(selection, label + DELIMITER + value)
        
        self.sched_list.Select(newitem)
        self.sched_list.CheckItem(newitem)
        self.sched_list.Expand(newitem)
        self.sched_list.SetFocus()
                
        self.GetScheduleTreeAndWriteData()
        
    def OnEdit(self, event):
        tree = self.sched_list
        selection = tree.GetSelection()
      
        item_text = self.sched_list.GetItemText(selection, 0)
        name, params = item_text.split(DELIMITER)
        params = make_tuple(params)
        params = {x:y for x,y in params}       
        params["name"] = name
            
        if selection == -1:
            logging.info("No item selected. Nothing to edit")
            return
       
        if self.GetItemDepth(selection) == 0:
            
            logging.info("Toplevel item selected. Item is a schedule")
            dlg = dialogs.schedule.AddSchedule(self)
            dlg.SetName(name)
            dlg.SetValue(params)
            if dlg.ShowModal() == wx.ID_OK:
                name, value = dlg.GetValue()
                value = name + DELIMITER + value
                tree.SetItemText(selection, 0, value)                
        
        else:
            dlg = self.GetDialog(name)
            dlg.SetValue(params)
            if dlg.ShowModal() == wx.ID_OK:
                value = dlg.GetValue()
                value = name + DELIMITER + value
                tree.SetItemText(selection, 0, value)
        
        # save tree to data
        schedules = self.GetScheduleTree()
        g_index = self.group_list.GetSelection()
        self._data[str(g_index)]["schedules"] = schedules
        
        # write changes to file
        self.WriteData()        
        
        self.sched_list.SetFocus()
        
        # updated information
        self.info_sched.SetValue(value)
        
    def OnGroupItemKeyDown(self, event):
        key = event.GetKeyCode()
        index = self.group_list.GetSelection()
        # if index == -1:
            # return
        print(key)    
        if key == wx.WXK_SPACE:
            self.group_list.CheckItem( index )            
    
    def OnGroupItemChecked(self, event):
        logging.info("OnGroupItemChecked")
        g_index = self.group_list.GetSelection()
        self._data[g_index]["checked"] = self.group_list.GetCheckedState(g_index)
        
    def OnGroupItemSelected(self, event):
        self.sched_list.DeleteAllItems()
        # update schedule list
        g_index = self.group_list.GetSelection()        
        
        data = self._data[str(g_index)]["schedules"]
        self.SetScheduleTree(data)
        
        # click the information text
        self.info_sched.SetValue("")
    
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
        
        selection = self.sched_list.GetSelection()
        
        # logging.info("Schedule tree items selected: %s" % str(selection))
        try:
            text = self.sched_list.GetItemText(selection)
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
            dlg = dialogs.groups.AddGroup(self)
           
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                return
            
            self.SaveStateToUndoStack()
            
            name = dlg.GetValue()
            
            newitem = self.group_list.AppendItemToRoot(name)
            self.sched_list.DeleteAllItems()
            
            group_tree = self.GetGroupTree()
            
            # we insert schedule tree into the relevant group item
            schedules = self.GetScheduleTree()
            self._data[newitem] = group_tree[newitem]
            self._data[newitem]["schedules"] = schedules
            
            self.WriteData()
            
            self.group_list.Select(newitem)
            # self.group_list.CheckItem(newitem)
                        
            self.group_list.SetFocus()            
            
            self._redo_stack = []
            
        elif label == "Remove Group":        
            g_index = self.group_list.GetSelection()
            if g_index == -1:
                return
                
            dlg = base.ConfirmDialog(self,
                                     "Confirm delete",
                                     "Delete group?")
            if dlg.ShowModal() == wx.ID_NO:
                return                      
            
            self.SaveStateToUndoStack()
            
            self.sched_list.DeleteAllItems()
            self.group_list.DeleteItem(g_index)
            del self._data[str(g_index)]
            
            new_data = {}
            count = 0
            for k in sorted(self._data.keys()):                
                new_data[str(count)] = self._data[k]
                count += 1
            
            self._redo_stack = []
            
            self._data = new_data
            self.WriteData()
            
            self.OnScheduleTreeSelectionChanged()
                
        elif label == "Undo":
        
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
            
            self.group_list.DeleteAllItems()
            self.sched_list.DeleteAllItems()
            
            for k,v in self._data.items():
                name = self._data[k]["name"]
                item = self.group_list.InsertItem(int(k), name)
                checked = v["checked"]
                if checked == "True":
                    self.group_list.CheckItem(item)
            
            self.group_list.Select(state["g_index"])            
            
            self.WriteData()
            
        elif label == "Redo":
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
            
            self.group_list.DeleteAllItems()
            self.sched_list.DeleteAllItems()
            
            for k,v in self._data.items():
                name = self._data[k]["name"]
                item = self.group_list.InsertItem(int(k), name)
                checked = v["checked"]
                if checked == "True":
                    self.group_list.CheckItem(item)
            
            self.group_list.Select(state["g_index"])
            
            self.WriteData()
            
        elif label == "Enable": 
            tool = e.FindById(id)
            tool.SetLabel("Disable")
            e.SetToolShortHelp(id, "Disable Schedule Manager")
            
            art = wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK)
            e.SetToolNormalBitmap(id, art)
                        
            self._schedmgr.SetSchedules(self._data)
            self._schedmgr.Start()    
            
            # switch to the manager when schedules are started
            self.notebook.SetSelection(1)
            
        elif label == "Disable":
            tool = e.FindById(id)
            tool.SetLabel("Enable")
            e.SetToolShortHelp(id, "Enable Schedule Manager")
            
            art = wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK)
            e.SetToolNormalBitmap(id, art)
            
            self._schedmgr.Stop()
    
    def GetScheduleTreeAndWriteData(self):
        # save tree to data
        #self.sched_list.DeleteAllItems()
        # update schedule list
        g_index = self.group_list.GetSelection()
        
        # checked = self.group_list.GetCheckedState(selection)
        
#        group_tree = self.group_list.GetTree()        
        schedules = self.sched_list.GetTree()  
        
#        self._data[g_index] = group_tree
        self._data[g_index]["schedules"] = schedules   
        print(self._data)
        # group_tree[g_index]["data"] = schedules        
        # self._d
        
        self.WriteData()
        
    def SaveStateToRedoStack(self):
        """ append current data to undo stack """
        g_index = self.group_list.GetFirstSelected()
        
        # create a copy of data
        data = {}
        for k,v in self._data.items():
            data[k] = dict(v)
            
        state = {"data": data,
                 "g_index": g_index}
                 
        self._redo_stack.append(state)        
        
        self.WriteData()
        
    def SaveStateToUndoStack(self):
        """ append current data to undo stack """
        return
        g_index = self.group_list.GetFirstSelected()
        
        # create a copy of data
        data = {}
        for k,v in self._data.items():
            data[k] = dict(v)
            
        state = {"data": data,
                 "g_index": g_index}
                 
        self._undo_stack.append(state)
        
        self.WriteData()
    
    def WriteData(self):
        """ write changes to data file"""
        logging.info("data: %s" % str(self._data))
       
        with open("schedules.json", 'w') as file: 
            json.dump(self._data, file, sort_keys=True, indent=4)
            
    def OnClose(self, event):
        # save data before exiting
        self.WriteData()
        event.Skip()
        
if __name__ == "__main__":
    app = wx.App()    
    Main()
    app.MainLoop()