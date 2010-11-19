import logging
import re
import urllib
import xml.etree.cElementTree as ET
import base64
import hashlib
import hmac
import time

from django.utils import simplejson as json
from BeautifulSoup import BeautifulSoup, NavigableString

from base import Provider
from utils import *
from secrets import *

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
            raise UnsupportedUrlError()

        resource_id = matches.group('resource')
        params = urllib.urlencode({'ResourceId': resource_id})

        fetch_url = 'http://cc00.clearspring.com/imdb/LookupTitle?' + params
        result = get_url(fetch_url)

        response = {'type': u'photo', 'version': u'1.0', 'provider_name': self.title}

        tree = ET.fromstring(result)
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
            raise UnsupportedUrlError()

        params = {'Service': 'AWSECommerceService',
                'AWSAccessKeyId': AWS_ACCESS_KEY_ID, # Please don't abuse!
                'AssociateTag': 'antrixnet-20',
                'Operation': 'ItemLookup',
                'ResponseGroup': 'Images,ItemAttributes',
                'Style': 'http://oohembed.com/static/amazon_json.xsl',
                'ContentType': 'text/javascript',
                'IdType': 'ASIN',
                'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()), #ISO 8601
                'ItemId': matches.group('asin')}

        str_to_sign = "GET" + "\n" + "xml-us.amznxslt.com" + "\n" + "/onca/xml" + "\n"
        str_to_sign = str_to_sign + urllib.urlencode(sorted(params.items())) # All query params sorted

        signature = hmac.new(key=AWS_SECRET_ACCESS_KEY, msg=str_to_sign,
                                digestmod=hashlib.sha256).digest()
         
        signature = base64.encodestring(signature).strip("\n") # base64.urlsafe_b64encode(signature)
        
        params['Signature'] = signature # Add the Signature to the query params

        fetch_url = 'http://xml-us.amznxslt.com/onca/xml?' + urllib.urlencode(params)

        result = get_url(fetch_url)

        try:
            parsed = json.loads(result)
        except:
            logging.error("error decoding as json. String was\n%s" % result, exc_info=True)
            raise OohEmbedError("Error decoding response from Amazon.")

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
            raise UnsupportedUrlError()

        photo_url = 'http://twitpic.com/show/full/' + matches.group('id')
        thumb_url = 'http://twitpic.com/show/thumb/' + matches.group('id')

        response = {'type': u'photo', 'version': u'1.0', 'provider_name': self.title,
                    'thumbnail_url': thumb_url, 'thumbnail_width': 150, 'thumbnail_height': 150,
                    'url': photo_url}

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response

class PhodroidProvider(Provider):
    """Provider for phodroid.com photos."""
    title = 'Phodroid Photos'
    url = r'http://*.phodroid.com/*/*/*'
    url_re = r'phodroid.com/(?P<id>\d\d/\d\d/\w+)/?'
    example_url = 'http://phodroid.com/09/06/k3q6bd'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        photo_url = 'http://s.phodroid.com/' + matches.group('id') + '.jpg'

        response = {'type': u'photo', 'version': u'1.0', 'provider_name': self.title,
                    'url': photo_url}

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response

class LJAvatarProvider(Provider):
    """Avatar image for LiveJournal user. Uses http://ljpic.seacrow.com/"""
    title = 'LiveJournal UserPic'
    url = r'http://*.livejournal.com/'
    url_re = r'(?P<id>\w+).livejournal.com/?$'
    example_url = 'http://jace.livejournal.com'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        fetch_url = 'http://ljpic.seacrow.com/json/' + matches.group('id') 
        result = get_url(fetch_url)

        try:
            parsed = json.loads(result)
        except:
            logging.error("error decoding as json. String was\n%s" % result, exc_info=True)
            raise OohEmbedError("Error decoding response from LJPic.")

        response = {'type': u'photo', 'version': u'1.0', 'provider_name': self.title,
                'url': parsed['image'], 'author_name': parsed['name']}

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response

class XKCDProvider(Provider):
    """Provides the comic image link for an xkcd.com comic page"""

    title = 'XKCD Comic'
    url = r'http://*.xkcd.com/*/'
    url_re = r'xkcd\.com/\d+/?$'
    example_url = 'http://xkcd.com/310/'

    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        result = get_url(query_url)

        soup = BeautifulSoup(result)

        photo = soup.find('div', id='contentContainer').find('img')

        response = {'type': u'photo', 'version': u'1.0', 'provider_name': self.title,
                'url': photo['src'], 'title': photo['alt'], 'author_name': 'Randall Munroe',
                'author_url': 'http://xkcd.com/'}

        json_response = json.dumps(response, ensure_ascii=False, indent=1)
        return json_response
