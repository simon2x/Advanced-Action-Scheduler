"""
linuxactionmanager.py

note: when wmctrl retrieves the geometry of a window, it doesn't account
      for the window decorations, which varies across desktop environments

      This complicates the method for getting the window rect. We deal with
      this using the GetDecoratedWindowOffset function

future: remove xdotool dependencs
"""

import logging
import subprocess
import time

def CloseWindow():
    cmd = "xkill -i $( xprop -root | awk '/_NET_ACTIVE_WINDOW\(WINDOW\)/{print $NF}' )"

def GetHostname():
    hostname = subprocess.check_output(["hostname"]).decode("utf-8").strip()
    return hostname

def GetUsername():
    username = subprocess.check_output(["whoami"]).decode("utf-8").strip()
    return username

def GetWindowDecorationOffset(title, winclass):
    """ We move the target window to 0,0. Then get the window position
        This position is the offset of the window (without decoration)
    """

    flags = ["-r", ":ACTIVE:", "-b", "remove,maximized_vert,maximized_horz"]
    output = subprocess.check_output(["wmctrl"] + flags).decode("utf-8").strip()

    # Pass default gravity '0'. Move to top left corner (0,0). Leave size unchanged
    flags = ["-r", ":ACTIVE:", "-e", "0,0,0,-1,-1"]
    logging.info("%s" % str(flags))
    output = subprocess.check_output(["wmctrl"] + flags).decode("utf-8").strip()

    # get the offset position
    output = WmCtrlList()
    hostname = GetHostname()

    lines = output.split("\n")
    for line in lines:
        linesplit = line.split(" ")
        host_idx = linesplit.index(hostname)

        t = " ".join(linesplit[host_idx+1:])

        if title != t:
            continue

        params = linesplit[:host_idx]
        params = [e for e in params if e]
        window_id, desktop_id, pid, off_x, off_y, w, h, win_class = params

        if win_class != winclass:
            continue

        offset = "(%s, %s)" % (off_x, off_y)
        logging.info("Got window decoration offset (top-left padding): %s" % offset)
        return off_x, off_y

    return None

def GetWindowInfo():

    """ returns all window information in a dictionary """

    output = WmCtrlList()
    hostname = GetHostname()
    row = 0
    outputparse = []
    windows = {}
    lines = output.split("\n")
    for line in lines:
        linesplit = line.split(" ")
        host_idx = linesplit.index(hostname)

        title = " ".join(linesplit[host_idx+1:])

        params = linesplit[:host_idx]
        params = [e for e in params if e or e is 0]
        print(params)
        window_id, desktop_id, pid, x, y, w, h, win_class = params


        windows[window_id] = {"desktop_id": desktop_id,
                              "title": title,
                              "pid": pid,
                              "client_machine": host_idx,
                              # "viewport": viewport,
                              "rect": [int(x), int(y), int(w), int(h)],
                              "size": (int(w), int(h)),
                              "win_class": win_class}

    return windows

def GetWindowId(title, winclass):
    """ -r <WIN> -e <MVARG> """
    output = WmCtrlList()
    hostname = GetHostname()
    row = 0
    outputparse = []
    windows = {}
    lines = output.split("\n")
    for line in lines:
        linesplit = line.split(" ")
        host_idx = linesplit.index(hostname)

        t = " ".join(linesplit[host_idx+1:])

        params = linesplit[:host_idx]
        params = [e for e in params if e or e is 0]
        window_id, desktop_id, pid, x, y, w, h, win_class = params

        if t != title:
            continue
        if win_class != winclass:
            continue

        return window_id

    # window not found!
    return None

def GetWindowList():

    """ returns window (title, class) tuple list """

    output = WmCtrlList()
    hostname = GetHostname()
    titles = []
    lines = output.split("\n")
    for line in lines:
        linesplit = line.split(" ")
        host_idx = linesplit.index(hostname)

        title = " ".join(linesplit[host_idx+1:])
        params = linesplit[:host_idx]
        params = [e for e in params if e or e is 0]
        win_class = params[7]
        titles.append(str((title, win_class)))

    logging.info("Windows: %s" % str(titles))
    return titles

