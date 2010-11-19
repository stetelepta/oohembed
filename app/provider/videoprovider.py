import logging
import re
import urllib
import xml.etree.cElementTree as ET

from django.utils import simplejson as json
import feedparser

from base import Provider
from utils import *
from secrets import *

class YoutubeProvider(object):
    """Provides the flash video embed code
    __NOTE:__ This is deprecated now. Youtube is handled via the upstream
    oembed provider. See oembedprovider.py """

    title = 'Youtube'
    url = 'http://*.youtube.com/watch*'
    url_re = r'youtube\.com/watch.+v=(?P<videoid>[\w-]+)&?' 
    example_url = 'http://www.youtube.com/watch?v=vk1HvP7NO5w'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        fetch_url = 'http://gdata.youtube.com/feeds/api/videos/' + matches.group('videoid') + '?alt=json'  

        try:
            result = urlfetch.fetch(fetch_url)
            if result.status_code != 200:
                logging.error('Youtube returned error (code %s): "%s" for url: %s' % (result.status_code, result.content, query_url))
                return None
        except urlfetch.Error, e:
            logging.error("error fetching url %s" % query_url, exc_info=True)
            return None

        try:
            parsed = json.loads(result.content)
            entry = parsed['entry']
        except:
            logging.error("error decoding as json. String was\n%s" % result.content, exc_info=True)
            return None

        author_name = entry['author'][0]['name']['$t']
        author_url = 'http://www.youtube.com/user/' + author_name
        title = entry['title']['$t']
        response = {'type': u'video', 'version': u'1.0', 'provider_name': self.title,
                'title': title, 'author_name': author_name, 'author_url': author_url,
                'width': 425, 'height': 344} 

        thumbnails = entry['media$group']['media$thumbnail']
        for thumb in thumbnails:
            if thumb['url'].endswith('1.jpg'):
                response['thumbnail_url'] = thumb['url']
                response['thumbnail_width'] = thumb['width']
                response['thumbnail_height'] = thumb['height']
                break

        html = "<embed src='http://www.youtube.com/v/%s&fs=1' allowfullscreen='true' " \
                "type='application/x-shockwave-flash' wmode='transparent' width='425' " \
                "height='344'></embed>" % matches.group('videoid')

        response['html'] = html

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response

class MetacafeProvider(Provider):
    """Provides the flash video embed code"""
    title = 'Metacafe'
    url = 'http://*.metacafe.com/watch/*'
    url_re = r'metacafe\.com/watch/(?P<videoid>[-\w]+)/.+'
    example_url = 'http://www.metacafe.com/watch/1350976/funny_call/'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        fetch_url = 'http://www.metacafe.com/api/item/' + matches.group('videoid') + '/'  

        try:
            result = urlfetch.fetch(fetch_url)
            if result.status_code != 200:
                logging.error('Metacafe returned error (code %s): "%s" for url: %s' % (result.status_code, result.content, query_url))
                return None
        except urlfetch.Error, e:
            logging.error("error fetching url %s" % query_url, exc_info=True)
            return None

        try:
            parsed = feedparser.parse(result.content)
            entry = parsed['entries'][0]
        except:
            logging.error("error decoding feed. String was\n%s" % result.content, exc_info=True)
            return None

        title = entry['title']
        author_name = entry['author']
        response = {'type': u'video', 'version': u'1.0', 'provider_name': self.title,
                    'title': title, 'author_name': author_name, 'width': 425, 'height': 344,
                    'thumbnail_url': 'http://www.metacafe.com/thumb/' + matches.group('videoid') + '.jpg',
                    'thumbnail_width': 136, 'thumbnail_height': 81
                   }
        response['html'] = "<embed src='http://www.metacafe.com/fplayer/%s/movie.swf' style='width:400px; height:345px;' width='400' height='345' wmode='transparent' type='application/x-shockwave-flash'></embed>" % matches.group('videoid')

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response

class GoogleVideoProvider(Provider):
    """Provides the flash video embed code"""
    title = 'Google Video'
    url = 'http://video.google.com/videoplay?*'
    url_re = r'video\.google\.com/videoplay.+docid=(?P<videoid>[\d-]+)&?'
    example_url = 'http://video.google.com/videoplay?docid=8372603330420559198'

    json_template = u"""{
    "version": "1.0",
    "type": "video",
    "provider_name": "Google Video",
    "width": 400,
    "height": 326,
    "html": "<embed style='width:400px; height:326px;' type='application/x-shockwave-flash' src='http://video.google.com/googleplayer.swf?docId=%s&amp;hl=en' width='400' height='326'></embed>"
}"""

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        return self.json_template % matches.group('videoid')

class CollegeHumorVideoProvider(Provider):
    """Provides the flash video embed code"""
    title = 'CollegeHumor Video'
    url = 'http://*.collegehumor.com/video:*'
    url_re = r'collegehumor\.com/video:(?P<videoid>[\d]+)'
    example_url = 'http://www.collegehumor.com/video:1772239'

    json_template = u"""{
    "version": "1.0",
    "type": "video",
    "provider_name": "CollegeHumor Video",
    "width": 480,
    "height": 360,
    "html": "<embed style='width:480px; height:360px;' width='480' height='360' type='application/x-shockwave-flash' src='http://www.collegehumor.com/moogaloop/moogaloop.swf?clip_id=%s&fullscreen=1' ></embed>"
}"""

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        return self.json_template % matches.group('videoid')

