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
import subprocess
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
            time.sleep(float(delay)) #remove the 's'
            self.SendLog("Delayed for {0} seconds".format(delay))
            
        elif action == "IfWindowOpen":
            window = kwargs["window"]
            kwargs["matches"] = 1
            if not actman.FindWindow(kwargs):
                self.SendLog("IfWindowOpen: %s ...not found" % window)
                return
            
            self.SendLog("IfWindowOpen: %s ...found" % window)
            return True

        elif action == "IfWindowNotOpen":
            window = kwargs["window"]
            kwargs["matches"] = 1
            if not actman.FindWindow(kwargs):
                self.SendLog("IfWindowNotOpen: %s ...not found" % window)
                return True

            self.SendLog("IfWindowNotOpen: %s ...found" % window)
            return

        elif action == "MouseClickAbsolute":
            window = kwargs["window"]
            actman.MouseClickAbsolute(kwargs)
            self.SendLog("MouseClickAbsolute: {0}".format(window))   
                       
        elif action == "MouseClickRelative":
            window = kwargs["window"]
            actman.MouseClickRelative(kwargs)
            self.SendLog("MouseClickRelative: {0}".format(window))   
            
        elif action == "NewProcess":
            # remove leading and trailing whitespace
            cmd = [s.strip() for s in kwargs["cmd"].split(",")]
            try:
                subprocess.call(cmd)
                self.SendLog("NewProcess: {0}".format(cmd))
            except FileNotFoundError as e:
                self.SendLog("NewProcess: {0}, {1}".format(cmd, e))
            except PermissionError as e:
                self.SendLog("NewProcess: {0}, {1}".format(cmd, e))
        
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
            kwargs["matches"] = 1
            actman.SwitchWindow(kwargs)

        return True
        
    def GetParent(self):
        return self._parent

    def OnSchedule(self, args):
        groupName, schedName = args
         
        childIgnore = () 
        for index, action, params in self._schedData[groupName][schedName]:
            if childIgnore and not index.startswith(childIgnore):
                continue
            
            a = self.DoAction(action, params)
            if not a:
                childIgnore + (index+",",)

        self.SendLog("Executed schedule %s from group: %s" % (schedName, groupName))

    def SendLog(self, message):
        """ pass message to schedule manager lis """
        parent = self.GetParent()
        parent.AddLogMessage(message)

    def SetSchedules(self, data):
        """ 
        receive a tuple list of (groupName, schedList)
        """

        # stop and remove schedules first
        self.Stop()
        
        childIgnore = ()
        # process schedule data
        for groupName, schedList in data.items():
            self._schedData[groupName] = {}
            currentSched = None
            for index, itemData in schedList:
                # is a schedule?
                if "," not in index:
                    if itemData["checked"] == 0:
                        childIgnore += (index+",",)
                        continue
                    schedStr = itemData["columns"]["0"]
                    currentSched, _ = schedStr.split(DELIMITER)
                    self._schedData[groupName][currentSched] = []
                    self.AddSchedule(groupName, schedStr)
                    continue
                    
                if itemData["checked"] == 0 or index.startswith(childIgnore):
                    childIgnore += (index+",",)
                    continue 
                schedItemStr = itemData["columns"]["0"]    
                self.AddScheduleItem(groupName, currentSched, index, schedItemStr)

    def Start(self):
        for groupName, groupScheds in self._schedules.items():
            for schedName, schedule in groupScheds:
                schedule.start()
                self.SendLog("Started schedule {0} from {1} group".format(schedName, groupName))

    def Stop(self):
        """ shutdown all schedules """
        for groupName, groupScheds in self._schedules.items():
            for schedName, schedule in groupScheds:
                schedule.shutdown(wait=False)
                self.SendLog("Stopped schedule {0} from {1} group".format(schedName, groupName))

        self.SendLog("All running schedules have been stopped")

        # clear schedules and data
        self._schedules = {}
        self._schedData = {}

# END