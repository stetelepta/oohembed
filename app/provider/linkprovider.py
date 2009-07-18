import logging
import re
import urllib

from django.utils import simplejson as json
from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulSoup, NavigableString

from base import Provider

class TwitterStatusProvider(Provider):
    """Provides info on a particular tweet as a link type oEmbed response"""
    title = 'Twitter Status'
    url = 'http://twitter.com/*/statuses/*'
    url_re = r'twitter\.com/(?P<user>\w+)/statuses/(?P<status>\d+)'
    example_url = 'http://twitter.com/mai_co_jp/statuses/822499364'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            return None

        fetch_url = 'http://twitter.com/statuses/show/' + matches.group('status') + '.json'
        try:
            result = urlfetch.fetch(fetch_url)
            if result.status_code != 200:
                logging.error('twitter returned error (code %s): "%s" for url: %s' % (result.status_code, result.content, query_url))
                return None
        except urlfetch.Error, e:
            logging.error("error fetching url %s" % query_url, exc_info=True)
            return None

        try:
            parsed = json.loads(result.content)
        except:
            logging.error("error decoding as json. String was\n%s" % result.content, exc_info=True)
            return None

        response = {'type': u'link', 'version': u'1.0', 'provider_name': self.title}

        if not 'text' in parsed:
            return None
        else:
            response['title'] = parsed['text']

        if 'user' in parsed:
            u = parsed['user']
            if 'name' in u:
                response['author_name'] = u['name']
            elif 'screen_name' in u:
                response['author_name'] = u['screen_name']

            if 'url' in u:
                response['author_url'] = u['url']

            if 'profile_image_url' in u:
                response['thumbnail_url'] = u['profile_image_url']
                response['thumbnail_width'] = 48
                response['thumbnail_height'] = 48

        json_response = json.dumps(response, ensure_ascii=False, indent=0)
        return json_response


class WikipediaProvider(Provider):
    """Returns lead content from a Wikipedia page as 'html' attribute of link type oEmbed response"""
    title = 'Wikipedia'
    url = 'http://*.wikipedia.org/wiki/*'
    #url_re = r'wikipedia\.org/wiki/(?P<title>[-\w\.\(\)]+)'
    url_re = r'wikipedia\.org/wiki/(?P<title>[^&=]+)'
    example_url = 'http://en.wikipedia.org/wiki/Life_on_Mars_(TV_series)'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            return None

        fetch_url = query_url + '?action=render'
        try:
            result = urlfetch.fetch(fetch_url)
            if result.status_code != 200:
                logging.error('wikipedia returned error (code %s): "%s" for url: %s' % (
                                    result.status_code, result.content, query_url))
                return None
        except urlfetch.Error, e:
            logging.error("error fetching url %s" % query_url, exc_info=True)
            return None

        soup = BeautifulSoup(result.content)

        page = u''
        count = 0

        for para in soup('p', recursive=False):
            page += unicode(para)
            count += 1
            if count >= 3: break

        response = {'type': u'link', 'version': u'1.0', 'provider_name': self.title}

        page_title = unicode(matches.group('title'), 'utf-8')
        page_title = urllib.unquote(page_title).replace('_', ' ')

        response['title'] = page_title
        response['html'] = page

        json_response = json.dumps(response, ensure_ascii=True, indent=0)
        return json_response

class WordpressProvider(Provider):
    """Returns lead content from a Wordpress.com blog post page as 'html' attribute of link type oEmbed response"""
    title = 'Wordpress.com'
    url = 'http://*.wordpress.com/yyyy/mm/dd/*'
    url_re = r'wordpress\.com/\d{4}/\d{2}/\d{2}/(?P<slug>[-\w\.]+)'
    example_url = 'http://martinpitt.wordpress.com/2008/05/07/my-computer-discovered-playing-games/'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            return None

        fetch_url = query_url 
        try:
            result = urlfetch.fetch(fetch_url)
            if result.status_code != 200:
                logging.error(u'Wordpress returned error (code %s): "%s" for url: %s' % (
                                result.status_code, unicode(result.content, 'utf-8'), query_url))
                return None
        except urlfetch.Error, e:
            logging.error(u"error fetching url %s" % query_url, exc_info=True)
            return None

        soup = BeautifulSoup(result.content)

        response = {'type': u'link', 'version': u'1.0', 'provider_name': self.title}
        
        response['title'] = unicode(soup.title.string)

        content = soup.find('div', 'snap_preview')
        if not content:
            logging.error("Didn't find any snap_preview node on this page: %s" % query_url)
            return None

        page = u''
        count = 1000
        para = content.first()
        if not para:
            logging.error("Didn't find any first paragraph on this page: %s" % query_url)
            return None

        while len(page) <= count:
            page += unicode(para)
            para = para.nextSibling
            if not para:
                break

        if len(page) > count:
            page = page[:count] + ' ...'

        response['html'] = unicode(BeautifulSoup(page))

        json_response = json.dumps(response, ensure_ascii=False, indent=0)
        return json_response
