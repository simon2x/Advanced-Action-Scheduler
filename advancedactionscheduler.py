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
from dialogs import *
import dialogs
import sys
import time
import wx
import theme
import os
import os.path
import subprocess
import schedulemanager
import wx.dataview #for TreeListCtrl
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub

import base

#----- logging -----#
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# create file handler which logs even debug messages
fh = logging.FileHandler('ssc.log')
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
         
        self._schedmgr = schedulemanager.Manager(self)
         
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        #-----
        self.splitter = wx.SplitterWindow(self)
        
        leftpanel = wx.Panel(self.splitter)   
        leftsizer = wx.BoxSizer(wx.VERTICAL)
        self.group_list = wx.ListCtrl(leftpanel, style=wx.LC_REPORT)
        self.group_list.InsertColumn(0, "Group")
        leftsizer.Add(self.group_list, 1, wx.ALL|wx.EXPAND, 0)
        leftpanel.SetSizer(leftsizer)
        
        panel = wx.Panel(self.splitter)   
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # -----
        hsizer_functions = wx.BoxSizer(wx.HORIZONTAL)
        self.function_list = wx.ComboBox(panel, style=wx.CB_READONLY, choices=FUNCTIONS)        
        btn = wx.Button(panel, label="Add Function", size=(-1, 24))
        btn.Bind(wx.EVT_BUTTON, self.OnAddFunction)
        
        hsizer_functions.Add(self.function_list, 0, wx.ALL|wx.ALIGN_CENTRE, 2)
        hsizer_functions.Add(btn, 0, wx.ALL|wx.ALIGN_CENTRE, 2)
        sizer.Add(hsizer_functions, 0, wx.ALL|wx.ALIGN_CENTRE, 0)
        
        sizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
        
        # -----
        # the bottom half
        hsizer_functions = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["New Schedule","Up","Down","Edit","Toggle","Delete"]:
            if label == "New Schedule":
                btn = wx.Button(panel, label=label, size=(-1, 24))
            else:
                btn = wx.Button(panel, label=label, size=(48, 24))
            if label == "Edit":
                btn.Bind(wx.EVT_BUTTON, self.OnEdit)
            else:
                btn.Bind(wx.EVT_BUTTON, self.OnButton)
            if label in ["Delete"]:
                hsizer_functions.AddStretchSpacer()
            hsizer_functions.Add(btn, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer_functions, 0, wx.ALL|wx.EXPAND, 0)
              
        self.bingo_list = wx.dataview.TreeListCtrl(panel, style=wx.dataview.TL_CHECKBOX)        
        self.bingo_list.AppendColumn("Schedule")
        sizer.Add(self.bingo_list, 1, wx.ALL|wx.EXPAND, 0)
        
        hsizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(panel, label="Enable", size=(-1, 24))
        btn.Bind(wx.EVT_BUTTON, self.OnEnable)
        hsizer_controls.AddStretchSpacer()
        hsizer_controls.Add(btn, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hsizer_controls, 0, wx.ALL|wx.EXPAND, 0)
        
        panel.SetSizer(sizer)        
        
        self.splitter.SplitVertically(leftpanel, panel)
        self.splitter.SetSashGravity(0.4)
        
        
        # self.SetSize((400, 600))
        
        #-----
        self.CreateStatusBar()
        
        #-----
        self.Show()       
        
        #load settings
        # try:
        with open("schedules.json", 'r') as file: 
            data = json.load(file)
        items = {}  
        expanded_items = []
        tree = self.bingo_list
        root = self.bingo_list.GetRootItem()
        for key in sorted(data.keys()):
            parent = key.split(",")[:-1]
            parent = ",".join(parent)
            if not parent:
                parent = root
            else:
                parent = items[parent]
                
            value = data[key]["data"]
            
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
            
        file.close()
        # except:             
            # pass
        
        tree.Select(tree.GetFirstItem())
        
