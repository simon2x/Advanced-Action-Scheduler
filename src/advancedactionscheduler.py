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
import base
import psutil
import json
import logging
import dialogs
import platform
import sys
import time
import os
import os.path
import subprocess
import schedulemanager
import wx.dataview #for TreeListCtrl
import wx.lib.agw.aui as aui

from dialogs import *
import wx.adv
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.agw import hyperlink
from userguide import UserGuideFrame

from ast import literal_eval as make_tuple
from time import gmtime, strftime
from copy import deepcopy
from pprint import pprint

__version__ = [0, 1, 0]
__title__ = "Advanced Action Scheduler"

PLATFORM = platform.system()
if PLATFORM == "Windows":
    import keyboard
else:
    try:
        import keyboard
        keyboard.unhook_all()
    except:    
        print("Failed to import keyboard. Using dummy keyboard")
        print("Not run with root privileges?")
        from dummykeyboard import keyboard        
    
# switch to applications directory
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
os.chdir(path)

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

FUNCTIONKEYS = {
     340: 'F1',
     341: 'F2',
     342: 'F3',
     343: 'F4',
     344: 'F5',
     345: 'F6',
     346: 'F7',
     347: 'F8',
     348: 'F9',
     349: 'F10',
     350: 'F11',
     351: 'F12',
     352: 'F13',
     353: 'F14',
     354: 'F15',
     355: 'F16',
     356: 'F17',
     357: 'F18',
     358: 'F19',
     359: 'F20',
     360: 'F21',
     361: 'F22',
     362: 'F23',
     363: 'F24'
}

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
  
DEFAULTCONFIG = {
    "browserPresets": [], # list of saved browsers
    "currentFile": False, # the currently opened schedule file
    "loadLastFile": True, # the currently opened schedule file
    "fileList": [], # recently opened schedule files
    "firstStart": True,
    "keepFileList": True,
    "maxUndoCount": 10, # maximum number of undo operations a user can do
    "newProcessPresets": [], # list of saved commands
    "openUrlPresets": [], # list of saved urls
    "onClose": 0, # on close window
    "onTrayIconLeft": 0,
    "onTrayIconLeftDouble": 1,
    "schedManagerLogCount": 20, # number of logs before clearing table
    "groupSelectionSwitchTab": True, # auto switch to Schedules tab when group item changed
    "schedManagerSwitchTab": True, # auto switch to Manager tab when schedules enabled
    "showSplashScreen": True,
    "showTrayIcon": True,
    "toggleSchedManHotkey": "CTRL+F11",
    "toolbarSize": 48, # maximum toolbar size
    "windowPos": False, # the last window position
    "windowSize": False, # the last window size
}

class AboutDialog(wx.Frame):  
    
    def __init__(self, parent):                    
        wx.Frame.__init__(self,
                          parent,
                          style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_NO_TASKBAR|wx.STAY_ON_TOP,
                          title=__title__)
        
        self.SetIcon(wx.Icon("icons/icon.png"))                
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
        version = "v" + ".".join([str(x) for x in __version__])
        grid.Add(wx.StaticText(panel, label=version), 0, wx.ALL, 5)
        
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
        w, h = self.GetSize()
        self.SetSize(w, h*2)
        self.SetMinSize(self.GetSize())
        self.SetMaxSize(self.GetSize())
        
        self.Raise()
        self.Show()
        
        self.Bind(wx.EVT_CHAR_HOOK, self.OnChar)
     
    def OnChar(self, event):
        e = event.GetEventObject()
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Destroy()
                          
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
        gridBag = wx.GridBagSizer(5,5)
        
        row = 0        
        self.chkShowTray = wx.CheckBox(panel, label="Show Tray Icon")
        gridBag.Add(self.chkShowTray, pos=(row,0), flag=wx.ALL, border=5)   

        row += 1        
        self.chkShowSplash = wx.CheckBox(panel, label="Show Splash Screen")
        gridBag.Add(self.chkShowSplash, pos=(row,0), flag=wx.ALL, border=5)       
         
        row += 1     
        lblTrayLeft = wx.StaticText(panel, label="On Tray Icon Left Click")
        trayChoices = ["Do Nothing","Show/Hide Main Window","Enable/Disable Schedule Manager",
                       "Show Tray Menu"]
        self.cboxTrayLeft = wx.ComboBox(panel, choices=trayChoices, style=wx.CB_READONLY)
        gridBag.Add(lblTrayLeft, pos=(row,0), flag=wx.ALL, border=5)  
        gridBag.Add(self.cboxTrayLeft, pos=(row,1), flag=wx.ALL, border=5)  
        
        row += 1     
        lblTrayLeft = wx.StaticText(panel, label="On Tray Icon Left Double Click")
        self.cboxTrayLeftDouble = wx.ComboBox(panel, choices=trayChoices, style=wx.CB_READONLY)
        gridBag.Add(lblTrayLeft, pos=(row,0), flag=wx.ALL, border=5)  
        gridBag.Add(self.cboxTrayLeftDouble, pos=(row,1), flag=wx.ALL, border=5)  
        
        row += 1        
        lblToolbarSize = wx.StaticText(panel, label="Maximum Toolbar Icon Size")
        choices = ["16","32","48","64","128","256"]
        self.cboxToolbarSize = wx.ComboBox(panel, choices=choices, style=wx.CB_READONLY)
        gridBag.Add(lblToolbarSize, pos=(row,0), flag=wx.ALL, border=5)  
        gridBag.Add(self.cboxToolbarSize, pos=(row,1), flag=wx.ALL, border=5)

        row += 1        
        self.chkLoadLastFile = wx.CheckBox(panel, label="Load Last Opened File")
        gridBag.Add(self.chkLoadLastFile, pos=(row,0), flag=wx.ALL, border=5)
         
        row += 1
        self.chkRecentFiles = wx.CheckBox(panel, label="Remember Recently Opened Files")
        gridBag.Add(self.chkRecentFiles, pos=(row,0), flag=wx.ALL, border=5)
        
        row += 1        
        self.chkGroupSelectionSwitch = wx.CheckBox(panel, label="Automatically Switch To Schedules Tab On Group Selection")
        gridBag.Add(self.chkGroupSelectionSwitch, pos=(row,0), flag=wx.ALL, border=5)
        
        row += 1        
        self.chkSchedMgrSwitch = wx.CheckBox(panel, label="Automatically Switch To Manager Tab On Enable")
        gridBag.Add(self.chkSchedMgrSwitch, pos=(row,0), flag=wx.ALL, border=5)
        
        row += 1
        lblSchedMgrLogCount = wx.StaticText(panel, label="Schedule Manager Log Count")
        self.schedMgrLogCount = wx.SpinCtrl(panel, min=-1, max=1000)
        gridBag.Add(lblSchedMgrLogCount, pos=(row,0), flag=wx.ALL, border=5)
        gridBag.Add(self.schedMgrLogCount, pos=(row,1), flag=wx.ALL, border=5)
        
        row += 1
        lbl = wx.StaticText(panel, label="Maximum Undo History")
        self.maxUndoCount = wx.SpinCtrl(panel, min=0, max=1000)
        gridBag.Add(lbl, pos=(row,0), flag=wx.ALL, border=5)
        gridBag.Add(self.maxUndoCount, pos=(row,1), flag=wx.ALL, border=5)
        
        row += 1
        lblSchedMgrHotkey = wx.StaticText(panel, label="Toggle Schedule Manager Hotkey")
        self.schedMgrHotkey = wx.TextCtrl(panel)
        # self.schedMgrHotkey.Bind(wx.EVT_TEXT, self.OnHotkeyText)
        self.schedMgrHotkey.Bind(wx.EVT_CHAR_HOOK, self.OnHotkeyEdit)
        gridBag.Add(lblSchedMgrHotkey, pos=(row,0), flag=wx.ALL, border=5)
        gridBag.Add(self.schedMgrHotkey, pos=(row,1), flag=wx.ALL, border=5)
        
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
        e = event.GetEventObject()
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Destroy()
            
    def OnHotkeyEdit(self, event):
        e = event.GetEventObject()
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
        if "+" not in hotkey and not hotkey in FUNCTIONKEYS.values():
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
                
class SplashScreen(wx.adv.SplashScreen):
        
    def __init__(self, timeout=800):  
        splash_style = wx.adv.SPLASH_CENTRE_ON_SCREEN|wx.adv.SPLASH_TIMEOUT
        bmp = wx.Bitmap("splash.png")
        wx.adv.SplashScreen.__init__(self, bmp, splash_style, timeout, None)                
        
class TaskBarIcon(wx.adv.TaskBarIcon):

    def __init__(self, parent):    
        wx.adv.TaskBarIcon.__init__(self)
        
        self.leftClickCount = 0
        self.isWaiting = False
        
        self.parent = parent
        self.parent.taskBarIcon = self
        
        self.iconNormal = wx.Icon(wx.Bitmap("icons/iconnormal.png"))
        self.iconRunning = wx.Icon(wx.Bitmap("icons/iconrunning.png"))
        
        self.tooltip = "{0} {1}".format(__title__, __version__)
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
            
class ToolTip(wx.Frame):  
    
    def __init__(self, parent):                    
        style = wx.SIMPLE_BORDER|wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR
        wx.Frame.__init__(self, parent=parent, style=style)        
        
        self.panel = panel = wx.Panel(self)    
        self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
        self._message = wx.StaticText(panel, label="")
        self._message.SetFont(self.font)
        
        sizer.Add(self._message, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        panel.SetSizerAndFit(sizer)
        self.Fit()
        self.Centre()
        w, h = self.GetSize()
        self.SetMinSize(self.GetSize())
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        
        self.SetBackgroundColour("yellow")
    
    @property
    def font(self):
        return wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False)
     
    @property    
    def message(self):
        return self._message
        
    @message.setter    
    def message(self, value):
        self.SetPosition(wx.GetMousePosition()+(25,15))
        self._message.SetLabel(value)
        self.panel.Fit()
        self.Fit()
        self.Show()
        # self.Raise()
        self.trans = 70
        self.coolDown = False
        self.SetTransparent(self.trans)
        self.timer.Start(100)
        
    def OnLeftUp(self, event):
        self.Hide()
        self.timer.Stop()
    
    def OnTimer(self, event):
        if self.coolDown is True:
            self.trans -= 5
            if self.trans == 50:
                self.Hide()
                self.timer.Stop()
        else:        
            self.trans += 10
        self.SetTransparent(self.trans)
        
        if self.trans == 250 and self.coolDown is False:
            self.coolDown = True
        
            
