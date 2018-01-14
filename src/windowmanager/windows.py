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

def CloseWindow(title, matchcase=False, matchstring=True):
    """
    Get handles and their respective titles. If condition is
    matched, try to close window by handle
    """

    titles = []
    def callback(hwnd, strings):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            # left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            # if window_title and right-left and bottom-top:
                # strings.append('0x{:08x}: "{}"'.format(hwnd, window_title))
            logging.info("hwnd: %s, title: %s" % (hwnd, window_title))
            titles.append((hwnd, window_title))
        return True
    win32gui.EnumWindows(callback, titles)

    def close_window(hwnd):
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            # win32gui.PostQuitMessage(hwnd)
        except:
            pass

    handles = []
    if matchcase and matchstring:
        for hwnd, t in titles:
            if title == t:
                handles.append(hwnd)

    elif matchcase and not matchstring:
        for hwnd, t in titles:
            if title in t:
                handles.append(hwnd)

    elif not matchcase and not matchstring:
        for hwnd, t in titles:
            if title.lower() in t.lower():
                handles.append(hwnd)

    elif not matchcase and matchstring:
        for hwnd, t in titles:
            if title.lower() == t.lower():
                handles.append(hwnd)

    for hwnd in handles:
        close_window(hwnd)

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

# def GetWindowPos(progName, title):
    # handle = GetHandle(progName, title)
    # if handle == 0:
        # return
    # x, y, w, h = win32gui.GetClientRect(handle)
    # print(x,y,w,h)
    # return [x, y, w, h]
    
def GetWindowRect(progName, title):
    handle = GetHandle(progName, title)
    if handle == 0:
        return
    x1, y1, x2, y2 = win32gui.GetWindowRect(handle)
    print(title, [x1, y1, x2, y2])
    return [x1, y1, x2, y2]

def KillProcess(pid):
    output = subprocess.check_output(["kill"] + [pid]).decode("utf-8").strip()
    if "arguments must be process or job IDs" in output:
        pass
    if "No such process" in output:
        pass
        
def MouseClickRelative(x, y, w=None, h=None, originalpos=False):
    pass
    
def MoveWindow(title, progName, x1, y1, w, h):

    handle = GetHandle(title, progName)
    print(handle)
    if not handle:
        return
        
    if w is None: # size not defined
        tmpX1, tmpY1, tmpX2, tmpY2 = win32gui.GetWindowRect(handle)
        w = tmpX2 - tmpX1
        h = tmpY2 - tmpY1
    
    win32gui.MoveWindow(handle, x1, y1, w, h, True)
    
def SetForegroundWindow(title, progName):
    """ activate the first matched window, and if no match found, return None """
    handle = GetHandle(title, progName)
    print(handle)
    if not handle:
        return
    win32gui.SetForegroundWindow(handle)

def SetWindowSize(title, progName, w, h):

    handle = GetHandle(title, progName)
    print(handle)
    if not handle:
        return
        
    x1, y1, _, _ = win32gui.GetWindowRect(handle)
    win32gui.MoveWindow(handle, x1, y1, w, h, True)        