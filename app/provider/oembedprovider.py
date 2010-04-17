import logging
import re
import urllib

from django.utils import simplejson as json

from base import Provider
from utils import *

class Proxy():
    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        params = {'url': query_url, 'format': 'json'}
        if extra_params:
            params.update(extra_params)

        fetch_url = self.service_url + urllib.urlencode(params)
        result = get_url(fetch_url)
        return result

class FlickrProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'Flickr Photos'
    url = 'http://*.flickr.com/photos/*'
    url_re = r'flickr\.com/photos/[-.\w@]+/(?P<id>\d+)/?'
    example_url = 'http://www.flickr.com/photos/fuffer2005/2435339994/'

    service_url = 'http://www.flickr.com/services/oembed/?'

class ViddlerProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'Viddler Video'
    url = 'http://*.viddler.com/explore/*'
    url_re = r'viddler\.com/explore/.*/videos/(?P<id>\w+)/?'
    example_url = 'http://www.viddler.com/explore/engadget/videos/14/'

    service_url = 'http://lab.viddler.com/services/oembed/?'

class QikProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'Qik Video'
    url = 'http://qik.com/*'
    url_re = r'qik\.com/\w+'
    example_url = 'http://qik.com/video/86776'

    service_url = 'http://qik.com/api/oembed.json?'

class HuluProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'Hulu'
    url = 'http://www.hulu.com/watch/*'
    url_re = r'hulu\.com/watch/.*'
    example_url = 'http://www.hulu.com/watch/20807/late-night-with-conan'

    service_url = 'http://www.hulu.com/api/oembed.json?'

class Revision3Provider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'Revision3'
    url = 'http://*.revision3.com/*'
    url_re = r'revision3\.com/.*'
    example_url = 'http://revision3.com/diggnation/2008-04-17xsanned/'

    service_url = 'http://revision3.com/api/oembed/?'

class VimeoProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'Vimeo'
    url = 'http://www.vimeo.com/* and http://www.vimeo.com/groups/*/videos/*'
    url_re = r'vimeo\.com/.*'
    example_url = 'http://www.vimeo.com/1211060'

    service_url = 'http://www.vimeo.com/api/oembed.json?'

class NFBProvider(Provider, Proxy):
    """Provides video embed codes for nfb.ca - the National Film Board of Canada.
    This is just a proxy for the original oEmbed compliant service."""
    title = 'National Film Board of Canada'
    url = 'http://*.nfb.ca/film/*'
    url_re = r'nfb\.ca/film/(?P<id>[-\w]+)/?'
    example_url = 'http://www.nfb.ca/film/blackfly/'

    service_url = 'http://www.nfb.ca/remote/services/oembed/?'

class DailymotionProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'Dailymotion'
    url = 'http://*.dailymotion.com/*'
    url_re = r'dailymotion\.com/.*'
    example_url = 'http://www.dailymotion.com/video/x5ioet_phoenix-mars-lander_tech'

    service_url = 'http://www.dailymotion.com/api/oembed/?'

class BlipTVProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'blip.tv'
    url = 'http://*.blip.tv/*'
    url_re = r'blip\.tv/.*'
    example_url = 'http://pycon.blip.tv/file/2058801/'

    service_url = 'http://blip.tv/oembed/?'

class ScribdProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'Scribd'
    url = 'http://*.scribd.com/*'
    url_re = r'scribd\.com/.*'
    example_url = 'http://www.scribd.com/doc/17896323/Indian-Automobile-industryPEST'

    service_url = 'http://www.scribd.com/services/oembed?'

class MovieClipsProvider(object):
    #class MovieClipsProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'Movieclips'
    url = 'http://movieclips.com/watch/*/*/'
    url_re = r'moviesclips\.com/watch/.*'
    example_url = 'http://movieclips.com/1/2/'

    service_url = 'http://movieclips.com/services/oembed/?'


class YoutubeProvider(Provider, Proxy):
    """Just a proxy for the original oEmbed compliant service"""
    title = 'YouTube'
    url = 'http://*.youtube.com/watch*'
    url_re = r'youtube\.com/watch.+v=(?P<videoid>[\w-]+)&?' 
    example_url = 'http://www.youtube.com/watch?v=vk1HvP7NO5w'

    service_url = 'http://www.youtube.com/oembed?'

