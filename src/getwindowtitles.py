import subprocess

def GetHostname():
    hostname = subprocess.check_output(["hostname"]).decode("utf-8").strip()
    return hostname

def GetUsername():
    username = subprocess.check_output(["whoami"]).decode("utf-8").strip()
    return username

def CloseWindow():
    pass

def KillProcess(pid):
    output = subprocess.check_output(["kill"] + [pid]).decode("utf-8").strip()
    if "arguments must be process or job IDs" in output:
        pass
    if "No such process" in output:
        pass

def GetWindowSize(pid):
    pass

def GetWindowSize(pid):
    pass

def GetWinInfo():
    """ returns window information in a dictionary """

    username = GetUsername()
    basecmd = "wmctrl"
    flags = ["-G", "-p", "-l"]
    output = subprocess.check_output(["wmctrl"] + flags).decode("utf-8").strip()

    row = 0
    outputparse = []
    windows = {}
    lines = output.split("\n")
    for line in lines:
        linesplit = line.split(" ")
        user = linesplit.index(username)

        title = " ".join(linesplit[user+1:])

        id = linesplit[0]
        params = linesplit[1:user]
        params = [e for e in params if e]
        desktop_id, pid, client_machine, viewport, w, h = params

        print(title,id,params)
        windows[id] = {"desktop_id": desktop_id,
                       "title": title,
                       "pid": pid,
                       "client_machine": client_machine,
                       "viewport": viewport,
                       "size": (int(w), int(h))}


    return windows

wininfo = GetWinInfo()
# for x in wininfo.items():
    # print(x)