#end __init__ def

    def GetItemDepth(self, item):
        """  backwards """
        tree = self.bingo_list
        
        depth = 0
        while tree.GetItemParent(item).IsOk():
            depth += 1 
            item = tree.GetItemParent(item)
        return depth - 1
            
    def GetTreeData(self):
        """ used for saving data """
        tree = self.bingo_list
        # root = tree.GetRootItem()
        
        item = tree.GetFirstItem()
        if not item.IsOk():
            event.Skip()
            return
            
        data = {}
        count = tree.GetColumnCount()
        row = 0
        depth = 0      
        index = "0"
        root = tree.GetItemParent(item)
        while item.IsOk():
            d = self.GetItemDepth(item)
            print(d)
            
            # the very first item (not root)
            if d == 0 and row == 0:
                index = "0"
                row += 1
                
            # a toplevel item (excluding first item)
            elif d == 0 and row != 0:  
                index = str(row)
                row += 1
                
            # depth unchanged, item is the next sibling of previous item
            elif d == depth:   
                index = index.split(",")[:-1] #chop off last level
                next = int(index[-1]) + 1
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
            
            print( index )
            depth = d  
            item_data = {}
            item_data["data"] = {col:tree.GetItemText(item, col) for col in range(count)}
            item_data["checked"] = tree.GetCheckedState(item)
            item_data["expanded"] = tree.IsExpanded(item)
            item_data["selected"] = tree.IsSelected(item)
            
            data[index] = item_data
            
            item = tree.GetNextItem(item)
        
        return data
        
    def GetTree(self):
        return self.bingo_list
        
    def OnEdit(self, event):
        tree = self.bingo_list
        selection = tree.GetSelection()
      
        item_text = self.bingo_list.GetItemText(selection, 0)
        name, params = item_text.split(DELIMITER)
        params = make_tuple(params)
        params = {x:y for x,y in params}       
        params["name"] = name
            
        if selection == -1:
            logging.info("no item selected")
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
                return
        
        else:
            dlg = self.OpenDialog(name)
            dlg.SetValue(params)
            if dlg.ShowModal() == wx.ID_OK:
                value = dlg.GetValue()
                value = name + DELIMITER + value
                tree.SetItemText(selection, 0, value)
                
        self.bingo_list.SetFocus()
                
#end OnEdit def           
    
    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        
        if label == "New Schedule":
            dlg = dialogs.schedule.AddSchedule(self)
           
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                return
                
            root = self.bingo_list.GetRootItem()
                
            name, value = dlg.GetValue()
            newitem = self.bingo_list.AppendItem(root, name + DELIMITER + value)
            
            self.bingo_list.Select(newitem)
            self.bingo_list.CheckItem(newitem)
            self.bingo_list.Expand(self.bingo_list.GetSelection())
            self.bingo_list.SetFocus()
     
        elif label == "Delete":
            self.bingo_list.DeleteItem(self.bingo_list.GetSelection())
        
    def GetScheduleList(self):
        """ return toplevel items"""
        tree = self.bingo_list
        
        schedules = []        
        item = self.bingo_list.GetFirstItem()
        while item.IsOk():
            if tree.GetCheckedState(item) == 1:
                schedules.append(tree.GetItemText(item, 0))           
            item = tree.GetNextSibling(item)
            
        return schedules
        
    def OnEnable(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        if label == "Enable":
            schedules = self.GetScheduleList()
            self._schedmgr.SetSchedules(schedules)
            self._schedmgr.Start()
            e.SetLabel("Disable")                        
        else:
            e.SetLabel("Enable")
            self._schedmgr.Stop()
        
    def OpenDialog(self, label, value=None):
        
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
        
    def OnAddFunction(self, event=None):
        index = self.function_list.GetFocusedItem()
        if index == -1:
            return
        label = self.function_list.GetItem(index).GetText()
        
        selection = self.bingo_list.GetSelection()
        if not selection.IsOk():
            return
            
        dlg = self.OpenDialog(label)
        
        # ret = dlg.Show()
        ret = dlg.ShowModal()
        if ret == wx.ID_CANCEL:
            return
        
        value = dlg.GetValue()
        newitem = self.bingo_list.AppendItem(selection, label + DELIMITER + value)
        
        self.bingo_list.Select(newitem)
        self.bingo_list.CheckItem(newitem)
        self.bingo_list.Expand(self.bingo_list.GetSelection())
        self.bingo_list.SetFocus()
    
#end OnButton def
    
    def GetTopLevel(self):
        """ return sequence tree top-level """
        try:
            selection = item = self.bingo_list.GetSelection()
        except:
            return False
        
        if not selection.IsOk():    
            return False
            
        text = self.bingo_list.GetItemText(selection)
      
        # root = self.bingo_list.GetRootItem()
        # parent = self.bingo_list.GetItemParent(selection)
        
        parents = [item]
        # get item parents
        while self.bingo_list.GetItemParent(item).IsOk():            
            parent = self.bingo_list.GetItemParent(item)     
            parents.append(parent)
            item = parent
            
        parents = [self.bingo_list.GetItemText(itm) for itm in parents if itm.IsOk()]
        print( parents )
        return parents[-2]
        
#end GetTopLevel def
        
    def OnListItemActivated(self, event):
        self.OnAddFunction()
                
#end OnListItemActivated def

    def UpdateStatusBar(self, event=None):
        """ update status bar when selecting a tree item on sequence"""
        selection = self.bingo_list.GetSelection()
        status = self.bingo_list.GetItemText(selection)
        print( status )
        self.GetTopLevelParent().SetStatusText(status)
       
        if event:
            event.Skip()
            
#end Main class

    def OnClose(self, event):        
        data = self.GetTreeData()
        logging.info("data: %s" % str(data))
       
        with open("schedules.json", 'w') as file: 
            json.dump(data, file, sort_keys=True, indent=1)
            
        # continue to exit program
        event.Skip()

#end OnClose def

if __name__ == "__main__":
    app = wx.App()    
    Main()
    app.MainLoop()
    