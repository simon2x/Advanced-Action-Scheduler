#
import win32con
import win32gui
import win32api
import win32com.client
import time
import pythoncom
import pywintypes

try:
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.schedulers.blocking import BlockingScheduler
except:
    pass
    

# Schedule('lucky', oneclick, '8-16', '4,14,24,34,44,54', '16,32', shutdown='22,05')    
class Schedule(object):

    def __init__(self,
                name,
                function,
                hour,
                minute, 
                second, 
                day=None,
                shutdown=None):
        
        sched = BlockingScheduler()        
        time = [hour, minute, second]
        
        if day is not None:
            time.append(day)
            print('run schedule on following day(s): %s' % day)
            name = CronTrigger(day_of_week=time[3], hour=time[0], minute=time[1], second=time[2])
        else:
            print('no day selected')
            name = CronTrigger(hour=time[0], minute=time[1], second=time[2])
        
        if shutdown is not None:
            h, m = shutdown.split(",")
            print('shutdown at h=%s, m=%s' % (h, m))
            sched.add_job(self.shutdown, CronTrigger(hour=h, minute=m))
        
        sched.add_job(function, name)
        print("job:", name, " has been added to schedule")
        sched.start()
        
        
    def shutdown(): 
        """force shutdown all jobs"""
        sched.shutdown(wait=False)
        
class Mouse:
    
    def __init__(self, title, *coordinates):        
        cur_pos = win32api.GetCursorPos()
        cur_win = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        print("current", cur_win)
        print(title)
        
        time.sleep(0.5)
        self.set_foreground(title)
        time.sleep(0.5)
        hwnd = win32gui.GetForegroundWindow()
        try:
            win32gui.MoveWindow(hwnd, 0, 0, 1366, 738, True)
        except pywintypes.error:
            return
        time.sleep(0.5)
        
        for key, value in enumerate(coordinates):            
            key = value.split(",")   
            print(key)
            x_value, y_value = key
            print(x_value, y_value)
            self.move_mouse(x_value,y_value)
            time.sleep(0.5)
                    
        # Return to original window and position
        self.set_foreground(cur_win)
        print("current position: ", cur_pos)
        # win32api.SetCursorPos(cur_pos)    
        try:
            win32api.SetCursorPos(cur_pos)    
        except:
            pass
            
    def set_foreground(self, title):        
        # workaround fix set foreground error
        time.sleep(0.5)
        pythoncom.CoInitialize() 
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        try:
            win32gui.SetForegroundWindow(win32gui.FindWindow(None, title))    
        except:
            return
            
    def move_mouse(self,x_value,y_value):
        get_foreground = win32gui.GetForegroundWindow()
        rect = win32gui.GetWindowRect(get_foreground)
        
        x = rect[0]
        y = rect[1]
        windowWidth = rect[2] - x
        windowHeight = rect[3] - y
        
        print("Go To Window: %s" % win32gui.GetWindowText(get_foreground))
        print("\tLocation: (%d, %d)" % (x, y))
        print("\tSize: (%d, %d)" % (windowWidth, windowHeight))
        
        # move cursor from top left corner of window
        move_x = int(windowWidth * float(x_value)/100)
        move_y = int(windowHeight * float(y_value)/100)       
        print(move_x, move_y)
        
        # move cursor to relative position and simulate mouse click
        win32api.SetCursorPos((x,y))
        win32api.SetCursorPos((move_x,move_y))  
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

if __name__ == "__main__": 
    Mouse("bingo", "60, 60")
    Mouse("Task Manager", "60, 60")    
    Mouse("bingo", "60, 60")
    Mouse("Task Manager", "60, 60")   
    Mouse("bingo", "60, 60")