class Main(wx.Frame):

    def __init__(self, parent=None):

        self._title = "{0}".format(__title__)
        wx.Frame.__init__(self, parent=parent, title=self._title)
                                  
        self._ids = {}
        self._appConfig = DEFAULTCONFIG 
        self._aboutDialog = None
        self._powerAction = None
        self._powerDialog = []
        self._settingsDialog = None
        self._userGuideDialog = None
        self._clipboard = None
        self._currentSelectionType = None
        self._currentTreeFocus = None
        self._fileList = []
        self._fileListMenuItems = {}
        self._imageList = wx.ImageList(32, 32)
        self._schedImageList = wx.ImageList(32, 32)
        self._imageListRef = []
        self._overrideToolSize = None
        self._data = {}
        self._menus = {}
        self._redoStack = []
        self._undoStack = []
        self._commandState = 0
        self._schedManager = schedulemanager.Manager(self)
        self._taskBarIcon = None
        self._toolbarBitmaps = {}
        self.toolbar = None 
        self.toolTip = ToolTip(self)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        #-----
        self.CreateMenu()
        self.CreateImageList()
        self.CreateToolbarBitmaps()
        self.CreateToolbar()
        self.CreateStatusBar()
        self.SetIcon(wx.Icon("icons/icon.png"))
        self.CreateUI()

        #load settings
        self.LoadConfig()
        
        #setup hotkeys
        self.SetupHotkeys()
        self.SetupAcceleratorTable()
        
        #
        self.powerTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnPowerTimer, self.powerTimer)
        self.powerTimer.Start(1000)
        
        self.SetMinSize((700, 600))
        self.SetSize((700, 600))      
        
    def ids(self, value):
        """ return existing ID or create a new ID """
        if value not in self._ids:
            self._ids[value] = wx.NewId()
        return self._ids[value]
            
    @property
    def configPath(self):
        sp = wx.StandardPaths.Get()
        path = sp.GetUserConfigDir()
        if PLATFORM == "Linux":
            dirPath = os.path.join(path, ".advancedactionscheduler")
        else:            
            dirPath = os.path.join(path, "Advanced Action Scheduler")
        path = os.path.join(dirPath, "config.json")
        if not os.path.exists(os.path.join(dirPath)):
            os.makedirs(dirPath)
       
        return path
        
    @property
    def taskBarIcon(self):
        return self._taskBarIcon
        
    @taskBarIcon.setter
    def taskBarIcon(self, value):
        self._taskBarIcon = value
        
    @property
    def groupSelection(self):
        return self.groupList.GetSelection()
     
    @property
    def scheduleSelection(self):
        return self.schedList.GetSelection()
        
    @property
    def commandState(self):
        return self._commandState
        
    @commandState.setter
    def commandState(self, value):
        self._commandState = value
        self.UpdateTitlebar()

    @property
    def infoSchedFont(self):
        return wx.Font(8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        
    @property
    def imageList(self):
        return self._imageList
        
    @property
    def schedImageList(self):
        return self._schedImageList
        
    def imageListIndex(self, label):
        return self._imageListRef.index(label.lower().replace(" ",""))
        
    def AddLogMessage(self, message):
        """ insert log message as first item to schedule messenger list """
        
        if self._appConfig["schedManagerLogCount"] <= 0:
            self.schedLog.DeleteAllItems()
            return
        
        columnNames = {}
        for x in range(self.schedLog.GetColumnCount()):
            column = self.schedLog.GetColumn(x)
            columnText = column.GetText()
            columnNames[columnText] = x
            
        while self.schedLog.GetItemCount() >= self._appConfig["schedManagerLogCount"]:
            try:
                self.schedLog.DeleteItem(self.schedLog.GetItemCount()-1)
            except:
                continue
                
        if self.schedLog.GetItemCount() == 0:
            n = 0
        else:
            first = self.schedLog.GetItemText(0, columnNames["#"])
            n = int(first) + 1
            
        item = self.schedLog.InsertItem(0, "")
        self.schedLog.SetItem(item, columnNames["#"], str(n))
        dt = gmtime() 
        self.schedLog.SetItem(item, columnNames["Time"], strftime("%H:%M:%S", dt))
        self.schedLog.SetItem(item, columnNames["Date"], strftime("%d-%m-%Y", dt))
        for k, v in message.items():
            try:
                self.schedLog.SetItem(item, columnNames[k], v)
            except:
                pass
       
    def AppendSchedules(self):
        if self._clipboard["toplevel"] is False:
            return
        self.SaveStateToUndoStack()
        self.ClearRedoStack()
        
        clip = self._clipboard
        name, schedules, origin = clip["name"], clip["schedules"], clip["origin"]    
        schedules = self.GetUniqueSchedules(schedules)
        self.schedList.AppendSubTree(self.schedList.GetRootItem(), schedules)
        
        index = self.GetGroupListIndex(self.groupSelection)
        self._data[index]["schedules"] = self.GetScheduleTree()
        self.UpdateScheduleImageList()
        
    def CancelPowerAlerts(self):
        for d in self._powerDialog:
            d.Close()
        self._powerDialog = []
            
    def ClearRecentFiles(self):
        for item in self._fileListMenuItems.values():
            self.menuFile.Delete(item)
        self._fileListMenuItems = {}
        self._fileList = []
        
    def ClearRedoStack(self): 
        self._redoStack = []
        self.UpdateToolbar()
        
    def ClearUI(self):
        """ clears lists and set toolbar/button states appropriately """
        self.groupList.DeleteAllItems()
        self.schedList.DeleteAllItems()
        self._data = {}
        
        self.commandState = 0
        self._undoStack = []
        self._redoStack = [] 
        
        self._appConfig["currentFile"] = False
        self.UpdateScheduleToolbar()
        self.UpdateGroupToolbar()
        self.UpdateToolbar()
        self.UpdateTitlebar()
        
    def CloseFile(self):
        
        self.Raise()
        self.Restore()
        self.Show()
        
        if self._commandState != 0:
            dlg = wx.MessageDialog(self,
                                   message="Save file before closing?",
                                   caption="Close File",
                                   style=wx.YES_NO|wx.CANCEL|wx.CANCEL_DEFAULT)
            ret = dlg.ShowModal()                 
            if ret == wx.ID_CANCEL:
                return wx.ID_CANCEL
            
            if ret == wx.ID_YES:
                self.SaveData()
            
            if self._appConfig["loadLastFile"] == False:
                self._appConfig["currentFile"] = False # clear
            if self._appConfig["keepFileList"] == False:
                self._appConfig["fileList"] = []
            else: 
                self._appConfig["fileList"] = self._fileList

        self.SaveDataToJSON(self.configPath, self._appConfig)
        self.ClearUI()
        
    def CopySelection(self):
    
        if self._currentSelectionType == "group":
            index = self.GetGroupListIndex(self.groupSelection)
            self._clipboard = {"origin": "group",
                               "type": "copy",
                               "schedules": self._data[index]["schedules"],
                               "name": self.groupList.GetItemText(self.groupSelection)}
            self._clipboard["toplevel"] = True
            
        elif self._currentSelectionType == "schedule":
            self._clipboard = {"origin": "schedule",
                               "type": "copy",
                               "schedules": self.schedList.GetSubTree(self.scheduleSelection),
                               "name": self.groupList.GetItemText(self.scheduleSelection)}
            if self.schedList.IsTopLevel(self.scheduleSelection):
                self._clipboard["toplevel"] = True
            else:
                self._clipboard["toplevel"] = False
                
        self.UpdateToolbar()
        
    def CreateImageList(self):
        labels = ["group", "schedule", "groupchecked"]
        labels.extend(FUNCTIONS)
        for label in labels:
            img = wx.Image("images/{0}.png".format(label.lower()))
            img.Rescale(32, 32, wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img)
            self.imageList.Add(bmp)
            self.schedImageList.Add(bmp)
            self._imageListRef.append(label.lower())
        
    def CreateMenu(self):
        menubar = wx.MenuBar()
        menuFile = wx.Menu()
        fileMenus = [
            ("New", "Ctrl+N", "New Schedule File", wx.ID_NEW),
            ("Open...", "Ctrl+O", "Open Schedule File", wx.ID_OPEN),
            ("Save", "Ctrl+S", "Save Schedule File", wx.ID_SAVE),
            ("Save As...", "Ctrl+Shift+S", "Save Schedule File As...", wx.ID_SAVEAS),
            ("Close File", "Ctrl+W", "Close Schedule File", wx.ID_CLOSE),
            # ("Import", "Ctrl+I", "Import Schedule File", wx.ID_CDROM), # because no import id
            ("Settings", "Alt+P", "Open Settings...", wx.ID_PREFERENCES),
            ("Exit", "Ctrl+Q", "Exit Program", wx.ID_EXIT)]
        for item, accelHint, helpStr, wxId in fileMenus:
            self._menus[item] = menuFile.Append(wxId, item+"\t"+accelHint, helpStr)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])
            if item == "Close File":
                menuFile.AppendSeparator()
            elif item == "Settings":
                menuFile.AppendSeparator()
                
        self.menuFile = menuFile
        
        menuRun = wx.Menu()
        runMenus = [("Enable Schedule Manager", "Enable Schedule Manager", wx.ID_EXECUTE),
                    ("Disable Schedule Manager", "Disable Schedule Manager", wx.ID_STOP)]
        for item, helpStr, wxId in runMenus:
            self._menus[item] = menuRun.Append(wxId, item, helpStr)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])
            
        self._menus["Disable Schedule Manager"].Enable(False)
            
        menuHelp = wx.Menu()
        helpMenus = [("User Guide\tCtrl+H", "Open User Guide", wx.ID_HELP),
                     ("Check for updates", "Check for updates", wx.ID_SETUP),
                     ("About\tCtrl+F1", "Import Images From Folder", wx.ID_ABOUT)]
        for item, helpStr, wxId in helpMenus:
            self._menus[item] = menuHelp.Append(wxId, item, helpStr)
            self.Bind(wx.EVT_MENU, self.OnMenu, self._menus[item])

        menubar.Append(menuFile, "&File")
        menubar.Append(menuRun, "&Run")
        menubar.Append(menuHelp, "&Help")
        self.menubar = menubar
        self.SetMenuBar(menubar)
        
    def CreateToolbar(self):
        self._tools = {}
        toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        toolSize = int(self._appConfig["toolbarSize"]), int(self._appConfig["toolbarSize"])
        toolbar.SetToolBitmapSize(toolSize)
        for label, help, state, wxId in [  
            ("New", "New", True, wx.ID_NEW),
            ("Open", "Open", True, wx.ID_OPEN),
            ("Save", "Save", True, wx.ID_SAVE),
            ("Save As...", "Save As...", True, wx.ID_SAVEAS),
            ("Close", "Close", True, wx.ID_CLOSE),
            # ("Import", "Import", True, None),
            ("Add Group", "Add Group", True, None),
            ("Remove Group", "Remove Selected Group", False, None),
            ("Cut", "Cut", False, wx.ID_CUT),
            ("Copy", "Copy", False, wx.ID_COPY),
            ("Paste", "Paste", False, wx.ID_PASTE),
            ("Undo", "Undo", False, wx.ID_UNDO),
            ("Redo", "Redo", False, wx.ID_REDO),
            ("Enable Schedule Manager", "Enable Schedule Manager", True, wx.ID_EXECUTE),
            ("Settings", "Settings", True, wx.ID_PREFERENCES)]:
            
            if wxId is None:
                wxId = self.ids(label)
                
            bmp = self._toolbarBitmaps[toolSize[0]][label]
            tool = toolbar.AddTool(wxId, label=label, bitmap=bmp, shortHelp=help)
            
            self.Bind(wx.EVT_TOOL, self.OnMenu, tool)
            self._tools[label] = tool
            tool.Enable(state)
            
            if label == "Close":
                toolbar.AddSeparator() 
            elif label == "Paste":
                toolbar.AddSeparator()      
            elif label == "Remove Group":
                toolbar.AddSeparator()    
            elif label == "Redo":
                toolbar.AddSeparator()
            elif label == "Enable Schedule Manager":
                toolbar.AddStretchableSpace()

        toolbar.Realize()
        self.toolbar = toolbar
        self.SetToolBar(toolbar)
        
    def CreateToolbarBitmaps(self):
        for label in ["New", "Open", "Save", "Save As...", "Close",
                      "Import", "Add Group", "Remove Group", 
                      "Remove Group", "Cut", "Copy", "Paste",
                      "Undo", "Redo", "Enable Schedule Manager",
                      "Disable Schedule Manager", "Settings"]:
            for size in [16,32,48,64,128,256]:
                # print(label)
                img = wx.Image("icons/{0}.png".format(label.lower().replace(" ", "").replace(".","")))
                img.Rescale(size,size, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
                
                try:
                    self._toolbarBitmaps[size]
                except:
                    self._toolbarBitmaps[size] = {}
                    
                self._toolbarBitmaps[size][label] = bmp
    
    def CreateTrayIcon(self):   
        if self.taskBarIcon:
            self.taskBarIcon.RemoveTray()
        self.taskBarIcon = TaskBarIcon(self)
        
    def CreateUI(self):
        self.splitter = wx.SplitterWindow(self)

        leftPanel = wx.Panel(self.splitter)
        # leftPanel.SetBackgroundColour("DARKGREY")
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        hSizerGroup = wx.WrapSizer(wx.HORIZONTAL)
        self.groupBtns = {}
        for label in ["Add Group", "Up", "Down", "Edit", "Toggle", "Delete"]:
            wxId = self.ids("group_"+label)
            btn = wx.Button(leftPanel, wxId, label, name=label, style=wx.BU_EXACTFIT|wx.BU_NOTEXT)
            if label != "Add Group":
                btn.Disable()
            self.groupBtns[label] = btn
            img = wx.Image("icons/{0}.png".format(label.lower().replace(" ", "")))
            img = img.Rescale(24,24, wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img)
            if label == "Edit":
                btn.Bind(wx.EVT_BUTTON, self.OnGroupItemEdit)
            else:
                btn.Bind(wx.EVT_BUTTON, self.OnGroupToolBar)
            btn.SetBitmap(bmp)

            tooltip = wx.ToolTip(label)
            btn.SetToolTip(tooltip)
            hSizerGroup.Add(btn, 0, wx.ALL|wx.EXPAND, 2)
        leftSizer.Add(hSizerGroup, 0, wx.ALL|wx.EXPAND, 5)
        
        self.groupList = base.TreeListCtrl(leftPanel)
        self.groupList.AssignImageList(self.imageList)
        self.groupList.Bind(wx.EVT_CHAR, self.OnGroupChar)
        self.groupList.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.OnGroupItemSelectionChanged)
        self.groupList.Bind(wx.dataview.EVT_TREELIST_ITEM_CONTEXT_MENU, self.OnGroupContextMenu)
        self.groupList.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.OnGroupItemChecked)
        self.groupList.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.OnGroupItemEdit)
        self.groupList.AppendColumn("Group")
        self.groupListRoot = self.groupList.GetRootItem()

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
            wxId = self.ids("schedule_"+label)
            btn = wx.Button(schedPanel, wxId, label, name=label, style=wx.BU_EXACTFIT|wx.BU_NOTEXT)
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
        # schedPanel.SetBackgroundColour("lightgray")
        # -----
        hSizerFunctions2 = wx.BoxSizer(wx.HORIZONTAL)

        self.cboxFunctions = wx.ComboBox(schedPanel, style=wx.CB_READONLY, choices=FUNCTIONS, size=(-1, -1))
        self.cboxFunctions.SetSelection(0)
        self.cboxFunctions.Disable()

        self.btnAddFunction = wx.Button(schedPanel, label="Add Action", name="Add Action", size=(-1, -1))
        img = wx.Image("icons/add.png")
        img = img.Rescale(24,24, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.Bitmap(img)
        self.btnAddFunction.SetBitmap(bmp)
        self.btnAddFunction.Bind(wx.EVT_BUTTON, self.OnScheduleToolBar)
        self.btnAddFunction.Disable()
        hSizerFunctions2.Add(self.cboxFunctions, 0, wx.ALL|wx.CENTRE, 5)
        hSizerFunctions2.Add(self.btnAddFunction, 0, wx.ALL|wx.CENTRE, 5)
        schedSizer.Add(hSizerFunctions2, 0, wx.ALL, 0)

        # -----
        self.splitter2 = wx.SplitterWindow(schedPanel)
        schedListPanel = wx.Panel(self.splitter2)
        schedListSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.schedList = base.TreeListCtrl(schedListPanel, style=wx.dataview.TL_CHECKBOX)
        schedListSizer.Add(self.schedList, 1, wx.ALL|wx.EXPAND, 0)
        schedListPanel.SetSizer(schedListSizer)
        self.schedList.AssignImageList(self.schedImageList)
        self.schedList.Bind(wx.EVT_CHAR, self.OnScheduleChar)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_ITEM_CONTEXT_MENU, self.OnScheduleContextMenu)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.OnScheduleTreeActivated)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.OnScheduleTreeSelectionChanged)
        self.schedList.Bind(wx.dataview.EVT_TREELIST_ITEM_CHECKED, self.OnScheduleTreeItemChecked)
        
        infoPanel = wx.Panel(self.splitter2)
        infoPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.infoSchedButton = wx.Button(infoPanel, style=wx.BU_EXACTFIT|wx.BU_NOTEXT)
        self.infoSchedButton.Bind(wx.EVT_BUTTON, self.OnScheduleItemEdit)
        self.infoSchedButton.SetBitmap(wx.Bitmap())
        self.infoSched = wx.TextCtrl(infoPanel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH|wx.BORDER_NONE)
        self.infoSched.SetFont(self.infoSchedFont)
        self.infoSched.SetBackgroundColour(wx.Colour(60,60,60))
        self.infoSched.SetForegroundColour(wx.Colour(250,250,250))
        infoPanel.SetBackgroundColour(wx.Colour(60,60,60))
        self.infoSchedButton.Hide()
        infoPanelSizer.Add(self.infoSchedButton, 1, wx.ALL|wx.EXPAND, 0)
        infoPanelSizer.Add(self.infoSched, 4, wx.ALL|wx.EXPAND, 5)
        infoPanel.SetSizer(infoPanelSizer)
        self.infoPanelSizer = infoPanelSizer
        self.splitter2.SplitHorizontally(schedListPanel, infoPanel)
        self.splitter2.SetSashGravity(0.8)

        schedSizer.Add(self.splitter2, 1, wx.ALL|wx.EXPAND, 0)
        schedPanel.SetSizer(schedSizer)
        
        self.schedList.SetForegroundColour(wx.Colour(30,30,30))
        self.groupList.SetForegroundColour(wx.Colour(30,30,30))
        
        # the schedule manager panel/tab page
        schedManagerPanel = wx.Panel(self.notebook)
        schedManagerSizer = wx.BoxSizer(wx.VERTICAL)
        schedManagerPanel.SetSizer(schedManagerSizer)

        schedManagerHsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.schedManagerBtns = {}
        for label in ["Clear"]:
            if label == "Clear":
                schedManagerHsizer.AddStretchSpacer()
            btn = wx.Button(schedManagerPanel, label=label, name=label, size=(-1, -1), style=wx.BU_EXACTFIT|wx.BU_NOTEXT)
            self.schedBtns[label] = btn
            img = wx.Image("icons/{0}.png".format(label.lower().replace(" ", "")))
            img = img.Rescale(32,32, wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img)
            btn.SetBitmap(bmp)
            btn.Bind(wx.EVT_BUTTON, self.OnScheduleManagerToolbar)
            schedManagerHsizer.Add(btn, 0, wx.ALL, 5)
            self.schedManagerBtns[label] = btn
            tooltip = wx.ToolTip(label)
            btn.SetToolTip(tooltip)
        schedManagerSizer.Add(schedManagerHsizer, 0, wx.ALL|wx.EXPAND, 0)

        self.schedLog = base.BaseList(schedManagerPanel)
        self.schedLog.Bind(wx.EVT_RIGHT_UP, self.OnScheduleManagerContextMenu)
        self.schedLog.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnScheduleManagerContextMenu)
        self.schedLog.InsertColumn(0, "Group")
        self.schedLog.InsertColumn(1, "Schedule")
        self.schedLog.InsertColumn(2, "Message")
        self.schedLog.InsertColumn(4, "Time")
        self.schedLog.InsertColumn(5, "Date")
        self.schedLog.InsertColumn(6, "#")
        self.schedLog.setResizeColumn(3)
        schedManagerSizer.Add(self.schedLog, 1, wx.ALL|wx.EXPAND, 5)

        self.notebook.AddPage(schedPanel, "Schedules")
        self.notebook.AddPage(schedManagerPanel, "Manager")

        nbPanel.SetSizer(nbSizer)

        self.splitter.SplitVertically(leftPanel, nbPanel)
        self.splitter.SetSashGravity(0.2)       
        
        self.schedList.AppendColumn("Schedule")
    
    def CutSelection(self):
    
        if self._currentSelectionType == "group":
            if not self.groupSelection.IsOk(): 
                return
            self.SaveStateToUndoStack()    
            index = self.GetGroupListIndex(self.groupSelection)
            self._clipboard = {"origin": "group",
                               "type": "cut",
                               "schedules": self._data[index]["schedules"],
                               "name": self.groupList.GetItemText(self.groupSelection),
                               "toplevel": True}
            next = self.groupList.GetNextSibling(self.groupSelection)
            self.groupList.DeleteItem(self.groupSelection)
            self.schedList.DeleteAllItems()
            del self._data[index]
            if next.IsOk():
                self.groupList.Select(next)
            
        elif self._currentSelectionType == "schedule":
            if not self.scheduleSelection.IsOk(): 
                return
            self.SaveStateToUndoStack()  
            index = self.GetGroupListIndex(self.groupSelection)
            nextItem = self.groupList.GetNextSibling(self.groupSelection)                
            self._clipboard = {"origin": "schedule",
                               "type": "cut",
                               "schedules": self.schedList.GetSubTree(self.scheduleSelection),
                               "name": self.groupList.GetItemText(self.scheduleSelection)}
            if self.schedList.IsTopLevel(self.scheduleSelection):
                self._clipboard["toplevel"] = True
            else:
                self._clipboard["toplevel"] = False
            self.schedList.DeleteItem(self.scheduleSelection)
            self._data[index]["schedules"] = self.GetScheduleTree()
            
            if nextItem.IsOk():
                self.groupList.Select(nextItem)

        self.UpdateScheduleInfo()
        self.UpdateToolbar()
            
    def DeleteGroupItem(self):
        if not self.groupSelection.IsOk():
            return
        groupIdx = self.GetGroupListIndex(self.groupSelection)
        next = self.groupList.GetNextSibling(self.groupSelection)
        self.SaveStateToUndoStack()
        self.ClearRedoStack()
        
        self.schedList.DeleteAllItems()        
        self.groupList.DeleteItem(self.groupSelection)
        del self._data[groupIdx]                
        
        if next.IsOk():
            self.groupList.Select(next)
            self.UpdateGroupToolbar()
            self.UpdateScheduleToolbar()
        self.UpdateScheduleInfo()
            
    def DeleteScheduleItem(self):
        if not self.scheduleSelection.IsOk():
            return
        self.SaveStateToUndoStack()
        next = self.schedList.GetNextSibling(self.scheduleSelection)
        self.schedList.DeleteItem(self.scheduleSelection)
        self.UpdateScheduleToolbar()
        self.SaveScheduleTreeToData()
        self.ClearRedoStack()
        if next.IsOk():
            self.schedList.Select(next)
            self.UpdateScheduleToolbar()
        self.UpdateScheduleInfo()    
       
    def DisableScheduleManager(self):
        # Enable/Disable menu item accordingly
        self._menus["Disable Schedule Manager"].Enable(False)
        self._menus["Enable Schedule Manager"].Enable(True)
        
        self._tools["Enable Schedule Manager"].SetLabel("Enable Schedule Manager")
        self._tools["Enable Schedule Manager"].SetShortHelp("Enable Schedule Manager")
        width, height = self.toolbar.GetToolBitmapSize()
        img = wx.Image("icons/enableschedulemanager.png")            
        img = img.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)        
        bmp = self._toolbarBitmaps[width]["Enable Schedule Manager"]
        self._tools["Enable Schedule Manager"].SetNormalBitmap(bmp)
        wx.CallAfter(self.toolbar.Realize)

        self._schedManager.Stop()
        
        if self.taskBarIcon:
            self.taskBarIcon.SetTrayIcon(running=False)
         
    def DoRedo(self):
        if self._redoStack == []:
            return
        state = self._redoStack[-1]
        self._undoStack.append(self.GetCommandState())
        del self._redoStack[-1]
        self.RestoreState(state)
        self.commandState += 1
        self.UpdateScheduleInfo()
        self.UpdateGroupImageList()
        
    def DoUndo(self):
        if self._undoStack == []:
            return
        state = self._undoStack[-1]
        self._redoStack.append(self.GetCommandState())
        del self._undoStack[-1]
        self.RestoreState(state)
        self.commandState -= 1
        self.UpdateScheduleInfo()
        self.UpdateGroupImageList()
        
    def EnableScheduleManager(self):
        self.CancelPowerAlerts()
        
        # Enable/Disable menu item accordingly
        self._menus["Disable Schedule Manager"].Enable(True)
        self._menus["Enable Schedule Manager"].Enable(False)
        
        self._tools["Enable Schedule Manager"].SetLabel("Disable Schedule Manager")
        self._tools["Enable Schedule Manager"].SetShortHelp("Disable Schedule Manager")
        width, height = self.toolbar.GetToolBitmapSize()
        
        img = wx.Image("icons/disableschedulemanager.png")        
        bmp = self._toolbarBitmaps[width]["Disable Schedule Manager"]
        self._tools["Enable Schedule Manager"].SetNormalBitmap(bmp)
        
        sendData = {}
        for item, data in self._data.items():
            if self.groupList.GetCheckedState(item) == 0:
                continue
            itemText = self.groupList.GetItemText(item)
            sendData[itemText] = data["schedules"]
        self.toolbar.Realize()    
        if not sendData:
            self.DisableScheduleManager()
            return
        self._schedManager.SetSchedules(sendData)
        self._schedManager.Start()

        # switch to the manager when schedules are started
        if self._appConfig["schedManagerSwitchTab"] is True:
            self.notebook.SetSelection(1)
        
        if self.taskBarIcon:
            self.taskBarIcon.SetTrayIcon(running=True)    
            
    def ExtractContentsFromSchedules(self, schedules):
        """"""
        result = {}
        for (index, itemData) in schedules:
            if "," not in index:
                n = int(index)
                result[n] = []
                continue
            newIndex = ",".join(index.split(",")[1:])
            result[n].append((newIndex, itemData))
        return result
    
    def GetAppConfig(self):
        return self._appConfig
        
    def GetCommandState(self):
        """ get state for undo/redo operations """
        state = {"data": self.GetDataForJSON(),
                 "groupSel": self.groupList.GetIndexByOrder(self.groupList.GetSelection()),
                 "schedSel": self.schedList.GetIndexByOrder(self.schedList.GetSelection()),
                 "currentSelectionType": self._currentSelectionType}
        return deepcopy(state)
    
    def GetDialog(self, label, value=None):

        if label == "CloseWindow":
            dlg = dialogs.window.WindowDialog(self, title="Close Window")
        elif label == "Control":
            dlg = dialogs.control.AddControl(self)
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
        elif label == "NewProcess":
            dlg = dialogs.process.NewProcess(self)
            dlg.SetHistoryList(self._appConfig["newProcessPresets"])
        elif label == "OpenURL":
            dlg = dialogs.browser.OpenURL(self)
            dlg.SetBrowserPresets(self._appConfig["browserPresets"])
            dlg.SetUrlPresets(self._appConfig["openUrlPresets"])
        elif label == "Power":
            dlg = power.AddPower(self)
        elif label == "StartSchedule":
            dlg = dialogs.schedule.StartSchedule(self)
            dlg.SetScheduleNames(self.GetScheduleNames())
        elif label == "StopSchedule":
            dlg = dialogs.schedule.StopSchedule(self)
            dlg.SetScheduleNames(self.GetScheduleNames())
            
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
            jsonData[str(n)]["schedules"] = itemData["schedules"]
            jsonData[str(n)]["checked"] = itemData["checked"]
            n += 1    
            child = self.groupList.GetNextSibling(child)
            
        jsonData["__version__"] = __version__        
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
        
    def GetBitmapFromImage(self, name, size=None):
        img = wx.Image("images/{0}.png".format(name.lower().replace(" ","")))
        if size:
            w, h = size
            img = img.Rescale(w, h, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.Bitmap(img)
        return bmp
        
    def GetGroupTree(self):
        """ retrieve tree structure, used for saving data """
        data = self.groupList.GetTree()
        return data

    def GetScheduleNames(self):
        """ return toplevel items"""
        schedules = []
        item = self.schedList.GetFirstItem()
        while item.IsOk():
            schedules.append(self.schedList.GetItemText(item, 0).split(DELIMITER)[0])
            item = self.schedList.GetNextSibling(item)

        return schedules

    def GetScheduleTree(self):
        """ retrieve tree structure, used for saving data """
        data = self.schedList.GetTree()
        return data
    
    def GetUniqueSchedules(self, schedules):
        """ rename names in tree structure if schedule already exists """
        schedules = deepcopy(schedules)
        result = []
        schedNames = self.GetScheduleNames()
        for (index, itemData) in schedules:
            if "," not in index:
                name, data = itemData["columns"]["0"].split(DELIMITER)
                n = 1
                newName = name
                while newName in schedNames:
                    newName = name + "_%d" % n
                    n += 1
                schedNames.append(newName)
                itemData["columns"]["0"] = newName + DELIMITER + data 
                result.append((index, itemData))
                continue
            result.append((index, itemData))
        return result
        
    def LoadConfig(self):
        """ load application config and restore config settings """
        try:
            with open(self.configPath, 'r') as file:
                self._appConfig.update(json.load(file))
        except FileNotFoundError:
            with open(self.configPath, 'w') as file:
                json.dump(self._appConfig, file, sort_keys=True, indent=2)
        except json.JSONDecodeError:
            with open(self.configPath, 'w') as file:
                json.dump(self._appConfig, file, sort_keys=True, indent=2)
        file.close()
        
        self.SetRecentFiles()
        
        if self._appConfig["loadLastFile"] is True:
            if os.path.exists(self._appConfig["currentFile"]):
                self.LoadFile(self._appConfig["currentFile"])
            else:
               self._appConfig["currentFile"] = False
              
        if self._appConfig["showSplashScreen"] is True:
            SplashScreen(800)
           
        # set position of window providing that the users monitor geometry 
        # (albeit with some arbitrary leeway) contains the last mouse position
        try:
            x, y = [int(v) for v in make_tuple(self._appConfig["windowPos"])]
            displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
            for display in displays:
                x1,y1,w,h = display.GetGeometry()
                if x in range(x1-200,x1+w) and y in range(y1-200,y1+h):
                    self.SetPosition((x,y))
                    break
                continue
            x, y = [int(v) for v in make_tuple(self._appConfig["windowSize"])]
            self.SetSize((x, y))
        except Exception as e:
            print(e)
            
        self.UpdateTrayIcon()
        self.UpdateToolbarSize()
        self.UpdateTitlebar()
        # wx.CallLater(1000, self.Show)
        self.Show()
        self.Raise()
        
        if self._appConfig["firstStart"]:
            self.ShowUserGuide()
            self._appConfig["firstStart"] = False
        
    def LoadFile(self, filePath):
        """ load a schedule file by file path """
        if filePath:
            try:
                with open(filePath, 'r') as file:
                    fileData = json.load(file)
                self.SetGroupTree(fileData)
                self.schedList.DeleteAllItems()
                self._appConfig["currentFile"] = filePath
                self.SaveDataToJSON(self.configPath, self._appConfig)
                self.UpdateTitlebar()
                
            except FileNotFoundError:
                logging.error("{0}".format(FileNotFoundError))
                return
            except json.JSONDecodeError:
                # TODO: raise corrupt/invalid file error
                logging.error("{0}".format(json.JSONDecodeError))
                return
     
            self.UpdateRecentFiles(filePath)
        
    def MoveGroupItemDown(self):
        # valid item selection?
        selection = self.groupList.GetSelection()
        if not selection.IsOk():
            return
        
        # can item be moved down?
        next = self.groupList.GetNextSibling(selection)
        assert next.IsOk(), "Next item is not valid"
        self.SaveStateToUndoStack()
        
        idxText = self.groupList.GetItemText(selection)
        checkState = self.groupList.GetCheckedState(selection)
        idxData = self._data[selection]
        
        newItem = self.groupList.InsertItem(self.groupListRoot, next, idxText)
        self.groupList.DeleteItem(selection)
        self.groupList.CheckItem(newItem, checkState)
        
        self._data[newItem] = idxData
        del self._data[selection]
        
        self.groupList.Select(newItem)
        
        self.UpdateGroupImageList()
        self.SaveScheduleTreeToData()
        self.ClearRedoStack()
        
        self.UpdateGroupToolbar()
    
    def MoveGroupItemUp(self):
        # valid item selection?
        selection = self.groupList.GetSelection()
        if not selection.IsOk():
            return
        
        # can previous item be moved down?
        previous = self.schedList.GetPreviousSibling(selection)
        assert previous.IsOk() is True, "Previous item is not valid"
        self.SaveStateToUndoStack()
        
        idxText = self.groupList.GetItemText(previous)
        checkState = self.groupList.GetCheckedState(previous)
        idxData = self._data[previous]
        
        newItem = self.groupList.InsertItem(self.groupListRoot, selection, idxText)
        self.groupList.DeleteItem(previous)
        self.groupList.CheckItem(newItem, checkState)
        
        self._data[newItem] = idxData
        del self._data[previous]

        self.SaveScheduleTreeToData()
        self.ClearRedoStack()
        
        self.UpdateGroupImageList()
        self.UpdateGroupToolbar()
        
    def MoveScheduleItemDown(self):
        # valid item selection?
        selection = self.schedList.GetSelection()
        if not selection.IsOk():
            return

        # can item be moved down?
        next = self.schedList.GetNextSibling(selection)
        assert next.IsOk(), "Next item is not valid"
        self.SaveStateToUndoStack()
        
        baseIdx = self.schedList.GetItemIndex(selection)
        subTree = self.schedList.GetSubTree(selection)
        self.schedList.InsertSubTree(next, subTree)        
        self.schedList.DeleteItem(selection)
                
        # need to reflect these changes in self._data
        groupSel = self.GetGroupListIndex(self.groupList.GetSelection())
        groupScheds = self._data[groupSel]["schedules"]
        
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
        self._data[groupSel]["schedules"] = newScheds      
        
        self.schedList.Select(self.schedList.GetNextSibling(next))
        self.UpdateScheduleToolbar()
        self.UpdateScheduleImageList()
        self.SaveScheduleTreeToData()
        self.ClearRedoStack()
    
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
        groupScheds = self._data[groupSel]["schedules"]
        
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
                
        # print(idxDecr, idxIncr)
        newScheds = groupScheds[:idxIncr[0]]
        for x in idxDecr:
            newScheds.append(groupScheds[x])
        for x in idxIncr:
            newScheds.append(groupScheds[x])
        newScheds += groupScheds[idxDecr[-1]+1:] 
        self._data[groupSel]["schedules"] = newScheds
        
        self.SaveScheduleTreeToData()
        self.ClearRedoStack()
        self.UpdateScheduleImageList()
        self.UpdateScheduleToolbar()
         
    def OnClose(self, event=None):
        """ 
        on application exit we prompt user to close file and
        disable the schedule manager directly
        """
        self._appConfig["windowSize"] = str(self.GetSize())
        self._appConfig["windowPos"] = str(self.GetPosition())
        if self.CloseFile() == wx.ID_CANCEL:
            return
        self.CancelPowerAlerts()
        self._schedManager.Stop()
        
        try:
            self.taskBarIcon.RemoveTray()
        except:
            pass
        
        keyboard.unhook_all()
        self.Destroy()        
        
    def OnAboutDialogClose(self, event):
        """ 
        clear reference to AboutDialog so a new instance 
        can be opened next time 
        """
        try:
            self._aboutDialog = None
            event.Skip()
        except Exception as e:
            print(e)
        
    def OnComboboxFunction(self, event=None):
        """ selecting a combobox option automatically raises a corresponding dialog """

        if not self.scheduleSelection.IsOk():
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
        self.SaveStateToUndoStack()
        self.ClearRedoStack()

        value = label + DELIMITER + dlg.GetValue()
        newItem = self.schedList.AppendItem(self.scheduleSelection, value)
        self.schedList.SetItemImage(newItem, self.imageListIndex(label))
        
        schedSelIdx = self.schedList.GetItemIndex(self.scheduleSelection)
        idx = self.schedList.GetItemIndex(newItem)
        groupSel = self.groupList.GetSelection()
       
        n = 0
        itm = self.schedList.GetFirstItem()
        while itm != newItem and itm.IsOk():
            n += 1
            itm = self.schedList.GetNextItem(itm)
            
        self._data[groupSel]["schedules"].insert(n, (idx, {'columns': {"0": value}, 
                                              'expanded': False, 
                                              'selected': True, 
                                              'checked': 1}))
        
        self.schedList.Select(newItem)
        self.schedList.CheckItem(newItem)
        self.schedList.Expand(newItem)
        self.schedList.SetFocus()
    
    def OnGroupChar(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_DELETE:
            self.DeleteGroupItem()
            return
        
        if key == 341: # F2
            self.OnGroupItemEdit()
            return
            
        # important, as the control toggles item 
        # even if item is not OK...therefore
        # causes issues with saving state correctly
        if key == wx.WXK_SPACE:
            if self.groupSelection.IsOk():
                event.Skip()
            return
        event.Skip()
               
    def OnGroupContextMenu(self, event):
        menu = wx.Menu()
        subMenu = wx.Menu()  
        pastes = []
        if self._clipboard and self._clipboard["toplevel"] is True:
            pastes = ["Paste As New Group"]
            if self.groupList.GetSelection().IsOk():
                pastes.extend(["Paste Before", "Paste After", "Paste Into Group"])
            for label in pastes:
                item = subMenu.Append(wx.ID_ANY, label)
            
        for label in ["Edit","Add Group","","Up","Down","Toggle","","Delete"]:
            if not label:
                menu.AppendSeparator()
                continue
            if label == "Add Group":
                if self.groupList.GetSelection().IsOk():
                    item = menu.Append(wx.ID_ANY, "Cut")  
                    item = menu.Append(wx.ID_ANY, "Copy")  
                if self._clipboard and pastes != []:
                    item = menu.AppendSubMenu(subMenu, "Paste")
            
            item = menu.Append(wx.ID_ANY, label)        
            if not self.groupBtns[label].IsEnabled():
                item.Enable(False)
                continue
        menu.Bind(wx.EVT_MENU, self.OnGroupToolBar)
        self.PopupMenu(menu)
        
    def OnGroupItemChecked(self, event):
        self.SaveStateToUndoStack()
        self.ClearRedoStack()
        groupSel = self.GetGroupListIndex(self.groupSelection)
        self._data[groupSel]["checked"] = self.groupList.GetCheckedState(self.groupSelection)
        self.UpdateGroupImageList()
        
    def OnGroupItemEdit(self, event=None):
        selection = self.groupList.GetSelection()
        if not selection.IsOk():
            return
         
        groupName = self.groupList.GetItemText(selection, 0)
        
        m = "Group Name:"
        
        # find unique group name
        i = 1
        b = "group_"
        uid = b + str(i)
        groupNames = [s for s in self.GetGroupNames() if not s == groupName]
        while uid in groupNames:
            i += 1
            uid = b + str(i)
                
        while True:            
            dlg = wx.TextEntryDialog(self, message=m, caption="Add Group", value=groupName)
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
            self.groupList.SetItemText(selection, newName)
            self.ClearRedoStack()
            return
        
    def OnGroupItemKeyDown(self, event):
        key = event.GetKeyCode()
        index = self.groupList.GetSelection()
        if key == wx.WXK_SPACE:
            self.groupList.CheckItem(index)
            
    def OnGroupItemSelectionChanged(self, event=None):
        """ update group buttons and schedule list """
        self._currentTreeFocus = "group"
        if self._appConfig["groupSelectionSwitchTab"] is True:
            self.notebook.SetSelection(0)
        
        self.UpdateGroupToolbar()
        self.UpdateToolbar()
        
        self.schedList.DeleteAllItems()
        for item, data in self._data.items():
            if self.groupSelection != item:
                continue
            self.toolbar.EnableTool(self._ids["Remove Group"], True)
            self.SetScheduleTree(data["schedules"])
            self.schedBtns["Add Schedule"].Enable()
            break
        
        self.toolbar.EnableTool(self._ids["Remove Group"], False)
        
        self.schedBtns["Add Schedule"].Disable()
        self.UpdateScheduleToolbar()
        self.UpdateScheduleInfo()
                    
    def OnGroupToolBar(self, event):
        try:
            e = event.GetEventObject()
            name = e.GetName()
        except:
            id = event.GetId()
            name = e.GetLabel(id)

        if name == "Add Group":
            self.ShowAddGroupDialog()
        elif name == "Copy":
            self.CopySelection()    
        elif name == "Cut":
            self.CutSelection()      
        elif name == "Delete":
            print("event type", dir(wx.EVT_BUTTON),event.GetEventCategory(),(event.GetEventType()))
            self.DeleteGroupItem()
        elif name == "Down":
            self.MoveGroupItemDown()
        elif name == "Edit":
            self.OnGroupItemEdit()
        elif name == "Paste After":
            self.OnGroupListPaste(append=2)    
        elif name == "Paste As New Group":
            self.OnGroupListPaste(append=0)
        elif name == "Paste Before":
            self.OnGroupListPaste(append=1)
        elif name == "Paste Into Group":
            self.PasteIntoGroup(append=0)
        elif name == "Toggle":
            self.ToggleGroupSelection()
        elif name == "Up":
            self.MoveGroupItemUp()   
            
    def OnMenu(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        
        if id == wx.ID_ABOUT:
            self.ShowAboutDialog()
        elif id == wx.ID_CLOSE:
            self.CloseFile()
        elif id == wx.ID_COPY:
            self.CopySelection()     
        elif id == wx.ID_CUT:
            self.CutSelection()    
        elif id == wx.ID_SETUP:
            self.ShowCheckForUpdatesDialog()  
        elif  id == wx.ID_EXECUTE:
            self.ToggleScheduleManager() 
        elif id == wx.ID_EXIT:
            self.Close()
        elif id == wx.ID_CDROM:
            self.ShowImportDialog()
        elif id == wx.ID_NEW:
            self.CloseFile()
        elif id == wx.ID_PREFERENCES:
            self.ShowSettingsDialog() 
        elif id == wx.ID_OPEN:
            self.OpenFile()
        elif id == wx.ID_PASTE:
            self.OnPaste()
        elif id == wx.ID_REDO:
            self.DoRedo()
        elif id == wx.ID_SAVE:
            self.SaveData()  
        elif id == wx.ID_SAVEAS:
            self.SaveFileAs()  
        elif id == wx.ID_STOP:
            self.DisableScheduleManager()
        elif id == wx.ID_UNDO:
            self.DoUndo()
        elif id == wx.ID_HELP:
            self.ShowUserGuide()
        elif id == self._ids["Add Group"]:
            self.ShowAddGroupDialog() 
        # elif id == self._ids["Import"]:
            # self.ShowImportDialog()    
        elif id == self._ids["Remove Group"]:
            self.DeleteGroupItem()    
    
    def OnGroupListPaste(self, append=0):
        """ 
        This handles the hotkey or toolbar press and not
        the context menu paste.
        By default, we paste clipboard contents into a new group 
        appended to end of group list.
        """
        
        # we only allow schedules to be pasted onto the group list
        if self._clipboard["toplevel"] is False:
            self.toolTip.message = ("Actions can only be pasted inside a schedule")
            return
        
        name = self._clipboard["name"]
        # if we are pasting a schedule into a group, we take
        # the schedule's name as new group name
        try:
            name = name.split(DELIMITER)[0]
        except:
            pass # not a schedule
            
        res = self.ShowAddGroupDialog(name, 
                                      "Paste Contents Into New Group",
                                      self._clipboard["schedules"], append)                                           
        
        # clear the clipboard
        # if self._clipboard["type"] == "cut" and res is not None:
            # self._clipboard = None
            # self.UpdateToolbar()
        
        self.UpdateGroupImageList()
             
    def OnPaste(self):
        """ user pressed shortcut or toolbar paste button """
        if self._clipboard is None:
            return 
        if self._currentSelectionType == "group":
            self.OnGroupListPaste()
        elif self._currentSelectionType == "schedule":
            self.OnScheduleTreePaste()
            
    def OnPowerAction(self, kwargs):
        self._powerAction = kwargs        
        self.DisableScheduleManager()
        
    def OnPowerTimer(self, event):
        """ 
        alert the user with notice of impending power action
        with a always on top dialog on each display/monitor
        or user specified
        
        the user can cancel this action by pressing cancel button,
        which subsequently destroys any other alerts
        """
        if self._powerAction and not self._powerDialog:
            primary = self._powerAction["primary"]
            displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
            for display in displays:
                if primary is True and not display.IsPrimary():
                    continue
                rectDisplay = display.GetGeometry()
                d = dialogs.power.PowerAlertDialog()
                d.SetContainingRect(rectDisplay)
                d.SetValue(self._powerAction)
                self._powerDialog.append(d)
            self._powerAction = None
        
        cancelAction = None
        for d in self._powerDialog:
            if not d.IsShown():
                cancelAction = True
                
        if cancelAction:
            self.CancelPowerAlerts()
            self.AddLogMessage({"Message":"User cancelled power action"})
        
    def OnRecentFile(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        filePath = e.GetLabel(id)
        
        if filePath == self._appConfig["currentFile"]:
            logging.info("File already opened")
            return
        self.CloseFile()    
        self.LoadFile(filePath)
        
    def OnScheduleChar(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_DELETE:
            self.DeleteScheduleItem()
            return
        
        if key == 341: # F2
            self.OnScheduleItemEdit()
            return
            
        # important, as the control toggles item 
        # even if item is not OK...therefore
        # causes issues with saving state correctly
        if key == wx.WXK_SPACE:
            if self.scheduleSelection.IsOk():
                event.Skip()
            return
        event.Skip()
            
    def OnScheduleContextMenu(self, event):
        menu = wx.Menu()
        self._currentSelectionType = "schedule"
        subMenu = wx.Menu()
        pastes = []
        if self._clipboard and self.scheduleSelection.IsOk():
            if self._clipboard["toplevel"] is False and not self.schedList.IsTopLevel(self.scheduleSelection):
                if self._clipboard["origin"] == "schedule":
                    pastes.extend(["Paste Before","Paste After","Paste Into"])
                pastes.append("Paste Append")
            elif self._clipboard["toplevel"] is False and self.schedList.IsTopLevel(self.scheduleSelection):
                pastes.append("Paste Into")
            elif self._clipboard["toplevel"] is True and self.schedList.IsTopLevel(self.scheduleSelection):
                pastes.extend(["Paste Before","Paste After"])
                if self._clipboard["origin"] == "schedule":
                    pastes.append("Paste Into")
                pastes.append("Paste Append")
            elif self._clipboard["toplevel"] is True and not self.schedList.IsTopLevel(self.scheduleSelection):
                pastes.append("Paste Append")
        elif self.scheduleSelection.IsOk():        
            pastes.append("Paste Append")
            
        for label in pastes:
            item = subMenu.Append(wx.ID_ANY, label)
                    
        subMenuFunctions = wx.Menu()
        if self.cboxFunctions.IsEnabled():
            for label in FUNCTIONS:
                item = subMenuFunctions.Append(wx.ID_ANY, label)
            
        for label in ["Edit", "Add Schedule", "", "Up", "Down",
                      "Toggle", "", "Delete"]:
            if not label:
                menu.AppendSeparator()
                continue
            if label == "Add Schedule":                        
                item = menu.AppendSubMenu(subMenuFunctions, "Add Action")
                if not self.cboxFunctions.IsEnabled():
                    item.Enable(False)
                    
            item = menu.Append(wx.ID_ANY, label)  

            if label == "Add Schedule":
                if self.schedList.GetSelection().IsOk():
                    menu.AppendSeparator()
                    item = menu.Append(wx.ID_ANY, "Cut")  
                    item = menu.Append(wx.ID_ANY, "Copy")  
                if self._clipboard and pastes != []:
                    item = menu.AppendSubMenu(subMenu, "Paste")
                    
            if not self.schedBtns[label].IsEnabled():
                item.Enable(False)
                continue
        menu.Bind(wx.EVT_MENU, self.OnScheduleToolBar)
        self.PopupMenu(menu)
        
    def OnScheduleManagerContextMenu(self, event):
        menu = wx.Menu()
        subMenu = wx.Menu()
        if self.cboxFunctions.IsEnabled():
            for label in FUNCTIONS:
                item = subMenu.Append(wx.ID_ANY, label)
            
        for label in ["Clear"]:
            if not label:
                menu.AppendSeparator()
                continue
                
            item = menu.Append(wx.ID_ANY, label)        
            # if not self.schedManagerBtns[label].IsEnabled():
                # item.Enable(False)
                # continue
        menu.Bind(wx.EVT_MENU, self.OnScheduleManagerToolbar)
        self.PopupMenu(menu)    
        
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
            self.SaveStateToUndoStack()    
            newName, value = dlg.GetValue()
            value = newName + DELIMITER + value
            self.schedList.SetItemText(selection, 0, value)
            self.SaveScheduleTreeToData() 
            self.ClearRedoStack()
        else:
            dlg = self.GetDialog(name)
            dlg.SetValue(params)
            if dlg.ShowModal() != wx.ID_OK:
                return    
            self.SaveStateToUndoStack()
            value = dlg.GetValue()
            value = name + DELIMITER + value
            self.schedList.SetItemText(selection, 0, value)
            self.SaveScheduleTreeToData() 
            self.ClearRedoStack()
                
        idx = self.schedList.GetItemIndex(selection)
        groupSel = self.groupList.GetSelection()
        for n, (j, k) in enumerate(self._data[groupSel]["schedules"]):
            if not j == idx:
                continue 
            self._data[groupSel]["schedules"][n][1]["columns"]["0"] = value
            break
          
        self.schedList.SetFocus()

        # updated information
        self.UpdateScheduleInfo()    

    def OnScheduleManagerToolbar(self, event):
        try:
            e = event.GetEventObject()
            name = e.GetName()
        except:
            id = event.GetId()
            name = e.GetLabel(id)

        if name == "Clear":
            self.schedLog.DeleteAllItems()       
            
    def OnScheduleToolBar(self, event):
        try:
            e = event.GetEventObject()
            name = e.GetName()
        except:
            id = event.GetId()
            name = e.GetLabel(id)

        if name == "Add Action":
            self.OnComboboxFunction()
        elif name == "Add Schedule":
            self.ShowAddScheduleDialog()
        elif name == "Copy":
            self.CopySelection()
        elif name == "Cut":
            self.CutSelection()
        elif name == "Delete":
            self.DeleteScheduleItem()   
        elif name == "Down":
            self.MoveScheduleItemDown()
        elif name == "Edit":
            self.OnScheduleItemEdit()
        elif name == "Paste Before":
            self.PasteIntoGroup(append=1)
        elif name == "Paste After":
            self.PasteIntoGroup(append=2)
        elif name == "Paste Append":
            self.PasteIntoGroup(append=0)
        elif name == "Paste Into":
            self.PasteIntoGroup(append=3)
        elif name == "Toggle":
            self.ToggleScheduleSelection()
        elif name == "Up":
            self.MoveScheduleItemUp()   
                        
    def OnScheduleTreeActivated(self, event):
        self.OnScheduleItemEdit(None)        
        
    def OnScheduleTreeSelectionChanged(self, event=None):
        """ update the schedule item information """
        self._currentSelectionType = "schedule"
        self.UpdateScheduleInfo()
        self.UpdateScheduleToolbar()   
        self.UpdateToolbar()
            
    def OnScheduleTreeItemChecked(self, event):
        self.schedList.Select(self.scheduleSelection)    
        self.SaveStateToUndoStack()
        self.ClearRedoStack()
        groupSel = self.GetGroupListIndex(self.groupSelection)
        idx = self.schedList.GetItemIndex(self.scheduleSelection)
        for n, (j, k) in enumerate(self._data[groupSel]["schedules"]):
            if not j == idx:
                continue 
            self._data[groupSel]["schedules"][n][1]["checked"] = self.schedList.GetCheckedState(self.scheduleSelection)
            break
            
    def OnScheduleTreePaste(self, append=0):
        """ user pastes on the schedule list """
        
        if self._clipboard["toplevel"] is False:
            if not self.scheduleSelection.IsOk():
                self.toolTip.message = "Cannot paste action item outside of a schedule"
                return

        if not self.scheduleSelection.IsOk():
            self.AppendSchedules()
            
        # ensure that a non-schedule item is inserted in schedule
        # rather than a sibling of a schedule
        elif self.schedList.IsTopLevel(self.scheduleSelection):
            if self._clipboard["toplevel"] is False:
                self.PasteIntoGroup(3)
            else:
                self.PasteIntoGroup(0)
        else:        
            self.PasteIntoGroup(2)
        # clear the clipboard
        # if self._clipboard["type"] == "cut":
            # self._clipboard = None
            # self.UpdateToolbar()
            
        self.UpdateScheduleImageList()
            
    def OnSize(self, event):
        wx.CallAfter(self.UpdateToolbarSize)
        event.Skip()
        
    def OnToolBar(self, event):
        e = event.GetEventObject()
        id = event.GetId()
        label = e.GetLabel(id)

        if label == "Add Group":
            self.ShowAddGroupDialog()
        elif label == "Close":
            self.CloseFile()    
        elif label == "Cut":
            self.CutSelection()
        elif label == "Disable Schedule Manager":
            self.DisableScheduleManager()
        elif label == "Enable Schedule Manager":
            self.EnableScheduleManager()
        elif label == "Import":
            self.ShowImportDialog()    
        elif label == "New":
            self.CloseFile()
        elif label == "Open":
            self.OpenFile()    
        elif label == "Remove Group":
            self.DeleteGroupItem()
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
    
    def PasteIntoGroup(self, append=0):
        if self._clipboard is None:
            return
        self.SaveStateToUndoStack()
        self.ClearRedoStack()
        
        clip = self._clipboard
        name, schedules, origin = clip["name"], clip["schedules"], clip["origin"]
        index = self.GetGroupListIndex(self.groupSelection)
        
        # no items in this group
        if not self.schedList.GetFirstItem().IsOk():
            self.SetScheduleTree(schedules)
            self._data[index]["schedules"] = schedules
        
        # append
        elif append == 0 and clip["toplevel"] is True:
            if self.scheduleSelection.IsOk():
                toplevel = self.schedList.GetTopLevelParent(self.scheduleSelection)
                previous = self.schedList.GetLastSibling(toplevel)
            else:
                previous = self.schedList.GetLastChild(self.schedList.GetRootItem())
            schedules = self.GetUniqueSchedules(schedules)
            newItem = self.schedList.InsertSubTree(previous, schedules)
            
        # insert schedule
        elif append == 1 and clip["toplevel"] is True:
            toplevel = self.schedList.GetTopLevelParent(self.scheduleSelection)
            previous = self.schedList.GetPreviousSibling(toplevel)
            schedules = self.GetUniqueSchedules(schedules)
            newItem = self.schedList.InsertSubTree(previous, schedules)
         
        # insert schedule after 
        elif append == 2 and clip["toplevel"] is True:
            toplevel = self.schedList.GetTopLevelParent(self.scheduleSelection)
            schedules = self.GetUniqueSchedules(schedules)
            newItem = self.schedList.InsertSubTree(toplevel, schedules)
            
        # append schedule contents inside another item 
        elif append == 3 and clip["toplevel"] is True:
            toplevel = self.schedList.GetTopLevelParent(self.scheduleSelection)
            last = self.schedList.GetLastChild(self.scheduleSelection)
            extract = self.ExtractContentsFromSchedules(schedules)
            for n in sorted(extract.keys()):
                e = extract[n]
                self.schedList.InsertSubTree(last, e)
                
        # append
        elif append == 0 and clip["toplevel"] is False:
            previous = self.schedList.GetLastSibling(self.scheduleSelection)
            newItem = self.schedList.InsertSubTree(previous, schedules)
            
        # insert schedule
        elif append == 1 and clip["toplevel"] is False:
            previous = self.schedList.GetPreviousSibling(self.scheduleSelection)
            newItem = self.schedList.InsertSubTree(previous, schedules)
         
        # insert schedule after 
        elif append == 2 and clip["toplevel"] is False:
            newItem = self.schedList.InsertSubTree(self.scheduleSelection, schedules)
            
        # append schedule contents inside another item 
        elif append == 3 and clip["toplevel"] is False:
            child = self.schedList.GetFirstChild(self.scheduleSelection)
            if not child.IsOk():
                self.schedList.InsertSubTree(child, schedules)
            else:    
                last = self.schedList.GetLastChild(child)
                self.schedList.InsertSubTree(last, schedules)
        
        # if clip["type"] == "cut":
            # self._clipboard = None
            # self.UpdateToolbar()
            
        self._data[index]["schedules"] = self.GetScheduleTree()
        self.UpdateScheduleImageList()
        
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
    
    def RestoreState(self, state):
        # print("Restore State", state)
        self._data = {}
        self.groupList.DeleteAllItems()
        self.schedList.DeleteAllItems()
        
        self.SetGroupTree(state["data"])
        self.groupList.SelectItemByOrder(state["groupSel"])
        self.OnGroupItemSelectionChanged()
        self.schedList.SelectItemByOrder(state["schedSel"])
        self.UpdateGroupToolbar()
        self.UpdateScheduleToolbar()
        self.UpdateToolbar()
        self._currentSelectionType = state["currentSelectionType"]
        
    def SaveData(self):
        jsonData = self.GetDataForJSON()
        if self._appConfig["currentFile"] is not False:
            self.SaveDataToJSON(self._appConfig["currentFile"], jsonData)
            self.commandState = 0
            self.UpdateTitlebar()
            return
            
        wildcard = "JSON files (*.json)|*.json"
        file = wx.FileDialog(self, 
                             defaultDir="",
                             message="Save File", 
                             wildcard=wildcard,
                             style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
        
        if file.ShowModal() == wx.ID_CANCEL:
            return
           
        filePath = file.GetPath()   
        self._appConfig["currentFile"] = filePath
        self.SaveDataToJSON(self.configPath, self._appConfig)
        self.SaveDataToJSON(self._appConfig["currentFile"], jsonData)
        self.commandState = 0
        self.UpdateRecentFiles(filePath)
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
        
        filePath = file.GetPath()
        jsonData = self.GetDataForJSON()
        self._appConfig["currentFile"] = filePath
        self.SaveDataToJSON(self.configPath, self._appConfig)
        self.SaveDataToJSON(filePath, jsonData)
        
        self.commandState = 0
        self.UpdateRecentFiles(filePath)
        
    def SaveScheduleTreeToData(self):
        """ cache schedule tree to selected group item in data """
        schedules = self.GetScheduleTree()
        for item, data in self._data.items():
            if self.groupSelection != item:
                continue
            self._data[self.groupSelection]["schedules"] = schedules
            
    def SaveStateToUndoStack(self):
        logging.info("Save State To Undo Stack")
        n = self._appConfig["maxUndoCount"]
        if n == 0:
            pass
        else:    
            state = self.GetCommandState()
            self._undoStack.append(state)
            if len(self._undoStack) > n:
                del self._undoStack[0]
        self.commandState += 1        
        self.UpdateToolbar()
        self.UpdateTitlebar()
    
    def SetGroupTree(self, data):
        """ set the group list tree """
        for idx in sorted([int(x) for x in data.keys() if x != "__version__"]):
            item = self.groupList.AppendItemToRoot(data[str(idx)]["columns"]["0"])
            self.groupList.CheckItem(item, data[str(idx)]["checked"])
            self._data[item] = {"checked": data[str(idx)]["checked"], 
                                "schedules": data[str(idx)]["schedules"]}
                                
        self.UpdateGroupImageList()
        self.groupList.UnselectAll()
        
    def SetRecentFiles(self):
        """ called once on start-up to insert recent file menu items """
        if self._appConfig["keepFileList"] == False:
            return
            
        for filePath in self._appConfig["fileList"]:
            item = wx.MenuItem(id=wx.ID_ANY, text=filePath)
            self._fileListMenuItems[filePath] = item            
            self.Bind(wx.EVT_MENU, self.OnRecentFile, item)
            item.SetHelp("Open File: {0}".format(filePath))
            self.menuFile.Insert(self.menuFile.GetMenuItemCount()-len(self._fileList)-1, item)
            self._fileList.append(filePath)
            
    def SetScheduleTree(self, data):
        """ set the schedule list tree """
        self.schedList.SetTree(data)
        self.UpdateScheduleImageList()

    def SetStatusBar(self, event=None):
        """ update status bar when selecting a tree item on sequence"""
        selection = self.schedList.GetSelection()
        status = self.schedList.GetItemText(selection)
        self.GetTopLevelParent().SetStatusText(status)

        if event:
            event.Skip() 
            
    def SetupAcceleratorTable(self):
        self.accelTable = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('N'), wx.ID_NEW),
            (wx.ACCEL_CTRL, ord('O'), wx.ID_OPEN),
            (wx.ACCEL_CTRL, ord('S'), wx.ID_SAVE),
            (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('S'), wx.ID_SAVEAS),
            (wx.ACCEL_CTRL, ord('W'), wx.ID_CLOSE),
            # (wx.ACCEL_CTRL, ord('I'), wx.ID_CDROM),
            (wx.ACCEL_ALT, ord('P'), wx.ID_PREFERENCES),
            (wx.ACCEL_CTRL, ord('Q'), wx.ID_EXIT),
            (wx.ACCEL_CTRL, ord('Y'), wx.ID_REDO),
            (wx.ACCEL_CTRL, ord('Z'), wx.ID_UNDO),
            (wx.ACCEL_CTRL, ord('C'), wx.ID_COPY),
            (wx.ACCEL_CTRL, ord('X'), wx.ID_CUT),
            (wx.ACCEL_CTRL, ord('V'), wx.ID_PASTE),
            (wx.ACCEL_CTRL, ord('H'), wx.ID_HELP),
            # (wx.ACCEL_CTRL, ord('I'), self._ids["Import"]),
            (wx.ACCEL_CTRL, ord('G'), self._ids["group_Add Group"]),
            # (wx.ACCEL_NORMAL, wx.WXK_DELETE, self._ids["schedule_Delete"]),
            # (wx.ACCEL_NORMAL, wx.WXK_DELETE, self._ids["group_Delete"]),
            (wx.ACCEL_CTRL, 304, wx.ID_ABOUT), # F1
          ])
        self.SetAcceleratorTable(self.accelTable)
        
    def SetupHotkeys(self):
        """ hook global hotkeys """
        
        # see https://github.com/boppreh/keyboard/issues/139
        # should be fixed in future, but now, we only unhook
        # if hooks are created in the first place
        try:
            keyboard.unhook_all()
        except AttributeError:
            pass
        keyboard.add_hotkey(self._appConfig["toggleSchedManHotkey"], self.ToggleScheduleManager)
            
    def ShowAboutDialog(self):
        if not self._aboutDialog:
            self._aboutDialog = AboutDialog(self)
            self._aboutDialog.Bind(wx.EVT_CLOSE, self.OnAboutDialogClose)
        self._aboutDialog.Show()    
            
    def ShowAddGroupDialog(self, uid=None, caption="Add Group", schedules=[], append=0):
        """ 
        optional to pass schedules/custom caption. In cases, such as copy and paste
        where we use this dialog
        
        append option: 0 = append, 1 = before selected item, 2 = after selected item
        """
        m = "Group Name:"
        groupNames = self.GetGroupNames()
        if uid is None:
            # find unique group name
            i = 1
            b = "group_"
            uid = b + str(i)
            while uid in groupNames:
                i += 1
                uid = b + str(i)
        else:
            i = 1
            b = uid
            uid = b
            while uid in groupNames:
                uid = b + "_%d" % i
                i += 1
                        
        while True:            
            dlg = wx.TextEntryDialog(self, message=m, caption=caption, value=uid)
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
            if append == 0: # append
                newItem = self.groupList.AppendItemToRoot(newName)
            elif append == 1: # paste before
                previous = self.groupList.GetPreviousSibling(self.groupSelection)
                if previous == -1:
                    newItem = self.groupList.PrependItem(self.groupListRoot, newName)
                else:    
                    newItem = self.groupList.InsertItem(self.groupListRoot, previous, newName)
            elif append == 2: # paste after
                newItem = self.groupList.InsertItem(self.groupListRoot, self.groupSelection, newName)
                
            self.schedList.DeleteAllItems()

            self._data[newItem] = {}
            self._data[newItem]["checked"] = 0
            self._data[newItem]["schedules"] = schedules
            self.OnGroupItemSelectionChanged()
            self.SetScheduleTree(schedules)

            self.groupList.Select(self.groupList.GetFirstItem())
            self.groupList.Select(newItem)
            self.groupList.SetFocus()
            self.UpdateGroupToolbar()
            self.UpdateScheduleToolbar()
            self.UpdateGroupImageList()
            self.UpdateScheduleInfo()
            self.ClearRedoStack()
            return newItem
            
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
        self.UpdateScheduleImageList()
        self.SaveScheduleTreeToData()
        
    def ShowCheckForUpdatesDialog(self):
        print("Checking For Updates...")
        import updatechecker
        dlg = updatechecker.CheckForUpdates(self, __version__)
        dlg.ShowModal()
        
    def ShowImportDialog(self):
        message = "Not yet implemented"
        dlg = wx.MessageDialog(self,
                               message,
                               caption="Import Schedule File")
        dlg.ShowModal()
                
    def ShowSettingsDialog(self):
        try:
            self._settingsDialog.Show()
        except:
            self._settingsDialog = SettingsFrame(self)
            self._settingsDialog.SetValue(self._appConfig)    
            self._settingsDialog.Show()            
        
        self._settingsDialog.Raise()    
        
    def ShowUserGuide(self):
    
        try:
            self._userGuideDialog.Show()
            self._userGuideDialog.Raise()
        except:    
            self._userGuideDialog = UserGuideFrame(self)
            self._userGuideDialog.CentreOnParent()
            self._userGuideDialog.Raise()
            self._userGuideDialog.Show()
    
    def ToggleGroupSelection(self):
        logging.debug("ToggleGroupSelection")
        if not self.groupSelection.IsOk():
            return
        self.SaveStateToUndoStack()
        self.ClearRedoStack()
        checked = self.groupList.GetCheckedState(self.groupSelection)
        if checked == 1:
            self.groupList.UncheckItem(self.groupSelection)
            checked = 0
        else:
            self.groupList.CheckItem(self.groupSelection)
            checked = 1
            
        self.UpdateGroupImageList()
        index = self.GetGroupListIndex(self.groupSelection)
        self._data[index]["checked"] = checked        
            
    def ToggleScheduleManager(self):
        if self._tools["Enable Schedule Manager"].GetLabel() == "Enable Schedule Manager":
            self.EnableScheduleManager()
        else:       
            self.DisableScheduleManager()
                
    def ToggleScheduleSelection(self):
        if not self.scheduleSelection.IsOk():
            return
        self.SaveStateToUndoStack()
        self.ClearRedoStack()
        checked = self.schedList.GetCheckedState(self.scheduleSelection)
        if checked == 1:
            self.schedList.UncheckItem(self.scheduleSelection)
            checked = 0
        else:
            self.schedList.CheckItem(self.scheduleSelection)
            checked = 1
            
        index = self.GetGroupListIndex(self.groupSelection)
        self._data[index]["schedules"] = self.GetScheduleTree()
                    
    def UpdateRecentFiles(self, filePath):
        if self._appConfig["keepFileList"] == False:
            return
        if filePath in self._fileList:
            self.menuFile.Delete(self._fileListMenuItems[filePath])
            del self._fileListMenuItems[filePath]
            del self._fileList[self._fileList.index(filePath)]
            
        self._fileListMenuItems[filePath] = item = wx.MenuItem(id=wx.ID_ANY, text=filePath)
        self.Bind(wx.EVT_MENU, self.OnRecentFile, item)
        item.SetHelp("Open File: {0}".format(filePath))
        self.menuFile.Insert(self.menuFile.GetMenuItemCount()-len(self._fileList)-1, item)
        self._fileList.insert(0, filePath)
        self.UpdateSettingsDict({"fileList":self._fileList})
     
    def UpdateGroupImageList(self):
        item = self.groupList.GetFirstItem()
        while item.IsOk():
            if self.groupList.GetCheckedState(item) == 1:
                self.groupList.SetItemImage(item, self.imageListIndex("groupchecked"))
            else:
                self.groupList.SetItemImage(item, self.imageListIndex("group"))
            item = self.groupList.GetNextItem(item)
            
    def UpdateGroupToolbar(self):
        selection = self.groupList.GetSelection()
        state = True
        if not selection.IsOk():
            state = False
            self._currentSelectionType = None
        else:    
            self._currentSelectionType = "group"
        for label, btn in self.groupBtns.items():
            if label == "Add Group":
                btn.Enable()
                continue 
            btn.Enable(state)
            
        if selection.IsOk():
            if self.groupList.GetFirstItem() == selection:
                self.groupBtns["Up"].Disable()
            if not self.groupList.GetNextSibling(selection).IsOk():
                self.groupBtns["Down"].Disable()
            
        self.toolbar.EnableTool(wx.ID_REMOVE, state)
            
    def UpdateScheduleInfo(self):
        if not self.scheduleSelection.IsOk():
            self.infoSched.SetValue("")
            self.infoSchedButton.Hide()
            self.infoPanelSizer.Layout()
            self.infoSched.Refresh() 
            return
            
        try:
            text = self.schedList.GetItemText(self.scheduleSelection)
            if self.schedList.IsTopLevel(self.scheduleSelection):
                name = "schedule"
                _, params = text.split(DELIMITER)
            else:
                name, params = text.split(DELIMITER)
            params = make_tuple(params)
            
            self.infoSched.SetValue(name)
            for x, y in params:
                self.infoSched.AppendText("\n - {0} = {1}".format(x, y))
            self.infoSchedButton.Show()
            self.infoPanelSizer.Layout()
            w, h = self.infoSchedButton.GetSize()
            if w > h:
                d = h
            else:
                d = w
            self.infoSchedButton.SetBitmap(self.GetBitmapFromImage(name, (d, d)))
            self.infoSchedButton.SetLabel(name) 
        except Exception as e:
            print(e)
            self.infoSched.SetValue("")
            self.infoSchedButton.Hide()
            self.infoPanelSizer.Layout()
           
        self.infoSched.Refresh()   
    
    def UpdateScheduleToolbar(self):
        if not self.scheduleSelection.IsOk():
            for label, btn in self.schedBtns.items():
                if label == "Add Schedule":
                    continue
                btn.Disable()
            # stop user from being able add function     
            self.cboxFunctions.Disable()
            self.btnAddFunction.Disable()
        else:          
            # enable user to add function     
            self.cboxFunctions.Enable()
            self.btnAddFunction.Enable()
            
            self.schedBtns["Edit"].Enable()
            self.schedBtns["Toggle"].Enable()
            self.schedBtns["Delete"].Enable()
         
            if self.schedList.GetNextSibling(self.scheduleSelection).IsOk():   
                self.schedBtns["Down"].Enable()
            else:
                self.schedBtns["Down"].Disable()
                
            parent = self.schedList.GetItemParent(self.scheduleSelection)    
            if self.schedList.GetFirstChild(parent) != self.scheduleSelection:   
                self.schedBtns["Up"].Enable()
            else:
                self.schedBtns["Up"].Disable()
            
        if self.groupSelection.IsOk():
            self.schedBtns["Add Schedule"].Enable()
                        
    def UpdateScheduleImageList(self):
        item = self.schedList.GetFirstItem()
        while item.IsOk():
            if self.schedList.GetItemParent(item) == self.schedList.GetRootItem():
                self.schedList.SetItemImage(item, self.imageListIndex("schedule"))
            else:
                action = self.schedList.GetItemText(item).split(DELIMITER)[0]
                try:
                    self.schedList.SetItemImage(item, self.imageListIndex(action.lower()))
                except:
                    pass
            item = self.schedList.GetNextItem(item)
            
    def UpdateSelectedItemInData(self):
        """Updates application data for the currently selected schedule item"""
        schedSel = self.scheduleSelection
        if not schedSel.IsOk():
            return
        idx = self.schedList.GetItemIndex(schedSel)
        groupSel = self.groupSelection
        for n, (j, k) in enumerate(self._data[groupSel]["schedules"]):
            if not j == idx:
                continue 
            self._data[groupSel]["schedules"][n][1]["columns"]["0"] = self.schedList.GetItemText(schedSel)
            break
    
    def UpdateSettingsDict(self, data):
        self._appConfig.update(data)
        self.SaveDataToJSON(self.configPath, self._appConfig)
        
        if self._appConfig["keepFileList"] == False:
            self.ClearRecentFiles()
        
        n = self._appConfig["maxUndoCount"]
        if n == 0:
            self._undoStack = []
            self._redoStack = []
        elif len(self._undoStack) > n:
            self._undoStack = self._undoStack[len(self._undoStack)-n:]
        
        self.SetupHotkeys()
        self.UpdateTrayIcon()
        self.UpdateToolbarSize()
        self.UpdateToolbar()
        self.UpdateTitlebar()
        
    def UpdateTitlebar(self):
        unsaved = ""
        if self.commandState != 0:
            unsaved = "*"
        
        try:
            _, name = os.path.split(self._appConfig["currentFile"])
            self.SetTitle("{0}{1} - {2}".format(unsaved, name, __title__))
        except:
            self.SetTitle("{0}New File.json - {1}".format(unsaved, __title__))
            
    def UpdateToolbar(self):
        if self._currentSelectionType:
            self.toolbar.EnableTool(wx.ID_CUT, True)
            self.toolbar.EnableTool(wx.ID_COPY, True)
        elif not self.groupList.GetSelection().IsOk():
            self.toolbar.EnableTool(wx.ID_CUT, False)
            self.toolbar.EnableTool(wx.ID_COPY, False)
            
        if self._clipboard:
            self.toolbar.EnableTool(wx.ID_PASTE, True)
        else:
            self.toolbar.EnableTool(wx.ID_PASTE, False)
            
        if self._undoStack:
            self.toolbar.EnableTool(wx.ID_UNDO, True)
        else:    
            self.toolbar.EnableTool(wx.ID_UNDO, False)
            
        if self._redoStack:
            self.toolbar.EnableTool(wx.ID_REDO, True)
        else:
            self.toolbar.EnableTool(wx.ID_REDO, False)
        
    def UpdateToolbarSize(self):
        
        if not self.toolbar:
            return 
            
        sizeChoices = [16,32,48,64,128,256]
        toolSize = int(self._appConfig["toolbarSize"]), int(self._appConfig["toolbarSize"])            
        width = self.GetSize()[0]
        toolCount = self.toolbar.GetToolsCount()
        if toolSize[0] * toolCount > width:
            idx = sizeChoices.index(toolSize[0])
            newSize = None
            for x in reversed(sizeChoices[:idx]):
                # # try to set the largest toolbar icon size possible
                if x * toolCount <= width:
                    toolSize = x, x
                    self._overrideToolSize = x
                    break
        else:
           self._overrideToolSize = None
        
        if self.toolbar.GetToolBitmapSize() == toolSize:
            return
            
        self.toolbar.SetToolBitmapSize(toolSize)
        for x in range(toolCount):
            tool = self.toolbar.GetToolByPos(x)
            label = tool.GetLabel()
            if not label:
                continue
            tool.SetNormalBitmap(self._toolbarBitmaps[toolSize[0]][label])
                      
        self.toolbar.Realize()
        
    def UpdateTrayIcon(self):
        if self._appConfig["showTrayIcon"] is True:
            if not self.taskBarIcon:
                self.CreateTrayIcon()
        else:
            if self.taskBarIcon:
                self.taskBarIcon.RemoveTray()
                self.taskBarIcon = None
   
if __name__ == "__main__":
    app = wx.App()
    mainFrame = Main()
    app.MainLoop()