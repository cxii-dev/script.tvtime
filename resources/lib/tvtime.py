#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.cookiejar
import re
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import json

request_uri = "https://api.tvtime.com/v1/"

class FindEpisode(object):
    def __init__(self, token, episode_id, filename=''):
        self.token = token
        self.episode_id = episode_id
        self.filename = filename
        if len(self.filename) > 0:
            self.action = 'episode?access_token=%s&filename=%s' % (self.token, self.filename)
        else:
            self.action = 'episode?access_token=%s&episode_id=%s' % (self.token, self.episode_id)
        

        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
           urllib.request.HTTPRedirectHandler(),
           urllib.request.HTTPHandler(debuglevel=0),
           urllib.request.HTTPSHandler(debuglevel=0),
           urllib.request.HTTPCookieProcessor(self.cj)
        )

        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]

        self.opener.get_method = lambda: 'GET'
        
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, None)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_found = False
        else:
           self.is_found = True
           self.resultdata = data['result']
           self.showname = data['episode']['show']['name']
           self.episodename = data['episode']['name']
           self.season_number = data['episode']['season_number']
           self.number = data['episode']['number']
           self.id = data['episode']['id']
           
class Show(object):
    def __init__(self, token, show_id):
        self.token = token
        self.show_id = show_id
        self.action = 'show?access_token=%s&show_id=%s' % (self.token, self.show_id)

        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
           urllib.request.HTTPRedirectHandler(),
           urllib.request.HTTPHandler(debuglevel=0),
           urllib.request.HTTPSHandler(debuglevel=0),
           urllib.request.HTTPCookieProcessor(self.cj)
        )

        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]

        self.opener.get_method = lambda: 'GET'
        
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, None)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_found = False
        else:
           self.is_found = True
           self.resultdata = data['result']
           self.id = data['show']['id']
           self.showname = data['show']['name']
           self.last_season_seen = data['show']['last_seen']['season_number']
           self.last_episode_seen = data['show']['last_seen']['number']
                   
class GetLibrary(object):
    def __init__(self, token, page, limit):
        self.token = token
        self.page = page
        self.limit = limit
        self.action = 'library?access_token=%s&page=%s&limit=%s' % (self.token, self.page, self.limit)

        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
           urllib.request.HTTPRedirectHandler(),
           urllib.request.HTTPHandler(debuglevel=0),
           urllib.request.HTTPSHandler(debuglevel=0),
           urllib.request.HTTPCookieProcessor(self.cj)
        )

        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]

        self.opener.get_method = lambda: 'GET'
        
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, None)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_found = False
        else:
           self.is_found = True
           self.resultdata = data['result']
           self.shows = data['shows']
           
class IsChecked(object):
    def __init__(self, token, episode_id):
        self.token = token
        self.episode_id = episode_id
        self.action = 'checkin?access_token=%s&episode_id=%s' % (self.token, self.episode_id)

        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
           urllib.request.HTTPRedirectHandler(),
           urllib.request.HTTPHandler(debuglevel=0),
           urllib.request.HTTPSHandler(debuglevel=0),
           urllib.request.HTTPCookieProcessor(self.cj)
        )

        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]

        self.opener.get_method = lambda: 'GET'
        
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, None)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_found = False
        else:
           self.is_found = True
           self.is_watched = data['code']

class MarkAsWatched(object):
    def __init__(self, token, episode_id, facebook=0, twitter=0, autofollow=1):
        self.token = token
        self.episode_id = episode_id

        self.facebook = facebook
        if self.facebook == True: self.facebook = 1
        else: self.facebook = 0

        self.twitter = twitter
        if self.twitter == True: self.twitter = 1
        else: self.twitter = 0

        self.autofollow = autofollow
        if self.autofollow == True: self.autofollow = 1
        else: self.autofollow = 0

        self.action = 'checkin'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'episode_id' : self.episode_id,
            'publish_on_ticker' : self.facebook,
            'publish_on_twitter' : self.twitter,
            'auto_follow': self.autofollow
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_marked = False
        else:
           self.is_marked = True
           
class MarkAsUnWatched(object):
    def __init__(self, token, episode_id):
        self.token = token
        self.episode_id = episode_id
        self.action = 'checkout'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'episode_id' : self.episode_id
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_unmarked = False
        else:
           self.is_unmarked = True

class SaveProgress(object):
    def __init__(self, token, episode_id, progress):
        self.token = token
        self.episode_id = episode_id
        self.progress = progress
        self.action = 'progress'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'episode_id' : self.episode_id,
            'progress' : self.progress
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_set = False
        else:
           self.is_set = True
           
