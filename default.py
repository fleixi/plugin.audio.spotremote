# https://docs.python.org/2.7/
import os
import sys
import urllib
import urlparse
# http://mirrors.kodi.tv/docs/python-docs/
import xbmcaddon
import xbmcgui
import xbmcplugin
import dbus

from subprocess import Popen, PIPE, call


def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)

def getDBUS():
    try:
        bus = dbus.SessionBus(private=True)
        spotify = bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')
        spotify = dbus.Interface(spotify, 'org.mpris.MediaPlayer2.Player')
        return spotify
    except:
        return None

def getDBUSManager():
    try:
        bus = dbus.SessionBus(private=True)
        spotify = bus.get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')
        properties_manager = dbus.Interface(spotify, 'org.freedesktop.DBus.Properties')
        return properties_manager
    except:
        return None
    
def getProcess(path):
    try:
        p = Popen(['ps', 'aux'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        process = output.split(path)[1].strip()
        if debug == True:
            xbmc.log('Spotremote_Addon - getProcess: ' + process, level=xbmc.LOGDEBUG)
        return process
    except:
        if debug == True:
            xbmc.log('Spotremote_Addon - getProcess: Error no process', level=xbmc.LOGDEBUG)
        return None

def start_spotify():
    
    if debug == True:
        xbmc.log('Spotremote_Addon - start spotify: init', level=xbmc.LOGDEBUG)
    try:
        p = Popen(['whereis', 'spotify'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        paths = output.split(" ")
        for i in paths:
            if "share" in i:
                path = i.strip() + "/spotify"
    except:
        path = "/usr/share/spotify/spotify"
    if debug == True:
        xbmc.log('Spotremote_Addon- start spotify: path= '  + path, level=xbmc.LOGDEBUG)
    running = getProcess(path)
    spotify = None
    if running == None or running == "":
        Popen(['spotify'])
        if debug == True:
            xbmc.log('Spotremote_Addon- start spotify: Spotify started', level=xbmc.LOGDEBUG)
    while running == None or running == "":
        running = getProcess(path)
        if debug == True:
            xbmc.log('Spotremote_Addon- start spotify: running= '  + runnig, level=xbmc.LOGDEBUG)
        xbmc.sleep(1000)
    while spotify == None:
        spotify = getDBUS()
        if debug == True:
            xbmc.log('Spotremote_Addon- start spotify: dbus= '  + spotify, level=xbmc.LOGDEBUG)
        xbmc.sleep(1000)
    if not spotify == None:
        properties_manager = getDBUSManager()
        status = None
        while not status == "Playing" :
            try:
                status = str(properties_manager.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
                if debug == True:
                    xbmc.log('Spotremote_Addon- start spotify: status= '  + status, level=xbmc.LOGDEBUG)
            except:
                break
            if not status == "Playing" :
                spotify.Play()
    if debug == True:
        xbmc.log('Spotremote_Addon- start spotify: ende', level=xbmc.LOGDEBUG)
    
def main():
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    
    if mode is None:
        url = build_url({'mode' :'start'})
        li = xbmcgui.ListItem(spotify_play)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    elif mode[0] == 'start':
        start_spotify()
    xbmcplugin.endOfDirectory(addon_handle)
    
    sys.exit(0)
    
if __name__ == '__main__':
    my_addon = xbmcaddon.Addon('service.audio.spotremote')
    debug = my_addon.getSetting('debug')
    spotify_play = my_addon.getLocalizedString(51030)
    addon_handle = int(sys.argv[1])
    main()
