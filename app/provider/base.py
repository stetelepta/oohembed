import re
from google.appengine.api import urlfetch

"""Plugin infrastructure based on Marty Alchin's post at
http://gulopine.gamemusic.org/2008/jan/10/simple-plugin-framework/
"""
class ProviderMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

    def get_providers(self, *args, **kwargs):
        return [p(*args, **kwargs) for p in self.plugins]

class Provider(object):
    """
    Mount point for plugins which refer to actions that can be performed.
    Plugins implementing this reference should provide the following attributes:
    ========  ========================================================
    title     the site/api for which this provider works
    url       friendly url description - ombed.com's configuration URL scheme
    url_re    the regex pattern for the URLs which the provider works for
    example_url  An exemplary URL that this provider should be able to work with
    ========  ========================================================

    With the provided url_re, this class' constructor will create a 
    class attribute named `url_regex`.
    """
    __metaclass__ = ProviderMount

    def __init__(self):
        self.__class__.url_regex = re.compile(self.__class__.url_re, re.I|re.UNICODE)

