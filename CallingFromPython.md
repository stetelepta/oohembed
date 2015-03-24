# Getting Started #

The easiest way to call oohembed from python is by using [python-oembed](http://code.google.com/p/python-oembed/)

[Download](http://code.google.com/p/python-oembed/downloads/list) and install python-oembed to get started.

# Using python-oembed with oohembed #

below sample shows how to use oohembed for various services:

```
import oembed
import pprint

consumer = oembed.OEmbedConsumer()
endpoint = oembed.OEmbedEndpoint('http://oohembed.com/oohembed','*')
consumer.addEndpoint(endpoint)

#now this consumer can be used with several oEmbed providers.
response = consumer.embed('http://www.flickr.com/photos/wizardbt/2584979382/')
pprint.pprint(response.getData())

response = consumer.embed('http://www.youtube.com/watch?v=vk1HvP7NO5w')
pprint.pprint(response.getData())

response = consumer.embed('http://www.metacafe.com/watch/1350976/funny_call/')
pprint.pprint(response.getData())

response = consumer.embed('http://twitter.com/mai_co_jp/statuses/822499364')
pprint.pprint(response.getData())

response = consumer.embed('http://en.wikipedia.org/wiki/Life_on_Mars_(TV_series)')
pprint.pprint(response.getData())

#Other elements can be accessed like;
print response['url']
print response['html']

```