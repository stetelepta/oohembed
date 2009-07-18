import logging
import re
import urllib
import xml.etree.cElementTree as ET

from django.utils import simplejson as json
from google.appengine.api import urlfetch

from base import Provider

class ImdbProvider(object):
    """Photo and some metadata for IMDb movie urls. Check sample response to see what metadata beyond that
    specified by the oEmbed spec is returned. Note that sometimes, a photo can't be found in which case
    you will get a link type response."""
    title = 'IMDb'
    url = r'http://*.imdb.com/title/tt*/'
    url_re = r'imdb.com/title/(?P<resource>tt\d{7,7})'
    example_url = 'http://www.imdb.com/title/tt0468569/'

    IMDB_NS = '{http://webservice.imdb.com/doc/2006-12-15/}'

    def set_value(self, elem, tag, d, key):
        """Check `tag` with Element `elem`. If exists, set `text` of tag
        as value of `key` in dictionary `d`. NOTE: `d` is modified for caller."""

        e = elem.find('.//' + self.IMDB_NS + tag)
        if e is not None and e.text:
            d[key] = e.text
            return True
        else:
            return False

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            return None

        resource_id = matches.group('resource')
        params = urllib.urlencode({'ResourceId': resource_id})

        fetch_url = 'http://cc00.clearspring.com/imdb/LookupTitle?' + params

        try:
            result = urlfetch.fetch(fetch_url)
            if result.status_code != 200:
                logging.error('imdb returned error (code %s): "%s" for url: %s' % (result.status_code, result.content, query_url))
                return None
        except urlfetch.Error, e:
            logging.error("error fetching url %s" % query_url, exc_info=True)
            return None

        response = {'type': u'photo', 'version': u'1.0', 'provider_name': self.title}

        tree = ET.fromstring(result.content)
        if not self.set_value(tree, 'Source', response, 'url'):
            response['type'] = 'link'
        else:
            self.set_value(tree, 'Width', response, 'width')
            self.set_value(tree, 'Height', response, 'height')

        self.set_value(tree, 'Title', response, 'title')
        self.set_value(tree, 'Year', response, 'year')

        e = tree.find('.//'+self.IMDB_NS+'Director')
        if e:
            self.set_value(e, 'Name', response, 'author_name')
            self.set_value(e, 'NameId', response, 'author_url')

        if self.set_value(tree, 'PlotSummary', response, 'html'):
            response['html'] =  u'<p>' + response['html'] + u'</p>'

        self.set_value(tree, 'Average', response, 'rating')

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response
        

class AmazonProvider(Provider):
    """Product images (and author_name for books) for Amazon products. Will soon honour maxwidth/maxheight"""
    title = 'Amazon Product Image'
    url_re = r'amazon\.(?:com|co\.uk|de|ca|jp)/.*/?(?:gp/product|o/ASIN|obidos/ASIN|dp)/(?P<asin>\w{8,11})[/\?]?'
    url = 'http://*.amazon.(com|co.uk|de|ca|jp)/*/(gp/product|o/ASIN|obidos/ASIN|dp)/*'
    example_url = 'http://www.amazon.com/Myths-Innovation-Scott-Berkun/dp/0596527055'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            return None

        params = {'Service': 'AWSECommerceService',
                'SubscriptionId': '1FTX8DJ3D0NCX9DRWQR2', # Please don't abuse!
                'AssociateTag': 'antrixnet-20',
                'Operation': 'ItemLookup',
                'ResponseGroup': 'Images,ItemAttributes',
                'Style': 'http://oohembed.com/static/amazon_json.xsl',
                'ContentType': 'text/javascript',
                'IdType': 'ASIN',
                'ItemId': matches.group('asin')}
        fetch_url = 'http://xml-us.amznxslt.com/onca/xml?' + urllib.urlencode(params)

        try:
            result = urlfetch.fetch(fetch_url)
            if result.status_code != 200:
                logging.error('amazon returned error (code %s): "%s" for url: %s' % (result.status_code, result.content, query_url))
                return None
        except urlfetch.Error, e:
            logging.error("error fetching url %s" % query_url, exc_info=True)
            return None

        try:
            parsed = json.loads(result.content)
        except:
            logging.error("error decoding as json. String was\n%s" % result.content, exc_info=True)
            return None

        item = parsed['Item']

        # The returned item contains small, medium and large image details
        # Each size is in nested dict in `item` with keyname `img_<size>`. 
        # We pick the one we want and move it up to the item dict.

        item.update(item['img_large'])

        # Now we create a response by selecting all needed key/value pairs from `item`.
        # This mostly means removing `img_*` keys since the size we want is already
        # in top-level of `item`.
        # However, sometimes we don't get image details so 'url', 'thumbnail_url', etc.,
        # attribute values will be empty strings. So we also prune those now.

        selected = dict((k, v) for k, v in item.iteritems() 
                                    if not k.startswith('img_') and v)

        if not 'url' in selected:
            # Return a standard Amazon.com logo
            selected['url'] = \
                'http://images.amazon.com/images/G/01/x-locale/browse/upf/amzn-logo-5.gif'
            selected['width'] = 140
            selected['height'] = 66

        response = {'type': u'photo', 'version': u'1.0', 'provider_name': self.title}
        response.update(selected)

        # The returned url includes Subscription ID, etc. Replace it.
        response['author_url'] = query_url

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response

class TwitPicProvider(Provider):
    """Photo and thumbnail for TwitPic.com photos."""
    title = 'TwitPic'
    url = r'http://*.twitpic.com/*'
    url_re = r'twitpic.com/(?P<id>\w+)'
    example_url = 'http://www.twitpic.com/1pz6z'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            return None

        photo_url = 'http://twitpic.com/show/full/' + matches.group('id')
        thumb_url = 'http://twitpic.com/show/thumb/' + matches.group('id')

        response = {'type': u'photo', 'version': u'1.0', 'provider_name': self.title,
                    'thumbnail_url': thumb_url, 'thumbnail_width': 150, 'thumbnail_height': 150,
                    'url': photo_url}

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response

class LJAvatarProvider(Provider):
    """Avatar image for LiveJournal user. Uses http://ljpic.seacrow.com/"""
    title = 'LiveJournal UserPic'
    url = r'http://*.livejournal.com/'
    url_re = r'(?P<id>\w+).livejournal.com'
    example_url = 'http://jace.livejournal.com'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            return None

        fetch_url = 'http://ljpic.seacrow.com/json/' + matches.group('id') 
        try:
            result = urlfetch.fetch(fetch_url)
            if result.status_code != 200:
                logging.error('LJPic returned error (code %s): "%s" for url: %s' % (result.status_code, result.content, query_url))
                return None
        except urlfetch.Error, e:
            logging.error("error fetching url %s" % query_url, exc_info=True)
            return None

        try:
            parsed = json.loads(result.content)
        except:
            logging.error("error decoding as json. String was\n%s" % result.content, exc_info=True)
            return None

        response = {'type': u'photo', 'version': u'1.0', 'provider_name': self.title,
                'url': parsed['image'], 'author_name': parsed['name']}

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response
