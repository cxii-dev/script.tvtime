#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import threading
import xbmc
import xbmcaddon
import unicodedata
import json

__addon__         = xbmcaddon.Addon()
__cwd__           = __addon__.getAddonInfo('path')
__icon__          = __addon__.getAddonInfo("icon")
__scriptname__    = __addon__.getAddonInfo('name')
__version__       = __addon__.getAddonInfo('version')
__language__      = __addon__.getLocalizedString
__resource_path__ = os.path.join(__cwd__, 'resources', 'lib')
__resource__      = xbmc.translatePath(__resource_path__).decode('utf-8')

from resources.lib.tvshowtime import FindEpisode
from resources.lib.tvshowtime import MarkAsWatched
from resources.lib.tvshowtime import MarkAsUnWatched
from resources.lib.tvshowtime import GetUserInformations
from resources.lib.tvshowtime import Signin

class Monitor(xbmc.Monitor):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )
        self.action = kwargs['action']
        self.facebook = __addon__.getSetting('facebook')
        self.twitter = __addon__.getSetting('twitter')
        self.notifications = __addon__.getSetting('notifications')

    def onSettingsChanged( self ):
        log('onSettingsChanged')
        self.action()
        
    def onNotification(self, sender, method, data):
        log('onNotification')
        log('method=%s' % method)
        if (method == 'Player.OnPlay'):
            log('Player.OnPlay')
            player._setUp()
            player._totalTime = player.getTotalTime()
            player._tracker.start()
            response = json.loads(data) 
            log('%s' % response)
            if response.get('item').get('type') == 'episode':
                xbmc_id = response.get('item').get('id')
                item = self.getEpisodeTVDB(xbmc_id)    
                log('showtitle=%s' % item['showtitle'])
                log('season=%s' % item['season'])
                log('episode=%s' % item['episode'])
                if len(item['showtitle']) > 0 and item['season'] > 0 and item['episode'] > 0:                   
                    player.filename = '%s.S%sE%s' % (formatName(item['showtitle']), item['season'], item['episode'])
                    log('tvshowtitle=%s' % player.filename)
                    player.episode = FindEpisode(player.user.token, player.filename)
                    log('episode.is_found=%s' % player.episode.is_found)
                    if player.episode.is_found:
                        if self.notifications:            
                            notif('%s %s %sx%s' % (__language__(32904), player.episode.showname, player.episode.season_number, player.episode.number), time=2500)
                    else:
                        if self.notifications:
                            notif(__language__(32905), time=2500)
                        player._tearDown()
                else:
                    if self.notifications:
                        notif(__language__(32905), time=2500)
                    player._tearDown()
        if (method == 'VideoLibrary.OnUpdate'):
            log('VideoLibrary.OnUpdate')
            response = json.loads(data) 
            log('%s' % response)
            if response.get('item').get('type') == 'episode':
                xbmc_id = response.get('item').get('id')
                playcount = response.get('playcount') 
                log('playcount=%s' % playcount)
                item = self.getEpisodeTVDB(xbmc_id)    
                log('showtitle=%s' % item['showtitle'])
                log('season=%s' % item['season'])
                log('episode=%s' % item['episode'])
                log('playcount=%s' % playcount)
                if len(item['showtitle']) > 0 and item['season'] > 0 and item['episode'] > 0:
                    self.filename = '%s.S%sE%s' % (formatName(item['showtitle']), item['season'], item['episode'])
                    log('tvshowtitle=%s' % self.filename)
                    self.episode = FindEpisode(player.user.token, self.filename)
                    log('episode.is_found=%s' % self.episode.is_found)
                    if self.episode.is_found:
                        if playcount is 1:
                            checkin = MarkAsWatched(player.user.token, self.filename, __addon__.getSetting('facebook'), __addon__.getSetting('twitter'))
                            log('checkin.is_marked:=%s' % checkin.is_marked)
                            if checkin.is_marked:
                                if self.notifications:
                                    notif('%s %s %sx%s' % (__language__(32906), self.episode.showname, self.episode.season_number, self.episode.number), time=2500)
                                else:
                                    if self.notifications:
                                        notif(__language__(32907), time=2500)
                        if playcount is 0:
                            checkin = MarkAsUnWatched(player.user.token, self.filename)
                            log('checkin.is_unmarked:=%s' % checkin.is_unmarked)
                            if checkin.is_unmarked:
                                if self.notifications:
                                    notif('%s %s %sx%s' % (__language__(32908), self.episode.showname, self.episode.season_number, self.episode.number), time=2500)
                                else:
                                    if self.notifications:
                                        notif(__language__(32907), time=2500)
            #if response.get('item').get('type') == 'tvshow':
            #    xbmc_id = response.get('item').get('id')
            #    items = self.getAllEpisodes(xbmc_id)
            #    log('%s' % items)

    def getEpisodeTVDB(self, xbmc_id):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodeDetails', 'params': {"episodeid": int(xbmc_id), 'properties': ['season', 'episode', 'tvshowid', 'showtitle']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)
        
        try:
            item = {}
            item['season'] = result['result']['episodedetails']['season']
            item['tvshowid'] = result['result']['episodedetails']['tvshowid']
            item['episode'] = result['result']['episodedetails']['episode']
            item['showtitle'] = result['result']['episodedetails']['showtitle']
            return item
        except:
            return False
            
    def getAllEpisodes(self, xbmc_id):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodes', 'params': {"tvshowid": int(xbmc_id), 'properties': ['season', 'episode', 'showtitle', 'playcount']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)
        return result