class Follow(object):
    def __init__(self, token, show_id):
        self.token = token
        self.show_id = show_id
        self.action = 'follow'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'show_id' : self.show_id
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_follow = False
        else:
           self.is_follow = True
           
class FollowShows(object):
    def __init__(self, token, show_id):
        self.token = token
        self.show_id = show_id
        self.action = 'follow'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'show_id' : self.show_id
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_follow = False
        else:
           self.is_follow = True

class SaveShowProgress(object):
    def __init__(self, token, show_id, season, episode):
        self.token = token
        self.show_id = show_id
        self.season = season
        self.episode = episode
        self.action = 'show_progress'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'show_id' : self.show_id,
            'season' : self.season,
            'episode' : self.episode
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_set = False
        else:
           self.is_set = True
           
class SaveShowsProgress(object):
    def __init__(self, token, shows):
        self.token = token
        self.shows = shows
        self.action = 'show_progress'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'shows' : self.shows
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_set = False
        else:
           self.is_set = True
               
class DeleteShowProgress(object):
    def __init__(self, token, show_id):
        self.token = token
        self.show_id = show_id
        self.action = 'delete_show_progress'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'show_id' : self.show_id
        }).encode("utf-8")

        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
           urllib.request.HTTPRedirectHandler(),
           urllib.request.HTTPHandler(debuglevel=0),
           urllib.request.HTTPSHandler(debuglevel=0),
           urllib.request.HTTPCookieProcessor(self.cj)
        )

        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]

        self.opener.get_method = lambda: 'POST'
        
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_delete = False
        else:
           self.is_delete = True
           self.resultdata = data['result']
           
class DeleteShowsProgress(object):
    def __init__(self, token, shows):
        self.token = token
        self.shows = shows
        self.action = 'delete_show_progress'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'shows' : self.shows
        }).encode("utf-8")

        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
           urllib.request.HTTPRedirectHandler(),
           urllib.request.HTTPHandler(debuglevel=0),
           urllib.request.HTTPSHandler(debuglevel=0),
           urllib.request.HTTPCookieProcessor(self.cj)
        )

        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]

        self.opener.get_method = lambda: 'POST'
        
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_delete = False
        else:
           self.is_delete = True
           self.resultdata = data['result']

class SetEmotion(object):
    def __init__(self, token, episode_id, emotion_id):
        self.token = token
        self.episode_id = episode_id
        self.emotion_id = emotion_id
        self.action = 'emotion'
        request_data = urllib.parse.urlencode({
            'access_token' : self.token,
            'episode_id' : self.episode_id,
            'emotion_id' : self.emotion_id
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_set = False
        else:
           self.is_set = True

class GetUserInformations(object):
    def __init__(self, token):
        self.token = token
        self.action = 'user?access_token=%s' % self.token
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
             
        self.opener.get_method = lambda: 'GET'
        
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, None)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_authenticated = False
        else:
           self.is_authenticated = True
           self.username = data['user']['name']
           
class GetCode(object):
    def __init__(self):
        self.client_id = '845mHJx5-CxI8dSlStHB'
        self.action = 'oauth/device/code'
        request_data = urllib.parse.urlencode({
            'client_id' : self.client_id
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_code = False
        else:
           self.is_code = True
           self.device_code = data['device_code']
           self.user_code = data['user_code']
           self.verification_url = data['verification_url']
           self.expires_in = data['expires_in']
           self.interval = data['interval']

class Authorize(object):
    def __init__(self, code):
        self.client_id = '845mHJx5-CxI8dSlStHB'
        self.client_secret = 'lvN6LZOZkUAH8aa_WAbvAJ4AXGcSo7irZyAPdRQj'
        self.action = 'oauth/access_token'
        self.code = code
        request_data = urllib.parse.urlencode({
            'client_id' : self.client_id,
            'client_secret' : self.client_secret,
            'code' : self.code
        }).encode("utf-8")
        
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', 'Lynx/2.8.1pre.9 libwww-FM/2.14')
        ]
                           
        self.opener.get_method = lambda: 'POST'
             
        request_url = "%s%s" % (request_uri, self.action)
        try:
            response = self.opener.open(request_url, request_data)
            data = json.loads(response.read())
        except:
            data = None
        
        if (data is None) or (data['result'] == "KO"):
           self.is_authorized = False
           self.message = data['message']
        else:
           self.is_authorized = True
           self.access_token = data['access_token']
