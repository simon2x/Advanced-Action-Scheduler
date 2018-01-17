# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler> 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. 
"""

import logging
import subprocess
import time
from ast import literal_eval as make_tuple

from windowmanager import windows as winman

def CloseWindow(kwargs):
    """
    Get handles and their respective titles. If condition is
    matched, try to close window by handle
    """
    progName, title = make_tuple(kwargs["window"])
    handles = winman.GetHandles(progName, title, **kwargs)
    print("handles", handles)
    for handle in handles:
        winman.CloseWindow(handle)
    return

def FindWindow(kwargs):
    progName, title = make_tuple(kwargs["window"])
    if winman.GetHandles(progName, title, **kwargs) == []:
        return False
    return True    

def KillProcess(pid):
    output = subprocess.check_output(["kill"] + [pid]).decode("utf-8").strip()
    if "arguments must be process or job IDs" in output:
        pass
    if "No such process" in output:
        pass
    
def MouseClickAbsolute(kwargs):
    progName, title = make_tuple(kwargs["window"])
    handles = winman.GetHandles(progName, title, **kwargs)
    x1, y1, w, h = kwargs["offsetx"], kwargs["offsety"], kwargs["width"], kwargs["height"]
    x, y = int(kwargs["x"]), int(kwargs["y"])
    for handle in handles:
        winman.RestoreWindow(handle)
        if kwargs["resize"] is True:
            winman.MoveWindow(handle, x1, y1, w, h)
            winman.SetForegroundWindow(handle)
        winman.LeftMouseClick(x, y)
    
def MouseClickRelative(kwargs):
    progName, title = make_tuple(kwargs["window"])
    handles = winman.GetHandles(progName, title, **kwargs)
    x1, y1, w, h = kwargs["offsetx"], kwargs["offsety"], kwargs["width"], kwargs["height"]
    x, y = x1 + int(kwargs["%width"] * w * 0.01), y1 + int(kwargs["%height"] * h * 0.01)
    for handle in handles:
        winman.RestoreWindow(handle)
        winman.SetForegroundWindow(handle)
        if kwargs["resize"] is True:
            winman.MoveWindow(handle, x1, y1, w, h)
        else:
            # calculate new relative positon
            x1, y1, w, h = winman.GetWindowRect(handle)
            x, y = x1 + int(kwargs["%width"] * w * 0.01), y1 + int(kwargs["%height"] * h * 0.01)
            
        winman.LeftMouseClick(x, y)