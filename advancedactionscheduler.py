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
import wx.lib.agw.aui as aui 
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
         
        self._data = {} 
        self._menus = {}
        
        self._schedmgr = schedulemanager.Manager(self)
         
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        #-----
        self.splitter = wx.SplitterWindow(self)
        
        leftpanel = wx.Panel(self.splitter)   
        leftsizer = wx.BoxSizer(wx.VERTICAL)
        
        # sizer for group buttons
        # lefthsizer = wx.WrapSizer(wx.HORIZONTAL)
        # for label in ["New Group","Up","Down","Edit","Delete"]:
            # btn = wx.Button(leftpanel, label=label, size=(-1, 24))
            # lefthsizer.Add(btn, 0, wx.ALL|wx.EXPAND, 2)
            # btn.Bind(wx.EVT_BUTTON, self.OnGroupButtons)
            
        self.group_list = base.CheckList(leftpanel)
        self.group_list.InsertColumn(0, "Group")
        self.group_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnGroupItemSelected)
        
        # leftsizer.Add(lefthsizer, 0, wx.ALL|wx.EXPAND, 0)
        leftsizer.Add(self.group_list, 1, wx.ALL|wx.EXPAND, 0)
        leftpanel.SetSizer(leftsizer)
        
        
        # rhs layout
        
        nbpanel = wx.Panel(self.splitter)   
        self.notebook = wx.Notebook(nbpanel)
        nbsizer = wx.BoxSizer(wx.VERTICAL)
        nbsizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 2)
        
        # the schedule panel/tab page 
        schedpanel = wx.Panel(self.notebook)   
        schedsizer = wx.BoxSizer(wx.VERTICAL)
        
        # -----
        hsizer_functions = wx.WrapSizer(wx.HORIZONTAL)
        for label in ["New Schedule","Up","Down","Edit","Toggle","Delete"]:
            if label == "New Schedule":
                btn = wx.Button(schedpanel, label=label, size=(-1, -1))
            else:
                btn = wx.Button(schedpanel, label=label, size=(-1, -1))
            if label == "Edit":
                btn.Bind(wx.EVT_BUTTON, self.OnEdit)
            else:
                btn.Bind(wx.EVT_BUTTON, self.OnButton)
            if label in ["Delete"]:
                hsizer_functions.AddStretchSpacer()
            hsizer_functions.Add(btn, 0, wx.ALL|wx.EXPAND, 2)
        schedsizer.Add(hsizer_functions, 0, wx.ALL|wx.EXPAND, 2)
        
        hsizer_functions2 = wx.BoxSizer(wx.HORIZONTAL)
        self.cbox_functions = wx.ComboBox(schedpanel, style=wx.CB_READONLY, choices=FUNCTIONS)  
        self.cbox_functions.SetSelection(0)
        btn = wx.Button(schedpanel, label="Add Function", size=(-1, -1))
        btn.Bind(wx.EVT_BUTTON, self.OnAddFunction)
        
        hsizer_functions2.Add(self.cbox_functions, 0, wx.ALL|wx.CENTRE, 2)
        hsizer_functions2.Add(btn, 0, wx.ALL, 5)
        schedsizer.Add(hsizer_functions2, 0, wx.ALL, 0)
        
        # schedsizer.Add(wx.StaticLine(schedpanel), 0, wx.ALL|wx.EXPAND, 0)
                
        # -----
                      
        self.sched_list = wx.dataview.TreeListCtrl(schedpanel, style=wx.dataview.TL_CHECKBOX)        
        self.sched_list.AppendColumn("Schedule")
        schedsizer.Add(self.sched_list, 1, wx.ALL|wx.EXPAND, 0)
        
        hsizer_controls = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(schedpanel, label="Enable", size=(-1, 24))
        btn.Bind(wx.EVT_BUTTON, self.OnEnable)
        hsizer_controls.AddStretchSpacer()
        hsizer_controls.Add(btn, 0, wx.ALL|wx.EXPAND, 2)
        schedsizer.Add(hsizer_controls, 0, wx.ALL|wx.EXPAND, 0)
        
        schedpanel.SetSizer(schedsizer)        
        
        # the schedule manager panel/tab page 
        mgrpanel = wx.Panel(self.notebook)   
        mgrsizer = wx.BoxSizer(wx.VERTICAL)
        mgrpanel.SetSizer(mgrsizer)
        
        self.notebook.AddPage(schedpanel, "Schedules")
        self.notebook.AddPage(mgrpanel, "Manager")
        
        nbpanel.SetSizer(nbsizer)
        
        self.splitter.SplitVertically(leftpanel, nbpanel)
        self.splitter.SetSashGravity(0.4)
        
        self.SetMinSize((700, 600))
        self.SetSize((700, 600))
        
        #-----
        self.CreateMenu()
        self.CreateToolbar()
        self.CreateStatusBar()
        
        #-----
        self.Show()       
        
        #load settings
        # try:
        with open("schedules.json", 'r') as file: 
            self._data = json.load(file)
            
        for k,v in self._data.items():
            name = self._data[k]["name"]
            self.group_list.InsertItem(int(k), name)
            
        file.close()
        # except:             
            # pass
        
        # tree.Select(tree.GetFirstItem())
        
