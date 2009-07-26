import logging
import xml.etree.cElementTree as ET
from google.appengine.api import urlfetch

# xml to dict stuff from 
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/410469
class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})

def xml2dict(xml_string):
    """Returns a dictionary representation of xml in string `xml_string`"""

    root = ET.fromstring(xml_string)
    return XmlDictConfig(root)

class OohEmbedError(Exception):
    def __init__(self, value):
        self.reason = value

    def __str__(self):
        return repr(self.reason)

class UnsupportedUrlError(OohEmbedError):
    def __init__(self):
        super(UnsupportedUrlError, self).__init__("This provider does not support this URL")

class HTTPError(Exception):
    def __init__(self, url, code, content=""):
        self.url = url
        self.code = code
        self.content = content

    def __str__(self):
        return "HTTPError %s on url %s" % (self.url, self.code)

def get_url(url):
    try:
        result = urlfetch.fetch(url, headers={'User-Agent': 'oohEmbed.com'})
        if result.status_code != 200:
            logging.debug('Error code %s while fetching url: %s' % (result.status_code, url))
            raise HTTPError(url, result.status_code, result.content)
        else:
            return result.content
    except urlfetch.Error, e:
        logging.warn("Error fetching url %s" % url, exc_info=True)
        raise OohEmbedError("Error fetching url %s" % query_url)


def make_key(query_url, extra_params):
    keys = sorted(extra_params.keys())
    return query_url + "|".join(["%s:%s" % (key, extra_params[key]) for key in keys])