def GetWindowRect(title, winclass):
    output = WmCtrlList()
    hostname = GetHostname()

    lines = output.split("\n")
    for line in lines:
        linesplit = line.split(" ")
        host_idx = linesplit.index(hostname)

        t = " ".join(linesplit[host_idx+1:])

        if title != t:
            continue

        params = linesplit[:host_idx]
        params = [e for e in params if e]
        window_id, desktop_id, pid, x, y, w, h, win_class = params

        if win_class != winclass:
            continue

        WmCtrlActivate(window_id)
        off_x, off_y = GetWindowDecorationOffset(title, win_class)

        # calculate the adjusted offset
        adj_x, adj_y = int(x)-int(off_x), int(y)-int(off_y)

        # revert back to original window position
        SetWindowSize(title, win_class, adj_x, adj_y, w, h)

        return [adj_x, adj_y, int(w), int(h)]

# def GetWindowRect(title, winclass):
    # output = WmCtrlList()
    # hostname = GetHostname()

    # lines = output.split("\n")
    # for line in lines:
        # linesplit = line.split(" ")
        # host_idx = linesplit.index(hostname)

        # t = " ".join(linesplit[host_idx+1:])

        # if title != t:
            # continue

        # params = linesplit[:host_idx]
        # params = [e for e in params if e]
        # window_id, desktop_id, pid, x, y, w, h, win_class = params

        # if win_class != winclass:
            # continue

        # WmCtrlActivate(window_id)
        # off_x, off_y = GetWindowDecorationOffset(title, win_class)

        # # calculate the adjusted offset
        # adj_x, adj_y = int(x)-int(off_x), int(y)-int(off_y)

        # # revert back to original window position
        # SetWindowSize(title, win_class, adj_x, adj_y, w, h)

        # return [adj_x, adj_y, int(w), int(h)]


def GetWindowSize(title):
    hostname = GetHostname()
    output = WmCtrlList()

    row = 0
    outputparse = []
    windows = {}
    lines = output.split("\n")
    for line in lines:
        linesplit = line.split(" ")
        host_idx = linesplit.index(hostname)

        t = " ".join(linesplit[host_idx+1:])

        if title != t:
            continue

        id = linesplit[0]
        params = linesplit[:host_idx]
        params = [e for e in params if e]
        desktop_id, pid, client_machine, viewport, w, h = params

        return (0, 0, w, h)

def KillProcess(pid):
    output = subprocess.check_output(["kill"] + [pid]).decode("utf-8").strip()
    if "arguments must be process or job IDs" in output:
        pass
    if "No such process" in output:
        pass

def MouseClickRelative(x, y, w=None, h=None, originalpos=False):
    pass

def SetForegroundWindow(title, winclass):

    """ activate the first matched window, and if no match found, return None """

    output = WmCtrlList()
    hostname = GetHostname()
    row = 0
    outputparse = []
    windows = {}
    lines = output.split("\n")
    for line in lines:
        linesplit = line.split(" ")
        host_idx = linesplit.index(hostname)

        t = " ".join(linesplit[host_idx+1:])

        params = linesplit[:host_idx]
        params = [e for e in params if e or e is 0]
        window_id, desktop_id, pid, x, y, w, h, win_class = params

        if t != title:
            continue
        if win_class != winclass:
            continue

        WmCtrlActivate(window_id)
        return True

    logging.info("Could not set foreground window: %s" % title)
    return None

def SetWindowSize(title, win_class, offw, offy, w, h):

    # we always switch to the window since background maximised windows
    # can't be resized/moved. Though not sure why.
    success = SetForegroundWindow(title, win_class)
    if not success:
        return None

    flags = ["-r", ":ACTIVE:", "-b", "remove,maximized_vert,maximized_horz"]
    output = subprocess.check_output(["wmctrl"] + flags).decode("utf-8").strip()

    # Pass default gravity '0'
    flags = ["-r", ":ACTIVE:", "-e", "0,%s,%s,%s,%s" % (offw, offy, w, h)]
    logging.info("%s" % str(flags))
    output = subprocess.check_output(["wmctrl"] + flags).decode("utf-8").strip()

def WmCtrlActivate(window_id):

    """ activate (set foreground) window id """

    cmd = ["wmctrl", "-ia"] + [window_id]
    output = subprocess.check_output(cmd).decode("utf-8").strip()
    logging.info("Activated window: %s" % window_id)

def WmCtrlList():

    """
    return output of command 'wmctrl -G -p -l'
    -G: geometry
    -p: pid
    -x: window class
    """

    basecmd = "wmctrl"
    flags = ["-G", "-p", "-x", "-l"]
    output = subprocess.check_output(["wmctrl"] + flags).decode("utf-8").strip()

    return output