class Player(xbmc.Player):

    def __init__ (self):
        xbmc.Player.__init__(self)
        log('Player - init')
        self.username = __addon__.getSetting('username')
        self.password = __addon__.getSetting('password')
        self.facebook = __addon__.getSetting('facebook')
        self.twitter = __addon__.getSetting('twitter')
        self.notifications = __addon__.getSetting('notifications')
        if self.username is '' or self.password is '':
            log(__language__(32901))
            notif(__language__(32901), time=2500)
            return
        self.user = self._loginTVST()
        if not self.user.is_connected:
            return
        self._lastPos = 0
        self._min_percent = int(__addon__.getSetting('watched-percent'))
        self._tracker = None
        self._playbackLock = threading.Event()
        self._monitor = Monitor(action = self._reset)
        log('Player - monitor')
        
    def _reset(self):
        self._tearDown()
        self.__init__()
        
    def _trackPosition(self):
        while self._playbackLock.isSet() and not xbmc.abortRequested:
            try:
                self._lastPos = self.getTime()
            except:
                self._playbackLock.clear()
            if self._totalTime > 0:
                actual_percent = (self._lastPos/self._totalTime)*100
                #log('actual_percent=%s' % actual_percent)
                if (actual_percent >= self._min_percent):
                    log('episode.is_found=%s' % self.episode.is_found)
                    if self.episode.is_found:        
                        checkin = MarkAsWatched(self.user.token, self.filename, __addon__.getSetting('facebook'), __addon__.getSetting('twitter'))
                        log('checkin.is_marked:=%s' % checkin.is_marked)
                        if checkin.is_marked:
                            if self.notifications:
                                notif('%s %s %sx%s' % (__language__(32906), self.episode.showname, self.episode.season_number, self.episode.number), time=2500)
                        else:
                            if self.notifications:
                                notif(__language__(32907), time=2500)
            
                        self._tearDown()
            xbmc.sleep(250)

    def _setUp(self):
        self._playbackLock.set()
        self._tracker = threading.Thread(target=self._trackPosition)

    def _tearDown(self):
        if hasattr(self, '_playbackLock'):
            self._playbackLock.clear()
        #self._monitor = None
        if not hasattr(self, '_tracker'):
            return
        if self._tracker is None:
            return
        self._tracker = None

    def _loginTVST(self):
        log('_loginTVST')
        user = Signin(self.username, self.password)
        if user.is_connected:
            if self.notifications:
                notif('%s %s' % (__language__(32902), self.username), time=2500)
        else:
            notif(__language__(32903), time=2500)
        return user

    #def onPlayBackStarted(self):
        #log('onPlayBackStarted')
        #self._setUp()
        #self._totalTime = self.getTotalTime()
        #self._tracker.start()
    	  #
        #filename_full_path = self.getPlayingFile().decode('utf-8') 
        #if _is_excluded(filename_full_path):
        #    self._tearDown()
        #    return
        #	   
        #tvshowtitle = xbmc.getInfoLabel("ListItem.TVshowtitle")
        #season = xbmc.getInfoLabel("ListItem.Season")
        #episode = xbmc.getInfoLabel("ListItem.Episode")
        #log('tvshowtitle=%s' % tvshowtitle)
        #log('season=%s' % season)
        #log('episode=%s' % episode)
        #if len(tvshowtitle) > 0 and season > 0 and episode > 0:
        #    self.filename = '%s.S%sE%s' % (formatName(tvshowtitle), season, episode)
        #    log('filename=%s' % self.filename)
        #    self.episode = FindEpisode(self.user.token, self.filename)
        #    log('episode.is_found=%s' % self.episode.is_found)
        #
        #    if self.episode.is_found:
        #        if self.notifications:            
        #            notif('%s %s %sx%s' % (__language__(32904), self.episode.showname, self.episode.season_number, self.episode.number), time=2500)
        #    else:
        #        if self.notifications:
        #            notif(__language__(32905), time=2500)
        #        self._tearDown()
        #else:
        #    if self.notifications:
        #        notif(__language__(32905), time=2500)
        #    self._tearDown()

    def onPlayBackStopped(self):
        log('onPlayBackStopped')
        self.onPlayBackEnded()

    def onQueueNextItem(self):
        log('onQueueNextItem')
        self.onPlayBackEnded()

    def onPlayBackEnded(self):
        log('onPlayBackEnded')
        self._tearDown()

def formatNumber(number):
    if len(number) < 2:
         number = '0%s' % number
    return number
	 
def formatName(filename):
    filename = filename.strip()
    filename = filename.replace(' ', '.')
    return filename	 
    
def notif(msg, time=5000):
    notif_msg = "%s, %s, %i, %s" % (__scriptname__, msg, time, __icon__)
    xbmc.executebuiltin("XBMC.Notification(%s)" % notif_msg.encode('utf-8'))

def log(msg):
    xbmc.log("### [%s] - %s" % (__scriptname__, msg.encode('utf-8'), ),
            level=100) #100 #xbmc.LOGDEBUG

def _is_excluded(filename):
    log("_is_excluded(): Check if '%s' is a URL." % filename)
    excluded_protocols = ["pvr://", "http://", "https://"]
    return any(protocol in filename for protocol in excluded_protocols)

if ( __name__ == "__main__" ):
    player = Player()
    log( "[%s] - Version: %s Started" % (__scriptname__, __version__))

    while not xbmc.abortRequested:
        xbmc.sleep(100)

    log( "sys.exit(0)")
    sys.exit(0)

