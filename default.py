#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import threading
import xbmc
import xbmcvfs
import xbmcgui
import xbmcaddon
import unicodedata
import json

__addon__         = xbmcaddon.Addon()
__cwd__           = __addon__.getAddonInfo('path')
__icon__          = __addon__.getAddonInfo('icon')
__scriptname__    = __addon__.getAddonInfo('name')
__version__       = __addon__.getAddonInfo('version')
__language__      = __addon__.getLocalizedString
__resource_path__ = os.path.join(__cwd__, 'resources', 'lib')
__resource__      = xbmcvfs.translatePath(__resource_path__)
__notifications__ = __addon__.getSetting('notifications')

from resources.lib.tvtime import FindEpisode
from resources.lib.tvtime import MarkAsWatched
from resources.lib.tvtime import MarkAsUnWatched
from resources.lib.tvtime import GetUserInformations
from resources.lib.tvtime import SaveProgress
from resources.lib.tvtime import SetEmotion

class Monitor(xbmc.Monitor):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )
        self.action = kwargs['action']
        self._total_time = 999999
        self._last_pos = 0
        self._tracker = None
        self._playback_lock = threading.Event()

    def _trackPosition(self):
        monit = xbmc.Monitor()
        while self._playback_lock.isSet() and not monit.abortRequested:
            try:
                self._last_pos = player.getTime()
            except:
                self._playback_lock.clear()
            log('Inside Player. Tracker time = %s' % self._last_pos)
            xbmc.sleep(250)
        log('Position tracker ending with last_pos = %s' % self._last_pos)

    def _setUp(self):
        self._playback_lock.set()
        self._tracker = threading.Thread(target=self._trackPosition)

    def _tearDown(self):
        if hasattr(self, '_playback_lock'):
            self._playback_lock.clear()
        self._monitor = None
        if not hasattr(self, '_tracker'):
            return
        if self._tracker is None:
            return
        if self._tracker.isAlive():
            self._tracker.join()
        self._tracker = None

    def onSettingsChanged( self ):
        log('onSettingsChanged')
        self.action()
        
    def onNotification(self, sender, method, data):
        log('onNotification')
        log('method=%s' % method)
        log('sender=%s' % sender)
        log('data=%s' % data)
        if (method == 'Player.OnPlay'):
            self._player_onplay(data)
        if (method == 'Player.OnStop'):
            self._player_onstop(data)
        if (method == 'VideoLibrary.OnUpdate'):
            self._video_onupdate(data)

    def _player_onplay(self, data):
        self._setUp()
        self._total_time = player.getTotalTime()
        self._tracker.start()
        log('Player.OnPlay')
        if player.http == 'true' and player.getPlayingFile()[:4] == 'http' and re.search(r'[sS][0-9]*[eE][0-9]*', os.path.basename(player.getPlayingFile()), flags=0) :
            player.http_playing = True
            player.filename = os.path.basename(player.getPlayingFile())
            log('rawname=%s' % player.filename)
            startcut = player.filename.find("%5B")
            endcut = player.filename.find("%5D")
            tocut = player.filename[startcut:endcut]
            player.filename = player.filename.replace(tocut, "")
            player.filename = player.filename.replace("%5B", "")
            player.filename = player.filename.replace("%5D", "")
            player.filename = player.filename.replace("%20", ".")
            log('tvshowtitle=%s' % player.filename)

            player.episode = FindEpisode(player.token, 0, player.filename)
            log('episode.is_found=%s' % player.episode.is_found)

            if player.notifications != 'true':
                return
            if player.notif_during_playback == 'false' and player.isPlaying() == 1:
                return

            if player.episode.is_found:
                if player.notif_scrobbling == 'false':
                    return
                notif('%s %s %sx%s' % (__language__(32904), player.episode.showname, player.episode.season_number, player.episode.number), time=2500)
            else:
                notif(__language__(32905), time=2500)
        else:
            player.http_playing = False
            response = json.loads(data)
            log('%s' % response)
            if response.get('item') is None or response.get('item').get('type') != 'episode':
                return

            xbmc_id = response.get('item').get('id')
            item = self.getEpisodeTVDB(xbmc_id)
            log('showtitle=%s' % item['showtitle'])
            log('season=%s' % item['season'])
            log('episode=%s' % item['episode'])
            log('episode_id=%s' % item['episode_id'])
            if len(item['showtitle']) > 0 and item['season'] > 0 and item['episode'] > 0 and len(str(item['episode_id'])) > 0:
                player.filename = '%s.S%.2dE%.2d' % (formatName(item['showtitle']), float(item['season']), float(item['episode']))
                log('tvshowtitle=%s' % player.filename)

                player.episode = FindEpisode(player.token, item['episode_id'], player.filename)
                log('episode.is_found=%s' % player.episode.is_found)

                if player.notifications != 'true':
                    return
                if player.notif_during_playback == 'false' and player.isPlaying() == 1:
                    return

                if player.episode.is_found:
                    notif('%s %s %sx%s' % (__language__(32904), player.episode.showname, player.episode.season_number, player.episode.number), time=2500)
                else:
                    notif(__language__(32905), time=2500)
            else:
                if player.notifications != 'true':
                    return
                if player.notif_during_playback == 'false' and player.isPlaying() == 1:
                    return
                
                notif(__language__(32905), time=2500)


    def _player_onstop(self, data):
        self._tearDown()
        actual_percent = (self._last_pos/self._total_time)*100
        log('last_pos / total_time : %s / %s = %s %%' % (self._last_pos, self._total_time, actual_percent))
        log('Player.OnStop')
        if player.http == 'true' and player.http_playing == True:
            if player.progress != 'true':
                return

            player.episode = FindEpisode(player.token, 0, player.filename)
            log('episode.is_found=%s' % player.episode.is_found)

            if not player.episode.is_found:
                return

            log('progress=%s' % self._last_pos)
            progress = SaveProgress(player.token, player.episode.id, self._last_pos)
            log('progress.is_set:=%s' % progress.is_set)

            if actual_percent <= 90:
                return

            log('MarkAsWatched(*, %s, %s, %s)' % (player.filename, player.facebook, player.twitter))
            checkin = MarkAsWatched(player.token, player.episode.id, player.facebook, player.twitter)
            log('checkin.is_marked:=%s' % checkin.is_marked)
            if not checkin.is_marked:
                return

            if player.emotion == 'true':
                msg = '%s: %s %sx%s' % (__language__(33909), player.episode.showname, player.episode.season_number, player.episode.number)
                emotion = xbmcgui.Dialog().select(msg, [__language__(35311), __language__(35312), __language__(35313), __language__(35314), __language__(35316), __language__(35317)])
                if emotion < 0: return
                if emotion == 0:
                    emotion = 1
                elif emotion == 1:
                    emotion = 2
                elif emotion == 2:
                    emotion = 3
                elif emotion == 3:
                    emotion = 4
                elif emotion == 4:
                    emotion = 6
                elif emotion == 5:
                    emotion = 7
                SetEmotion(player.token, player.episode.id, emotion)

            if player.notifications != 'true':
                return
            if player.notif_during_playback == 'false' and player.isPlaying() == 1:
                return
            notif('%s %s %sx%s' % (__language__(32906), player.episode.showname, player.episode.season_number, player.episode.number), time=2500)
        else:
            response = json.loads(data)
            log('%s' % response)

            if player.progress != 'true':
                return

            if response.get('item').get('type') != 'episode':
                return

            xbmc_id = response.get('item').get('id')
            item = self.getEpisodeTVDB(xbmc_id)
            log('showtitle=%s' % item['showtitle'])
            log('season=%s' % item['season'])
            log('episode=%s' % item['episode'])
            log('episode_id=%s' % item['episode_id'])

            if len(item['showtitle']) > 0 and item['season'] > 0 and item['episode'] > 0 and len(str(item['episode_id'])) > 0:
                player.filename = '%s.S%.2dE%.2d' % (formatName(item['showtitle']), float(item['season']), float(item['episode']))
                log('tvshowtitle=%s' % player.filename)

            log('progress=%s' % self._last_pos)
            progress = SaveProgress(player.token, item['episode_id'], self._last_pos)
            log('progress.is_set:=%s' % progress.is_set)

    def _video_onupdate(self, data):
        log('VideoLibrary.OnUpdate')
        response = json.loads(data)
        log('%s' % response)
        if response.get('item') is None or response.get('item').get('type') != 'episode':
            return

        xbmc_id = response.get('item').get('id')
        playcount = response.get('playcount')
        log('playcount=%s' % playcount)

        item = self.getEpisodeTVDB(xbmc_id)
        log('showtitle=%s' % item['showtitle'])
        log('season=%s' % item['season'])
        log('episode=%s' % item['episode'])
        log('episode_id=%s' % item['episode_id'])
        log('playcount=%s' % playcount)

        if item.get('showtitle') is None or item.get('season') is None or item.get('episode') is None or item.get('episode_id') is None:
            return

        self.filename = '%s.S%.2dE%.2d' % (formatName(item['showtitle']), float(item['season']), float(item['episode']))
        log('tvshowtitle=%s' % self.filename)
        self.episode = FindEpisode(player.token, item['episode_id'], self.filename)
        log('episode.is_found=%s' % self.episode.is_found)

        if not self.episode.is_found:
            return

        if playcount == 1:
            log('MarkAsWatched(*, %s, %s, %s)' % (self.filename, player.facebook, player.twitter))
            checkin = MarkAsWatched(player.token, self.episode.id, player.facebook, player.twitter)
            log('checkin.is_marked:=%s' % checkin.is_marked)
            if checkin.is_marked:
                if player.emotion == 'true':
                    emotion = xbmcgui.Dialog().select('%s: %s' % (__language__(33909), self.filename), [__language__(35311), __language__(35312), __language__(35313), __language__(35314), __language__(35316), __language__(35317)])
                    if emotion < 0: return
                    if emotion == 0:
                        emotion = 1
                    elif emotion == 1:
                        emotion = 2
                    elif emotion == 2:
                        emotion = 3
                    elif emotion == 3:
                        emotion = 4
                    elif emotion == 4:
                        emotion = 6
                    elif emotion == 5:
                        emotion = 7
                    SetEmotion(player.token, self.episode.id, emotion)

                if player.notifications != 'true':
                    return
                if player.notif_during_playback == 'false' and player.isPlaying() == 1:
                    return
                if player.notif_scrobbling == 'false':
                    return
                notif('%s %s %sx%s' % (__language__(32906), self.episode.showname, self.episode.season_number, self.episode.number), time=2500)
            else:
                if player.notifications != 'true':
                    return
                if player.notif_during_playback == 'false' and player.isPlaying() == 1:
                    return
                notif(__language__(32907), time=2500)
        elif playcount == 0:
            log('MarkAsUnWatched(*, %s)' % (self.filename))
            checkin = MarkAsUnWatched(player.token, self.episode.id)
            log('checkin.is_unmarked:=%s' % checkin.is_unmarked)

            if player.notifications != 'true':
                return
            if player.notif_during_playback == 'false' and player.isPlaying() == 1:
                return

            if checkin.is_unmarked:
                if player.notif_scrobbling == 'false':
                    return
                notif('%s %s %sx%s' % (__language__(32908), self.episode.showname, self.episode.season_number, self.episode.number), time=2500)
            else:
                notif(__language__(32907), time=2500)

    def getEpisodeTVDB(self, xbmc_id):
        rpccmd = {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodeDetails', 'params': {"episodeid": int(xbmc_id), 'properties': ['season', 'episode', 'tvshowid', 'showtitle', 'uniqueid']}, 'id': 1}
        rpccmd = json.dumps(rpccmd)
        result = xbmc.executeJSONRPC(rpccmd)
        result = json.loads(result)
        log('result=%s' % result)

        if 'unknown' in result['result']['episodedetails']['uniqueid']:
            episode_id = result['result']['episodedetails']['uniqueid']['unknown']
        elif 'tvdb' in result['result']['episodedetails']['uniqueid']:
            episode_id = result['result']['episodedetails']['uniqueid']['tvdb']
        elif 'tmdb' in result['result']['episodedetails']['uniqueid']:
            episode_id = result['result']['episodedetails']['uniqueid']['tmdb']
        else:
            return {}
        log('episode_id=%s' % episode_id)

        try:
            item = {}
            item['season'] = result['result']['episodedetails']['season']
            item['tvshowid'] = result['result']['episodedetails']['tvshowid']
            item['episode'] = result['result']['episodedetails']['episode']
            item['showtitle'] = result['result']['episodedetails']['showtitle']
            item['episode_id'] = episode_id
            return item
        except:
            return {}

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
        self.token = __addon__.getSetting('token')
        self.facebook = __addon__.getSetting('facebook')
        self.twitter = __addon__.getSetting('twitter')
        self.welcome = __addon__.getSetting('welcome')
        self.notifications = __addon__.getSetting('notifications')
        self.notif_during_playback = __addon__.getSetting('notif_during_playback')
        self.notif_scrobbling = __addon__.getSetting('notif_scrobbling')
        self.progress = __addon__.getSetting('progress')
        self.http = __addon__.getSetting('http')
        self.http_playing = False
        self.emotion = __addon__.getSetting('emotion')
        self.defaultemotion = __addon__.getSetting('defaultemotion')
        if self.token == '':
            log(__language__(32901))
            if self.notifications == 'true':
                notif(__language__(32901), time=2500)
            return
        self.user = self._GetUser()
        if not self.user.is_authenticated:
            return
        self._monitor = Monitor(action = self._reset)
        log('Player - monitor')

    def _reset(self):
        self.__init__()

    def _GetUser(self):
        log('_GetUser')
        user = GetUserInformations(self.token)
        if user.is_authenticated:
            __addon__.setSetting('user', user.username)
            if self.notifications == 'true':
                if self.welcome == 'true':
                    notif('%s %s' % (__language__(32902), user.username), time=2500)
        else:
            __addon__.setSetting('user', '')
            if self.notifications == 'true':
                notif(__language__(32903), time=2500)
        return user

def formatNumber(number):
    if len(number) < 2:
         number = '0%s' % number
    return number

def formatName(filename):
    filename = filename.strip()
    filename = filename.replace(' ', '.')
    return normalizeString(filename)

def notif(msg, time=5000):
    xbmcgui.Dialog().notification(encode(__scriptname__), encode(msg), time=time, icon=__icon__)

def log(msg):
    xbmc.log("### [%s] - %s" % (__scriptname__, encode(msg), ),
            level=xbmc.LOGINFO) #100 #xbmc.LOGDEBUG

def encode(string):
    result = ''
    try:
        result = string.encode('UTF-8','replace')
    except UnicodeDecodeError:
        result = 'UTF-8 Error'
    return result

def normalizeString(str):
    return unicodedata.normalize('NFKD', str).encode('ascii','ignore').decode('UTF-8','replace')

if ( __name__ == "__main__" ):
    player = Player()
    log("[%s] - Version: %s Started" % (__scriptname__, __version__))
    monit = xbmc.Monitor()
    while not monit.abortRequested():
        if monit.waitForAbort(100):
            break
    player._monitor = None
    log("sys.exit(0)")
    sys.exit(0)
