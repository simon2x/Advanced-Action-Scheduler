# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler> 

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version. 
"""

import base
import logging
import platform
import pyautogui
import time
import webbrowser

from ast import literal_eval as make_tuple
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
import apscheduler.events as apsevents

PLATFORM = platform.system()
if PLATFORM == "Windows":
    import actions.windowsactionmanager as actman
elif PLATFORM == "Linux":
    import actions.linuxactionmanager as actman

DELIMITER = " ➡ "

class Manager:

    def __init__(self, parent):

        self._parent = parent
        self._schedules = {}
        self._schedData = {}
    
    def AddSchedule(self, groupName, schedStr):
        """ parse the schedule string and add schedule """
            
        schedName, schedTime = schedStr.split(DELIMITER)
        schedTime = make_tuple(schedTime)
        schedTime = {k:v for k,v in schedTime}
        
        params = {}
        for timeVar in ["dof","h","m","s"]:
            if timeVar in schedTime:
                params[timeVar] = ",".join([t for t in schedTime[timeVar]])
            else:
                params[timeVar] = "*"

        schedule = BackgroundScheduler()
        cronTrig = CronTrigger(day_of_week=params["dof"],
                               hour=params["h"],
                               minute=params["m"],
                               second=params["s"])

        args = (groupName, schedName)
        schedule.add_job(self.OnSchedule, args=[args], trigger=cronTrig)

        # attach a listener to schedule events
        # schedule.add_listener(self.OnScheduleEvent, 
                              # apsevents.EVENT_JOB_EXECUTED|apsevents.EVENT_JOB_ERROR)
        try:     
            self._schedules[groupName].append((schedName, schedule))
        except:
            self._schedules[groupName] = [(schedName, schedule)]
            
    def AddScheduleItem(self, groupName, schedName, index, schedItemStr):
        """ parse the schedItemStr to an action """
        action, paramStr = schedItemStr.split(DELIMITER)
        params = {k:v for k,v in make_tuple(paramStr)}
        self._schedData[groupName][schedName].append((index, action, params))

    def DoAction(self, action, kwargs):
        logging.info("Executing action: %s" % action)
        logging.info("parameters: %s" % str(kwargs))
        
        if action == "CloseWindow":
            actman.CloseWindow(kwargs)
            
        elif action == "Delay":
            delay = kwargs["delay"]
            value = float(delay[:-1])
            time.sleep(value) #remove the 's'
            self.SendLog(["-","Delayed for %s" % delay])

        elif action == "KillProcess":
            pass

        elif action == "IfWindowOpen":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            matchstring = kwargs["matchstring"]

            if not actman.FindWindow(window, matchcase):
                # no window found
                self.SendLog(["-","IfWindowOpen: %s ...found" % window])
                return False

            self.SendLog(["-","IfWindowOpen: %s ...not found" % window])
            return True

        elif action == "IfWindowNotOpen":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            matchstring = kwargs["matchstring"]

            if actman.FindWindow(window, matchcase):
                # window found
                self.SendLog(["-","IfWindowNotOpen: %s ...found" % window])
                return False

            self.SendLog(["-","IfWindowNotOpen: %s ...not found" % window])
            return True

        elif action == "MouseClickAbsolute":
            title, win_class = make_tuple(kwargs["window"])
            matchcase = kwargs["matchcase"]
            resize = kwargs["resize"]
            offsetx = kwargs["offsetx"]
            offsety = kwargs["offsety"]
            width = kwargs["width"]
            height = kwargs["height"]
            x = kwargs["x"]
            y = kwargs["y"]

            actman.SetWindowSize(title, win_class, offsetx, offsety, width, height)
            pyautogui.click(x=x, y=y)

        elif action == "MouseClickRelative":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            resize = kwargs["resize"]
            offsetx = kwargs["offsetx"]
            offsety = kwargs["offsety"]
            width = kwargs["width"]
            height = kwargs["height"]
            x = kwargs["x"]
            y = kwargs["y"]

            actman.MouseClickRelative(title, win_class, offsetx, offsety, width, height)

        elif action == "OpenURL":
            url = kwargs["url"]
            browser = kwargs["browser"]
            newwindow = kwargs["newwindow"]
            autoraise = kwargs["autoraise"]
            print (webbrowser._browsers)
            return
            if browser != "system default":
                b = webbrowser.get(browser)
            else:
                b = webbrowser.get(browser)

            if newwindow and autoraise:
                b.open(newwindow, new=1, sautoraise=True)
            elif newwindow and not autoraise:
                b.open(newwindow, new=1, autoraise=False)
            elif not newwindow and autoraise:
                b.open(newwindow, new=0, autoraise=True)
            elif not newwindow and not autoraise:
                b.open(newwindow, new=0, autoraise=False)

        elif action == "Power":
            action = kwargs["action"]
            alert = kwargs["alert"]

        elif action == "StopSchedule":
            schedule = kwargs["schedule"]

        elif action == "StartSchedule":
            schedule = kwargs["schedule"]

        elif action == "SwitchWindow":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            matchstring = kwargs["matchstring"]

        return True
        
    def GetParent(self):
        return self._parent

    def OnSchedule(self, args):
        groupName, schedName = args
         
        childIgnore = [] 
        for index, action, params in self._schedData[groupName][schedName]:
            a = self.DoAction(action, params)

            # if a is False:
                # # returned false, therefore action condition was not met
                # # we delete the actions children
                # for j,k in enumerate(reversed(indices)):
                    # if not j.startswith(i):
                        # continue
                    # del indices[k]
                # continue

        self.SendLog(["",
                      "Executed schedule %s from group: %s" % (schedName, groupName)])

    def SendLog(self, message):
        """ pass message to schedule manager lis """
        parent = self.GetParent()
        parent.AppendLogMessage(message)

    def SetSchedules(self, data):
        """ 
        receive a tuple list of (groupName, schedList)
        """

        # stop and remove schedules first
        self.Stop()
        
        # process schedule data
        for groupName, schedList in data.items():
            self._schedData[groupName] = {}
            childIgnore = []
            currentSched = None
            for index, itemData in schedList:
                # is a schedule?
                if "," not in index:
                    if itemData["checked"] == 0:
                        childIgnore.append(index+",")
                        continue
                    schedStr = itemData["columns"]["0"]
                    currentSched, _ = schedStr.split(DELIMITER)
                    self._schedData[groupName][currentSched] = []
                    self.AddSchedule(groupName, schedStr)
                    continue
                for ignore in childIgnore:
                    if index.startswith(ignore):
                        continue
                if itemData["checked"] == 0:
                    childIgnore.append(index+",")
                    continue 
                schedItemStr = itemData["columns"]["0"]    
                self.AddScheduleItem(groupName, currentSched, index, schedItemStr)

    def Start(self):
        for groupName, groupScheds in self._schedules.items():
            for schedName, schedule in groupScheds:
                schedule.start()
                self.SendLog(["-", "Started schedule {0} from {1} group".format(schedName, groupName)])

    def Stop(self):
        """ shutdown all schedules """
        for groupName, groupScheds in self._schedules.items():
            for schedName, schedule in groupScheds:
                schedule.shutdown()
                self.SendLog(["-", "Stopped schedule {0} from {1} group".format(schedName, groupName)])

        self.SendLog(["-", "All running schedules have been stopped"])

        # clear schedules and data
        self._schedules = {}
        self._schedData = {}

# END