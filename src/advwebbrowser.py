#! /usr/bin/env python3
# -*- coding: utf-8 -*
"""
@author Simon Wu <swprojects@runbox.com>

Copyright (c) 2018 by Simon Wu <Advanced Action Scheduler>
Released subject to the GNU Public License

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

"""
This module is based on python `webbrowser`.
https://docs.python.org/2/library/webbrowser.html#module-webbrowser

A few modifications made by Simon Wu (with Advanced Action Scheduler in mind). 
- removed Grails browser support
- removed background option
- remove try order. browser must be registered for get to work
- add klasses dict of browser klass

TODO:
    - incognito/private mode for those browsers which can support this feature
"""

from collections import OrderedDict
import os
import shlex
import shutil
import sys
import subprocess

__all__ = ["Error", "get", "register"]
_browsers = {} # Dictionary of available browser controllers

class Error(Exception):
    pass
    
def deregister(browser):
    try:
        del _browsers[browser.lower()]
    except KeyError:
        raise Error("no browser registered by %s" % browser)

def deregister_browsers():
    _browsers = {}  
    
def register(name, klass):
    """Register a browser connector and, optionally, connection."""
    _browsers[name.lower()] = klass(name=name)

def get(browser):
    """Return a browser launcher instance appropriate for the environment."""
    try:
        command = _browsers[browser.lower()]
    except KeyError:
        raise Error("no browser registered by %s" % browser)
        
    return command

# General parent classes

class BaseBrowser(object):
    """Parent class for all browsers. Do not use directly."""

    args = ['%s']

    def __init__(self, name=""):
        self.name = name
        self.basename = name

    def open(self, url, new=0, autoraise=True):
        raise NotImplementedError

    def open_new(self, url):
        return self.open(url, 1)

    def open_new_tab(self, url):
        return self.open(url, 2)


class GenericBrowser(BaseBrowser):
    """Class for all browsers started with a command
       and without remote functionality."""

    def __init__(self, name):
        if isinstance(name, str):
            self.name = name
            self.args = ["%s"]
        else:
            # name should be a list with arguments
            self.name = name[0]
            self.args = name[1:]
        self.basename = os.path.basename(self.name)

    def open(self, url, new=0, autoraise=True):
        cmdline = [self.name] + [arg.replace("%s", url)
                                 for arg in self.args]
        try:
            if sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            else:
                p = subprocess.Popen(cmdline, close_fds=True)
            return not p.wait()
        except OSError:
            return False


class BackgroundBrowser(GenericBrowser):
    """Class for all browsers which are to be started in the
       background."""

    def open(self, url, new=0, autoraise=True):
        cmdline = [self.name] + [arg.replace("%s", url)
                                 for arg in self.args]
        try:
            if sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            else:
                p = subprocess.Popen(cmdline, close_fds=True,
                                     start_new_session=True)
            return (p.poll() is None)
        except OSError:
            return False


class Browser(BaseBrowser):
    """Parent class for all Unix browsers with remote functionality."""

    raise_opts = None
    background = False
    redirect_stdout = True
    # In remote_args, %s will be replaced with the requested URL.  %action will
    # be replaced depending on the value of 'new' passed to open.
    # remote_action is used for new=0 (open).  If newwin is not None, it is
    # used for new=1 (open_new).  If newtab is not None, it is used for
    # new=3 (open_new_tab).  After both substitutions are made, any empty
    # strings in the transformed remote_args list will be removed.
    remote_args = ['%action', '%s']
    remote_action = None
    remote_action_newwin = None
    remote_action_newtab = None

    def _invoke(self, args, remote, autoraise):
        raise_opt = []
        if remote and self.raise_opts:
            # use autoraise argument only for remote invocation
            autoraise = int(autoraise)
            opt = self.raise_opts[autoraise]
            if opt: raise_opt = [opt]
        cmdline = [self.name] + raise_opt + args
        if remote or self.background:
            inout = subprocess.DEVNULL
        else:
            # for TTY browsers, we need stdin/out
            inout = None
        p = subprocess.Popen(cmdline, close_fds=False, stdin=inout,
                             stdout=(self.redirect_stdout and inout or None),
                             stderr=inout, start_new_session=True)                  
        if remote:
            # wait at most five seconds. If the subprocess is not finished, the
            # remote invocation has (hopefully) started a new instance.
            try:
                rc = p.wait(5)
                # if remote call failed, open() will try direct invocation
                return not rc
            except subprocess.TimeoutExpired:
                return True
        elif self.background:
            if p.poll() is None:
                return True
            else:
                return False
        else:
            return not p.wait()

    def open(self, url, new=0, autoraise=True):
        if new == 0:
            action = self.remote_action
        elif new == 1:
            action = self.remote_action_newwin
        elif new == 2:
            if self.remote_action_newtab is None:
                action = self.remote_action_newwin
            else:
                action = self.remote_action_newtab
        else:
            raise Error("Bad 'new' parameter to open(); " +
                        "expected 0, 1, or 2, got %s" % new)

        args = [arg.replace("%s", url).replace("%action", action)
                for arg in self.remote_args]
        args = [arg for arg in args if arg]
        success = self._invoke(args, True, autoraise)
        return success


class Mozilla(Browser):
    """Launcher class for Mozilla browsers."""

    remote_args = ['%action', '%s']
    remote_action = ""
    remote_action_newwin = "-new-window"
    remote_action_newtab = "-new-tab"
    background = True


class Netscape(Browser):
    """Launcher class for Netscape browser."""

    raise_opts = ["-noraise", "-raise"]
    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-tab"
    background = True


class Galeon(Browser):
    """Launcher class for Galeon/Epiphany browsers."""

    raise_opts = ["-noraise", ""]
    remote_args = ['%action', '%s']
    remote_action = "-n"
    remote_action_newwin = "-w"
    background = True


class Chrome(Browser):
    """Launcher class for Google Chrome browser."""

    remote_args = ['%action', '%s']
    remote_action = ""
    remote_action_newwin = "--new-window"
    remote_action_newtab = ""
    background = True

Chromium = Chrome


class Opera(Browser):
    """Launcher class for Opera browser."""

    raise_opts = ["-noraise", ""]
    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-page"
    background = True


class Elinks(Browser):
    """Launcher class for Elinks browsers."""

    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-tab"
    background = False

    # elinks doesn't like its stdout to be redirected -
    # it uses redirected stdout as a signal to do -dump
    redirect_stdout = False


class Konqueror(BaseBrowser):
    """
    Controller for the KDE File Manager (kfm, or Konqueror).
    See the output of ``kfmclient --commands``
    for more information on the Konqueror remote-control interface.
    """

    def open(self, url, new=0, autoraise=True):
        # XXX Currently I know no way to prevent KFM from opening a new win.
        if new == 2:
            action = "newTab"
        else:
            action = "openURL"

        devnull = subprocess.DEVNULL

        try:
            p = subprocess.Popen(["kfmclient", action, url],
                                 close_fds=True, stdin=devnull,
                                 stdout=devnull, stderr=devnull)
        except OSError:
            # fall through to next variant
            pass
        else:
            p.wait()
            # kfmclient's return code unfortunately has no meaning as it seems
            return True

        try:
            p = subprocess.Popen(["konqueror", "--silent", url],
                                 close_fds=True, stdin=devnull,
                                 stdout=devnull, stderr=devnull,
                                 start_new_session=True)
        except OSError:
            # fall through to next variant
            pass
        else:
            if p.poll() is None:
                # Should be running now.
                return True

        try:
            p = subprocess.Popen(["kfm", "-d", url],
                                 close_fds=True, stdin=devnull,
                                 stdout=devnull, stderr=devnull,
                                 start_new_session=True)
        except OSError:
            return False
        else:
            return (p.poll() is None)

#
# Platform support for Unix
#

# These are the right tests because all these Unix browsers require either
# a console terminal or an X display to run.

def register_X_browsers():

    # use xdg-open if around
    if shutil.which("xdg-open"):
        register("xdg-open", None, BackgroundBrowser("xdg-open"))

    # The default GNOME3 browser
    if "GNOME_DESKTOP_SESSION_ID" in os.environ and shutil.which("gvfs-open"):
        register("gvfs-open", None, BackgroundBrowser("gvfs-open"))

    # The default GNOME browser
    if "GNOME_DESKTOP_SESSION_ID" in os.environ and shutil.which("gnome-open"):
        register("gnome-open", None, BackgroundBrowser("gnome-open"))

    # The default KDE browser
    if "KDE_FULL_SESSION" in os.environ and shutil.which("kfmclient"):
        register("kfmclient", Konqueror, Konqueror("kfmclient"))

    if shutil.which("x-www-browser"):
        register("x-www-browser", None, BackgroundBrowser("x-www-browser"))

    # The Mozilla browsers
    for browser in ("firefox", "iceweasel", "iceape", "seamonkey"):
        if shutil.which(browser):
            register(browser, None, Mozilla(browser))

    # The Netscape and old Mozilla browsers
    for browser in ("mozilla-firefox",
                    "mozilla-firebird", "firebird",
                    "mozilla", "netscape"):
        if shutil.which(browser):
            register(browser, None, Netscape(browser))

    # Konqueror/kfm, the KDE browser.
    if shutil.which("kfm"):
        register("kfm", Konqueror, Konqueror("kfm"))
    elif shutil.which("konqueror"):
        register("konqueror", Konqueror, Konqueror("konqueror"))

    # Gnome's Galeon and Epiphany
    for browser in ("galeon", "epiphany"):
        if shutil.which(browser):
            register(browser, None, Galeon(browser))

    # Skipstone, another Gtk/Mozilla based browser
    if shutil.which("skipstone"):
        register("skipstone", None, BackgroundBrowser("skipstone"))

    # Google Chrome/Chromium browsers
    for browser in ("google-chrome", "chrome", "chromium", "chromium-browser"):
        if shutil.which(browser):
            register(browser, None, Chrome(browser))

    # Opera, quite popular
    if shutil.which("opera"):
        register("opera", None, Opera("opera"))

    # Next, Mosaic -- old but still in use.
    if shutil.which("mosaic"):
        register("mosaic", None, BackgroundBrowser("mosaic"))

# Prefer X browsers if present
if os.environ.get("DISPLAY"):
    register_X_browsers()

# Also try console browsers
if os.environ.get("TERM"):
    if shutil.which("www-browser"):
        register("www-browser", None, GenericBrowser("www-browser"))
    # The Links/elinks browsers <http://artax.karlin.mff.cuni.cz/~mikulas/links/>
    if shutil.which("links"):
        register("links", None, GenericBrowser("links"))
    if shutil.which("elinks"):
        register("elinks", None, Elinks("elinks"))
    # The Lynx browser <http://lynx.isc.org/>, <http://lynx.browser.org/>
    if shutil.which("lynx"):
        register("lynx", None, GenericBrowser("lynx"))
    # The w3m browser <http://w3m.sourceforge.net/>
    if shutil.which("w3m"):
        register("w3m", None, GenericBrowser("w3m"))
        
_klasses = {"Firefox": Mozilla,
            "Chrome/Chromium": Chrome,
            "Opera": Opera,
            "Mozilla": Mozilla,
            "Brave": Chrome,
            "Konqueror": Konqueror,
            "Galeon": Galeon,
            "Netscape": Netscape,
            "Elinks": Elinks,
            "Generic": BackgroundBrowser, 
            "Console": GenericBrowser}
            
klasses = OrderedDict()
for b in ["Generic", "Firefox","Chrome/Chromium","Opera","Mozilla","Brave",
          "Konqueror","Galeon","Elinks","Console"]:
    klasses[b] = _klasses[b]