#end __init__ def
    
    def SetScheduleList(self, data):
        """ set the schedule list tree """  
        self.sched_list.DeleteAllItems()
        if not data:
            return
        
        items = {}  
        expanded_items = []
        tree = self.sched_list
        root = self.sched_list.GetRootItem()
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
    
    def CreateToolbar(self):
        # toolbar = wx.ToolBar(self, style=wx.TB_TEXT|wx.TB_FLAT)
        # toolbar = wx.ToolBar(self, style=wx.TB_TEXT)
        toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        # toolbar.AddTool(wx.ID _ANY, "t")#,  wx.BitmapFromBuffer(wx.ART_FILE_OPEN))
        toolbar.SetToolBitmapSize((48,48))
        # toolbar.SetToolBitmapSize((48,48))
        toolbar.SetBackgroundColour("white")
        for label, help, icon in [
            ("Add Group", "Add Group", "new"),
            ("Open", "Open File", "open"), 
            ("Save", "Save File", "save"), 
            # ("Save As", "Save File As...", "save"), 
            ("Import", "Import Image", "import_image"),
            ("Prev", "Select previous image on list", "previous"), 
            ("Next", "Select next image on list", "next"), 
            ("Fullscreen", "Fullscreen image preview", "fullscreen"), 
            ("Transfer", "Transfer images to another file", "transfer")]:
            
            try:
                bmp = theme.GetBitmap(icon, 48,48)  
                # bmp = theme.GetBitmap(icon, 24,24)            
                tool = toolbar.AddTool(wx.ID_ANY, label=label, bitmap=bmp, shortHelp=help)
            except:
                bmp = wx.Bitmap(24,24)            
                tool = toolbar.AddTool(wx.ID_ANY, label=label, bitmap=bmp, shortHelp=help)
            self.Bind(wx.EVT_TOOL, self.OnToolBar, tool)
            
            if label == "Save":
                toolbar.AddSeparator()
            elif label == "Save As":
                toolbar.AddSeparator()
            elif label == "Fullscreen":
                toolbar.AddSeparator()
            
        toolbar.Realize()
        self.SetToolBar(toolbar)
     
