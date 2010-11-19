import os
import re
import urllib

from django.utils import simplejson as json

from base import ProviderMount, Provider
from utils import *

class Proxy():
    def provide(self, query_url, extra_params=None):
        matches = self.url_regex.search(query_url)
        if not matches:
            raise UnsupportedUrlError()

        params = {'url': query_url, 'format': 'json'}
        if extra_params:
            params.update(extra_params)

        fetch_url = self.endpoint_url + urllib.urlencode(params)
        result = get_url(fetch_url)
        return result


def load_providers():
    """Loads OEmbed compliant providers from a json source"""

    fp = open(os.path.join(os.path.split(__file__)[0], "endpoints.json"))

    providers = json.load(fp)

    for provider in providers:
        provider["endpoint_url"] = provider["endpoint_url"] + "?" # For ease in Proxy.provide()
        provider["__doc__"] = "Just a proxy for the original oEmbed compliant service"

        clazz_name = ''.join(provider["title"].strip().split()) # remove whitespace
        clazz_name = str(clazz_name) # coerce to string

        clazz = ProviderMount(clazz_name, (Provider, Proxy), provider)

load_providers()
