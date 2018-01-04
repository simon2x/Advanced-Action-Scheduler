"""
Copyright (c) <year> <copyright holders>

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
        self._sched_data = {}

        # populate with group names
        self._group_names = {}
    
    def AddSchedules(self, groupData):
        """ this method processes the groups schedules """
        
        groupName = groupData["columns"]["0"]
        groupSchedules = groupData["schedules"]

        groupChecked = groupData["checked"]
        if groupChecked == "False":
            return

        _schedules = {groupName: {}}
        ignore = [] #ignore any children of unchecked items
        for idx, idxData in groupSchedules:
            
            checked = idxData["checked"]
            if checked == 0:
                ignore.append(idx+",")
                continue

            # is a schedule?
            if "," not in idx:
                schedStr = idxData["columns"]["0"]
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

                args = (groupName, idx, schedName)
                schedule.add_job(self.OnSchedule, args=[args], trigger=cronTrig)

                # attach a listener to schedule events
                # schedule.add_listener(self.OnScheduleEvent, apsevents.EVENT_JOB_EXECUTED|apsevents.EVENT_JOB_ERROR)
                _schedules[groupName][idx] = (schedName, schedule)

            # ...is an action
            else:
                checked = idxData["checked"]
                # forget unchecked, because they are never called

                if checked == 0:
                    ignore.append(idx+",")
                    continue

                # is index a child of an unchecked item?
                isOk = True
                for g in ignore:
                    if idx.startswith(g):
                        isOk = False
                        break

                if isOk is False:
                    continue

                actionStr = idxData["columns"]["0"]
                action, params = actionStr.split(DELIMITER)
                params = make_tuple(params)

                try:
                    self._sched_data[groupName][idx] = (action, params)
                except:
                    self._sched_data[groupName] = {idx: (action, params)}

        # finally, start the checked schedules of the checked groups
        for groupName, groupScheds in _schedules.items():
            self._schedules[groupName] = groupScheds
            for i, sched in groupScheds.items():
                sched[1].start()
                self.SendLog(["-","Started schedule %s from %s group" % (sched[0], groupName)])
    
    def DoAction(self, action, kwargs):
        logging.info("Executing action: %s" % action)
        logging.info("parameters: %s" % str(kwargs))

        #convert tuple list to dictionary
        kwargs = {k:v for k,v in kwargs}

        if action == "CloseWindow":
            window = kwargs["window"]
            matchcase = kwargs["matchcase"]
            matchstring = kwargs["matchstring"]

            actman.CloseWindow(window, matchcase, matchstring)

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
        group, idx, schedName = args

        # sort indices by order of execution
        indices = [i for i in self._sched_data[group].keys()]
        indices = sorted(indices)

        while indices:
            i = indices[0]
            action, kwargs = self._sched_data[group][i]

            a = self.DoAction(action, kwargs)

            if a is False:
                # returned false, therefore action condition was not met
                # we delete the actions children
                for j,k in enumerate(reversed(indices)):
                    if not j.startswith(i):
                        continue
                    del indices[k]
                continue

            try:
                # otherwise, go to next action
                del indices[0]
            except:
                break

        self.SendLog(["",
                      "Executed schedule %s from group: %s" % (schedName, group)])

    def SendLog(self, message):
        """ pass message to schedule manager lis """
        parent = self.GetParent()
        parent.AppendLogMessage(message)

    def SetSchedules(self, data):
        """ process schedule data """

        # stop and remove schedules first
        self.Stop()

        for idx, groupData in data.items():
            self.AddSchedules(groupData)
    
    def Start(self):
        pass

    def Stop(self):
        """ shutdown all schedules """
        print(self._schedules)

        for group, data in self._schedules.items():
            for idx, schedules in data.items():
                s = schedules[1]
                s.shutdown()

                name = schedules[0]
                self.SendLog(["-",
                              "Stopped schedule %s from group %s" % (name, group)])

        self.SendLog(["-","Any running schedules have been stopped"])

        # clear schedules
        self._schedules = {}
    
# END