#end CreateToolbar def
            
    def WriteData(self):
        """ write changes to data file """
        
        return
            
    def OnToolBar(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        tool = e.FindById(id) 
        label = tool.GetLabel()
        
        if label == "Add Group":
            dlg = dialogs.groups.AddGroup(self)
           
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                return
                                
            name = dlg.GetValue()
            newitem = self.group_list.Append([name])
            
            self._data[newitem] = {"name": name,
                                   "schedules": {}}
            self.WriteData()
            
            self.group_list.Select(newitem)
            self.group_list.CheckItem(newitem)
                        
            self.group_list.SetFocus()            
            
     
        elif label == "Delete":
            self.group_list.DeleteItem(self.group_list.GetSelection())
            
            
        elif label == "new": 
            self.CreateNewEditor()            
        elif label == "open":
            self.OpenFile()            
        elif label == "save": 
            self.SaveFile()            
        elif label == "save as...": 
            self.SaveFileAs()            
        elif label == "import":  
            self.ImportFile()
        elif label == "fullscreen": 
            pub.sendMessage("CloseFullscreenViewer", True)                  
            fsv = FullscreenViewer(self)     
            
            page = self.notebook.GetCurrentPage()
            if page == -1:
                return
                
            image_list = page.image_list
            
            bitmap = None
            selected = image_list.GetFirstSelected()
            if selected == -1:
                if image_list.GetItemCount() > 0:
                   bitmap = image_list.GetItem(0).GetText()
                   bitmap = page.GetBitmap(bitmap)
            else:
                bitmap = image_list.GetItem(selected).GetText()
                bitmap = page.GetBitmap(bitmap)
                
            fsv.SetBitmap(bitmap)            
            fsv.Show()
            fsv.SetFocus()
            
#end OnToolBar def

    def CreateNewEditor(self):
        """ create a new file without a path specified """
        
        title = "untitled"
        ext = ".py"
        new_file = title + ext
        index = 1
        page_count = self.notebook.GetPageCount()
        editors = [self.notebook.GetPage(pg) for pg in range(page_count)]
        pages = [editor._name for editor in editors]
        
        # is new filename unique?
        while new_file in pages:
            new_file = title + str(index) + ext
            index += 1
        
        new_page = FileEditor(self.notebook, None, new_file)
        
        self.notebook.AddPage(new_page, new_file)
        self.notebook.SetSelection(page_count)
   
#end CreateNewEditor def

    def CreateMenu(self):
        menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        file_menus = [("New", "New Schedule File"),
                      ("Open...", "Open Schedule"),
                      ("Save", "Save PyEmbeddedFile"),
                      ("Save As...", "Save PyEmbeddedFile As"),
                      ("Import", "Import Image"),
                      ("Import From Folder", "Import Images From Folder")]
        for item, help_str in file_menus:
            self._menus[item] = menu_file.Append(wx.ID_ANY, item, help_str)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])
            
        menu_file.AppendSeparator()
        
        menu_settings = wx.Menu()
        settings_menus = [("setting ...", "Not Yet Implemented")]                    
        for item, help_str in settings_menus:
            self._menus[item] = menu_settings.Append(wx.ID_ANY, item, help_str)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])
            
        menu_help = wx.Menu()
        help_menus = [("Check for updates", "Check for updates (Not Yet Implemented)"),
                      ("About", "Import Images From Folder")]                      
        for item, help_str in help_menus:
            self._menus[item] = menu_help.Append(wx.ID_ANY, item, help_str)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])
            
        menubar.Append(menu_file, "&File")
        # menubar.Append(menu_edit, "&Edit")
        # menubar.Append(menu_settings, "&Settings")
        menubar.Append(menu_help, "&Help")
        
        self.SetMenuBar(menubar)
    
    def OnMenu(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        label = e.GetLabel(id).lower()
         
        if label == "new": 
            self.CreateNewEditor()            
        elif label == "open...":
            self.OpenFile()            
        elif label == "save": 
            self.SaveFile()            
        elif label == "save as...": 
            self.SaveFileAs()            
        elif label == "import":  
            self.ImportFile()
        elif label == "about":
            AboutDialog(self)
        
#end OnMenu def

    def GetItemDepth(self, item):
        """  backwards """
        tree = self.sched_list
        
        depth = 0
        while tree.GetItemParent(item).IsOk():
            depth += 1 
            item = tree.GetItemParent(item)
        return depth - 1
            
    def GetTreeData(self):
        """ used for saving data """
        tree = self.sched_list
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
        return self.sched_list
        
    def OnEdit(self, event):
        tree = self.sched_list
        selection = tree.GetSelection()
      
        item_text = self.sched_list.GetItemText(selection, 0)
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
                
        self.sched_list.SetFocus()
                
#end OnEdit def           
    
    def OnGroupItemSelected(self, event):
        index = event.Index        
        logging.info("Group item selected: %s" % index)
        
        self.sched_list.DeleteAllItems()
        # update schedule list
        g_index = self.group_list.GetFocusedItem()
        if g_index == -1:
            return
         
        schedules = self._data[str(g_index)]["schedules"] 
        self.SetScheduleList(schedules)
    
#end OnGroupItemSelected def 

    def OnGroupButtons(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        
        if label == "New Group":
            dlg = dialogs.groups.AddGroup(self)
           
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                return
                                
            name = dlg.GetValue()
            newitem = self.group_list.Append([name])
            
            self.group_list.Select(newitem)
            self.group_list.CheckItem(newitem)
            
            self.group_list.SetFocus()
     
        elif label == "Delete":
            self.group_list.DeleteItem(self.group_list.GetSelection())
    
#end OnGroupButtons def           

    def OnButton(self, event):
        e = event.GetEventObject()
        label = e.GetLabel()
        
        if label == "New Schedule":
            dlg = dialogs.schedule.AddSchedule(self)
           
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                return
                
            root = self.sched_list.GetRootItem()
                
            name, value = dlg.GetValue()
            newitem = self.sched_list.AppendItem(root, name + DELIMITER + value)
            
            self.sched_list.Select(newitem)
            self.sched_list.CheckItem(newitem)
            self.sched_list.Expand(self.sched_list.GetSelection())
            self.sched_list.SetFocus()
     
        elif label == "Delete":
            self.sched_list.DeleteItem(self.sched_list.GetSelection())
        
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
        index = self.cbox_functions.GetSelection()
        if index == -1:
            return
        label = self.cbox_functions.GetStringSelection()
        print( label )
        selection = self.sched_list.GetSelection()
        if not selection.IsOk():
            return
            
        dlg = self.OpenDialog(label)
        
        # ret = dlg.Show()
        ret = dlg.ShowModal()
        if ret == wx.ID_CANCEL:
            return
        
        value = dlg.GetValue()
        newitem = self.sched_list.AppendItem(selection, label + DELIMITER + value)
        
        self.sched_list.Select(newitem)
        self.sched_list.CheckItem(newitem)
        self.sched_list.Expand(self.sched_list.GetSelection())
        self.sched_list.SetFocus()
        
        # save tree to data
        schedules = self.GetTreeData()
        g_index = self.group_list.GetFocusedItem()
        self._data[str(g_index)]["schedules"] = schedules
        
        # write changes to file
        self.WriteData()        
        
#end OnButton def
    
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
        
#end GetTopLevel def
        
    def OnListItemActivated(self, event):
        self.OnAddFunction()
                
#end OnListItemActivated def

    def UpdateStatusBar(self, event=None):
        """ update status bar when selecting a tree item on sequence"""
        selection = self.sched_list.GetSelection()
        status = self.sched_list.GetItemText(selection)
        print( status )
        self.GetTopLevelParent().SetStatusText(status)
       
        if event:
            event.Skip()
            
#end Main class

    def OnClose(self, event):        
        # data = self.GetTreeData()
        logging.info("data: %s" % str(self._data))
       
        with open("schedules.json", 'w') as file: 
            json.dump(self._data, file, sort_keys=True, indent=1)
            
        # continue to exit program
        event.Skip()

#end OnClose def

if __name__ == "__main__":
    app = wx.App()    
    Main()
    app.MainLoop()
    