class FunnyOrDieProvider(Provider):
    """Provides the flash video embed code"""
    title = 'Funny or Die Video'
    url = 'http://*.funnyordie.com/videos/*'
    url_re = r'funnyordie\.com/videos/(?P<videoid>\w+)'
    example_url = 'http://www.funnyordie.com/videos/eae26bb96d'

    json_template = u"""{
    "version": "1.0",
    "type": "video",
    "provider_name": "Funny Or Die Video",
    "width": 464,
    "height": 388,
    "html": "<embed width='464' height='388' flashvars='key=%s' allowfullscreen='true' quality='high' src='http://www2.funnyordie.com/public/flash/fodplayer.swf?7228' type='application/x-shockwave-flash'></embed>"
}"""

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        return self.json_template % matches.group('videoid')

class FiveMinVideoProvider(Provider):
    """Provides the flash video embed code"""
    title = '5min.com'
    url = 'http://*.5min.com/Video/*'
    url_re = r'5min\.com/Video/.*-(?P<videoid>[\d]+)$'
    example_url = 'http://www.5min.com/Video/Chocolate-Marquise-Recipe-89007978'

    json_template = u"""{
    "version": "1.0",
    "type": "video",
    "provider_name": "5min.com Video",
    "width": 480,
    "height": 401,
    "html": "<embed style='width:480px; height:401px;' width='480' height='401' type='application/x-shockwave-flash' src='http://www.5min.com/Embeded/%s/' allowFullscreen='true'></embed>"
}"""

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        return self.json_template % matches.group('videoid')

class DailyShowVideoProvider(Provider):
    """Provides the flash video embed code"""
    title = 'Daily Show with Jon Stewart'
    url = 'http://*.thedailyshow.com/video/*'
    url_re = r'thedailyshow\.com/video/index\.jhtml.*videoId=(?P<videoid>[\d]+)'
    example_url = 'http://www.thedailyshow.com/video/index.jhtml?videoId=210855&title=CNN%27s-Magic-Wall-Conspiracy-Thriller'

    json_template = u"""{
    "version": "1.0",
    "type": "video",
    "provider_name": "Daily Show with Jon Stewart",
    "width": 360,
    "height": 301,
    "html": "<embed style='width:360px; height:301px;' width='360' height='301' type='application/x-shockwave-flash' src='http://media.mtvnservices.com/mgid:cms:item:comedycentral.com:%s' allowFullscreen='true'></embed>"
}"""

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        return self.json_template % matches.group('videoid')

class SlideShareProvider(Provider):
    """Provides the embed code for slideshow"""
    title = 'SlideShare'
    url = 'http://*.slideshare.net/*'
    url_re = r'slideshare\.net/.+'
    example_url = 'http://www.slideshare.net/igniteportland/' \
            'how-to-run-a-startup-without-losing-your-mind'

    _api_key = SLIDESHARE_KEY
    _api_secret = SLIDESHARE_SECRET
    _api_url = 'http://www.slideshare.net/api/2/get_slideshow?'

    def fetch_info(self, query_url):
        from hashlib import sha1
        import time

        ts = int(time.time())  # unix timestamp

        params = {'api_key': self._api_key,
                  'ts': ts,
                  'hash': sha1(self._api_secret + str(ts)).hexdigest(),
                  'slideshow_url': query_url}

        fetch_url = self._api_url + urllib.urlencode(params)
        result = get_url(fetch_url)
        return result

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        result = self.fetch_info(query_url)
        
        if not result:
            raise OohEmbedError("Did not get response from SlideShare")

        if "SlideShareServiceError" in result:
            error_msg = ET.fromstring(result) 
            error_msg = error_msg.find("Message")
            if error_msg is not None:
                raise OohEmbedError("SlideShare returned error: %s" % error_msg.text)
            else:
                logging.error("SlideShare error response: %s" % result)
                raise OohEmbedError("SlideShare returned error: %s" % result)

        result = xml2dict(result) 

        response = {'version' : '1.0',
                    'type': 'rich',
                    'provider_name': self.title
                    }

        response['title'] = result['Title']

        # Slideshare's embed code is wrapped in an extra
        # left-aligned div. Strip that div out
        m = re.match(r'<div.*?>(?P<code>.+)</div>', result['Embed'], re.I)
        if not m:
            raise OohEmbedError("Could not parse response from SlideShare")

        response['html'] = m.group('code')

        m = re.search(r'width="(?P<width>\d+)"', response['html'], re.I)
        if m:
            response['width'] = m.group('width')

        m = re.search(r'height="(?P<height>\d+)"', response['html'], re.I)
        if m:
            response['height'] = m.group('height')

        try:
            response['author_name'] = result['Username']
            response['author_url'] = 'http://www.slideshare.net/'+result['Username']
        except KeyError:
            pass

        response['thumbnail_url'] = result['ThumbnailURL']

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response

