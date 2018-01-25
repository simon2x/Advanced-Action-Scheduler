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
import wx
import advwebbrowser

from ast import literal_eval as make_tuple
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
import apscheduler.events as apsevents

PLATFORM = platform.system()
if PLATFORM == "Windows":
    from win import actionmanager as actman
elif PLATFORM == "Linux":
    from linux import actionmanager as actman

DELIMITER = " ➡ "

class Manager:

    def __init__(self, parent):

        self._parent = parent
        self._schedules = {}
        self._schedData = {}
        self._webbrowser = advwebbrowser
        self._browsers = {} # registered browsers
    
    def AddSchedule(self, groupName, schedStr, enabled):
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
            self._schedules[groupName].append((schedName, schedule, enabled))
        except:
            self._schedules[groupName] = [(schedName, schedule, enabled)]
            
    def AddScheduleItem(self, groupName, schedName, index, schedItemStr):
        """ parse the schedItemStr to an action """
        action, paramStr = schedItemStr.split(DELIMITER)
        params = {k:v for k,v in make_tuple(paramStr)}
        self._schedData[groupName][schedName].append((index, action, params))

    def DoAction(self, groupName, schedName, action, kwargs):
        logging.info("Executing action: %s" % action)
        logging.info("parameters: %s" % str(kwargs))
        logData = {"Group": groupName, "Schedule": schedName, "Message": action}
        
        if action == "CloseWindow":
            actman.CloseWindow(kwargs)
            logData["Message"] = "SwitchWindow: {0}".format(kwargs["window"])  
            
        elif action == "Delay":
            delay = kwargs["delay"]
            time.sleep(float(delay)) #remove the 's'
            logData["Message"] = "Delay: {0} seconds".format(delay)
            self.SendLog(logData)
            
        elif action == "IfWindowOpen":
            window = kwargs["window"]
            kwargs["matches"] = 1
            if not actman.FindWindow(kwargs):
                logData["Message"] = "IfWindowOpen: {0} ...not found".format(window)
                self.SendLog(logData)
                return
            else:
                logData["Message"] = "IfWindowOpen: {0} ...found".format(window)
                self.SendLog(logData)

        elif action == "IfWindowNotOpen":
            window = kwargs["window"]
            kwargs["matches"] = 1
            if not actman.FindWindow(kwargs):
                logData["Message"] = "IfWindowOpen: {0} ...not found".format(window)
                self.SendLog(logData)
            else:
                logData["Message"] = "IfWindowOpen: {0} ...found".format(window)
                self.SendLog(logData)
                return

        elif action == "MouseClickAbsolute":
            window = kwargs["window"]
            actman.MouseClickAbsolute(kwargs)
            logData["Message"] = "MouseClickRelative: {0}".format(window)  
                       
        elif action == "MouseClickRelative":
            window = kwargs["window"]
            actman.MouseClickRelative(kwargs)
            logData["Message"] = "MouseClickRelative: {0}".format(window) 
            
        elif action == "NewProcess":
            # remove leading and trailing whitespace
            cmd = [s.strip() for s in kwargs["cmd"].split(",")]
            try:
                subprocess.call(cmd)
                logData["Message"] = "NewProcess: {0}".format(cmd)  
            except FileNotFoundError as e:
                logData["Message"] = "NewProcess: {0}, {1}".format(cmd, e)
            except PermissionError as e:
                logData["Message"] = "NewProcess: {0}, {1}".format(cmd, e)
        
        elif action == "OpenURL":
            self.OpenURL(kwargs)
            logData["Message"] = "OpenURL: {0}, {1}".format(kwargs["url"], kwargs["browser"])  
            
        elif action == "Power":
            logData["Message"] = "Power: {0}, {1}".format(kwargs["action"], kwargs["alert"])
            self.GetParent().OnPowerAction(kwargs)

        elif action == "SwitchWindow":
            kwargs["matches"] = 1
            actman.SwitchWindow(kwargs)
            logData["Message"] = "SwitchWindow: {0}".format(kwargs["window"])  

        self.SendLog(logData)    
        return True
        
    def GetParent(self):
        return self._parent

    def OnSchedule(self, args):
        groupName, schedName = args
                 
        childIgnore = () 
        for index, action, params in self._schedData[groupName][schedName]:
            if childIgnore and not index.startswith(childIgnore):
                continue
            print(action)    
            if action == "StopSchedule":
                schedule = params["schedule"]
                self.StartSchedule(groupName, schedule, enable=0)
                if schedule == schedName:
                    return
                    
            elif action == "StartSchedule":
                schedule = params["schedule"]
                self.StartSchedule(groupName, schedule, enable=1)
                if schedule == schedName:
                    return
                    
            else:
                a = self.DoAction(groupName, schedName, action, params)
                if not a:
                    childIgnore + (index+",",)

        logData = {"Group": groupName, "Schedule": schedName, "Message": "Executed Schedule"}
        self.SendLog(logData)

    def OpenURL(self, kwargs):
        url = kwargs["url"]
        browser = kwargs["browser"]
        browserclass = self._webbrowser.klasses[kwargs["browserclass"]]
        newwindow = kwargs["newwindow"]
        autoraise = kwargs["autoraise"]
        
        try:
            b = self._browsers[browser]
        except KeyError:
            self._webbrowser.register(browser, browserclass)
            b = self._webbrowser.get(browser)
            self._browsers[browser] = b
        except Exception as e:
            self.SendLog({"Message":"OpenURL: Error - {0}".format(e)})
            return
            
        if newwindow and autoraise:
            b.open(url, new=1, autoraise=True)
        elif newwindow and not autoraise:
            b.open(url, new=1, autoraise=False)
        elif not newwindow and autoraise:
            b.open(url, new=2, autoraise=True)
        elif not newwindow and not autoraise:
            b.open(url, new=2, autoraise=False)
        self.SendLog({"Message": "OpenURL: {1} ({0})".format(browser, url)})
        
    def SendLog(self, message):
        """ pass message to schedule manager lis """
        parent = self.GetParent()
        wx.CallAfter(parent.AddLogMessage, message)

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
                    # if itemData["checked"] == 0:
                        # childIgnore += (index+",",)
                        # continue
                    schedStr = itemData["columns"]["0"]
                    currentSched, _ = schedStr.split(DELIMITER)
                    self._schedData[groupName][currentSched] = []
                    self.AddSchedule(groupName, schedStr, itemData["checked"])
                    continue
                    
                if itemData["checked"] == 0 or index.startswith(childIgnore):
                    childIgnore += (index+",",)
                    continue 
                schedItemStr = itemData["columns"]["0"]    
                self.AddScheduleItem(groupName, currentSched, index, schedItemStr)

    def Start(self):
        for groupName, groupScheds in self._schedules.items():
            for schedName, schedule, enabled in groupScheds:
                if enabled == 0:
                    continue
                schedule.start()
                self.SendLog({"Message":"Started schedule {0} from {1} group".format(schedName, groupName)})

    def Stop(self):
        """ shutdown all schedules """
        for groupName, groupScheds in self._schedules.items():
            for schedName, schedule, enabled in groupScheds:
                if enabled == 0:
                    continue
                schedule.shutdown(wait=False)
                self.SendLog({"Message":"Stopped schedule {0} from {1} group".format(schedName, groupName)})

        self.SendLog({"Message":"All running schedules have been stopped"})

        # clear schedules and data
        self._schedules = {}
        self._schedData = {}

    def StartSchedule(self, groupName, schedName, enable=1):
        """ start/stop schedule """
        logging.info("{0}, {1}".format(groupName, schedName))
        
        found = None
        enabled = None
        for n, (name, schedule, e) in enumerate(self._schedules[groupName]):
            # print(name, schedName)
            if name != schedName:
                continue
            found = name
            enabled = e
            break
        
        if not found:
            if enable == 1:
                self.SendLog({"Message":"StartSchedule: Could not find schedule {0} from group: {1}".format(schedName, groupName)})
            else:
                self.SendLog({"Message":"StopSchedule: Could not find schedule {0} from group: {1}".format(schedName, groupName)})
            return
                
        # start
        if enable == 1 and enabled == 0:
            self._schedules[groupName][n] = (name, schedule, 1)
            schedule.start()
            self.SendLog({"Message":"StartSchedule: {0} from group: {1}".format(schedName, groupName)})
            
        elif enable == 1 and enabled == 1:
            self.SendLog({"Message":"StartSchedule: {0} from group: {1} is already running".format(schedName, groupName)})
            
        # stop
        elif enable == 0 and enabled == 1:
            self._schedules[groupName][n] = (name, schedule, 0)
            schedule.shutdown(wait=False)
            self.SendLog({"Message":"StopSchedule: {0} from group: {1}".format(schedName, groupName)})

        elif enable == 0 and enabled == 0:
            self._schedules[groupName][n] = (name, schedule, 0)
            self.SendLog({"Message":"StopSchedule: {0} from group: {1} is already stopped".format(schedName, groupName)})
                    
# END