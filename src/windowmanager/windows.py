# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler> 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. 
"""

import ctypes
import logging
import platform
import psutil
import subprocess
import time
import win32
import win32api
import win32con
import win32gui
import win32process

from ctypes import pointer, wintypes
from ast import literal_eval as make_tuple

lpdw_process_id = ctypes.c_ulong()
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId


ctypes.windll.kernel32.GetModuleHandleW.restype = wintypes.HMODULE
ctypes.windll.kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]

hMod = ctypes.windll.kernel32.GetModuleHandleW

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

def CloseWindow(handle):
    win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)
    
def GetHandle(progName, title):
    matchTitle = title
    foundHandle = []
    
    # filter out pids which match executable name
    pidList = [(p.pid, p.name()) for p in psutil.process_iter() if p.name() == progName]
    
    def enumWindowsProc(hwnd, lParam):
        """ append window titles which match a pid """
        if (lParam is None) or ((lParam is not None) and (win32process.GetWindowThreadProcessId(hwnd)[1] == lParam)):
            text = win32gui.GetWindowText(hwnd)
            if text:
                wStyle = win32api.GetWindowLong(hwnd, win32con.GWL_STYLE)
                if wStyle & win32con.WS_VISIBLE:
                    if text == matchTitle:
                        foundHandle.append(hwnd)
                        return

    def enumProcWnds(pid=None):
        win32gui.EnumWindows(enumWindowsProc, pid)
    
    for pid, pName in pidList:
        enumProcWnds(pid)
        if foundHandle:
            return foundHandle[0]
    
    return
    
def GetHandles(progName, matchTitle, **kwargs):
    match = {"matchcondition":0,
             "matchcase": True,
             "matchstring": True,
             "matches": 0}
    match.update(**kwargs)
    handles = []
    
    if match["matchcondition"] == 0:
        # match both window class and title
        pidList = [(p.pid, p.name()) for p in psutil.process_iter() if p.name() == progName]
    elif match["matchcondition"] == 1:
        # match window class only
        pidList = [(p.pid, p.name()) for p in psutil.process_iter() if p.name() == progName]
    elif match["matchcondition"] == 2:
        # match title only
        pidList = [(p.pid, p.name()) for p in psutil.process_iter()]
        
    def isMatch(title):
        print(title, matchTitle)
        if match["matchcase"] is True:
            if match["matchstring"] is True:
                if title == matchTitle:
                    return True
            else:
                if title in matchTitle:
                    return True
        else:
            title = title.lower()
            if match["matchstring"] is True:
                if title == matchTitle.lower():
                    return True
            else:
                if title in matchTitle.lower():
                    return True
        
        return False           
    
    def enumWindowsProc(hwnd, lParam):
        """ append window titles which match a pid """
        if (lParam is None) or ((lParam is not None) and (win32process.GetWindowThreadProcessId(hwnd)[1] == lParam)):
            text = win32gui.GetWindowText(hwnd) # window title
            if text:
                wStyle = win32api.GetWindowLong(hwnd, win32con.GWL_STYLE)
                if wStyle & win32con.WS_VISIBLE:
                    if isMatch(text) is True:
                        handles.append(hwnd)
                        
    def enumProcWnds(pid=None):
        win32gui.EnumWindows(enumWindowsProc, pid)
    
    for pid, pName in pidList:
        enumProcWnds(pid)
        if len(handles) == match["matches"] and match["matches"] != 0:
            break
        
    return handles
    
def GetHostname():
    hostname = subprocess.check_output(["hostname"]).decode("utf-8").strip()
    return hostname

def GetProcessName(hwnd):
    threadID, ProcessID = win32process.GetWindowThreadProcessId(hwnd)
    procName = psutil.Process(ProcessID)
    appName = procName.name()
    return appName

def GetUsername():
    username = subprocess.check_output(["whoami"]).decode("utf-8").strip()
    return username

def GetWindowList():
    """ 
    returns window title list 
    based on this answer - https://stackoverflow.com/a/31280850
    """
    
    titles = []
    t = []
    pidList = [(p.pid, p.name()) for p in psutil.process_iter()]
    
    def enumWindowsProc(hwnd, lParam):
        """ append window titles which match a pid """
        if (lParam is None) or ((lParam is not None) and (win32process.GetWindowThreadProcessId(hwnd)[1] == lParam)):
            text = win32gui.GetWindowText(hwnd)
            if text:
                wStyle = win32api.GetWindowLong(hwnd, win32con.GWL_STYLE)
                if wStyle & win32con.WS_VISIBLE:
                    t.append("%s" % (text))
                    return

    def enumProcWnds(pid=None):
        win32gui.EnumWindows(enumWindowsProc, pid)
    
    for pid, pName in pidList:
        enumProcWnds(pid)
        if t:
            for title in t:                
                titles.append("('{0}', '{1}')".format(pName, title))
            t = []
    
    titles = sorted(titles, key=lambda x: x[0].lower())
    return titles
    
def GetWindowRect(handle):
    x1, y1, x2, y2 = win32gui.GetWindowRect(handle)
    # print([x1, y1, x2, y2])
    return [x1, y1, x2, y2]

def KillProcess(pid):
    output = subprocess.check_output(["kill"] + [pid]).decode("utf-8").strip()
    if "arguments must be process or job IDs" in output:
        pass
    if "No such process" in output:
        pass
        
def MoveWindow(handle, x1, y1, w, h):

    if w is None: # size not defined
        tmpX1, tmpY1, tmpX2, tmpY2 = win32gui.GetWindowRect(handle)
        w = tmpX2 - tmpX1
        h = tmpY2 - tmpY1
    
    win32gui.MoveWindow(handle, x1, y1, w, h, True)
    
def SetForegroundWindow(handle):
    win32gui.SetForegroundWindow(handle)

def SetWindowSize(handle, w, h):        
    x1, y1, _, _ = win32gui.GetWindowRect(handle)
    win32gui.MoveWindow(handle, x1, y1, w, h, True)        