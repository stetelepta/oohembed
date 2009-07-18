import logging
import re
import urllib

from django.utils import simplejson as json
from google.appengine.api import urlfetch

from base import Provider

class Proxy():
    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            return None

        params = {'url': query_url, 'format': 'json'}
        if extra_params:
            params.update(extra_params)

        fetch_url = self.service_url + urllib.urlencode(params)

        try:
            result = urlfetch.fetch(fetch_url)
            if result.status_code != 200:
                logging.error('%s returned error (code %s): "%s" for url: %s' % (
                         self.title, result.status_code, result.content, query_url))
                return None
            else:
                return result.content
        except urlfetch.Error, e:
            logging.error("error fetching url %s" % query_url, exc_info=True)
            return None


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
