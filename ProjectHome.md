This project hosts the source code that powers oohEmbed.com

## No Longer Supported ##

oohEmbed.com was [acquired by Embedly](http://blog.embed.ly/oohembed) and since then, the site runs on Embedly's infrastructure and not using the code derived from this project.

This project is basically in archive mode now. Feel free to fork it and use it to host your own instances on App Engine. If you prefer not to use App Engine, then a few changes should get the code up & running in any Python WSGI environment.

## What is oohEmbed? ##

In a nutshell: _oohEmbed is an oEmbed compatible provider of HTML embed codes for various web sites._

What is this oEmbed? From [oembed.com](http://www.oembed.com/):

> oEmbed is a format for allowing an embedded representation of a URL on third party sites. The simple API allows a website to display embedded content (such as photos or videos) when a user posts a link to that resource, without having to parse the resource directly.

Still don't get it? Perhaps an example will make things clear. If you make a URL request like this:

> `http://oohembed.com/oohembed/?url=http%3A//www.amazon.com/Myths-Innovation-Scott-Berkun/dp/0596527055/`

You will get this as the response:

```
{
     "asin": "0596527055",
     "title": "The Myths of Innovation",
     "url": "http://ecx.images-amazon.com/images/I/31%2BfVjL2nqL.jpg",
     "thumbnail_width": "48",
     "height": "500",
     "width": "317",
     "version": "1.0",
     "author_name": "Scott Berkun",
     "provider_name": "Amazon Product Image",
     "thumbnail_url": "http://ecx.images-amazon.com/images/I/31%2BfVjL2nqL._SL75_.jpg",
     "type": "photo",
     "thumbnail_height": "75",
     "author_url": "http://www.amazon.com/gp/redirect.html%3FASIN=0596527055%26location=/Myths-Innovation-Scott-Berkun/dp/0596527055"
}
```

That should make everything clear. No? Then head over to http://oohEmbed.com/ for more details!

## Brief Overview ##

oohEmbed is running on Google App Engine and so what you see in the [source repository](http://code.google.com/p/oohembed/source/browse/) here is a Python app meant to run on App Engine. Thus, some familiarity with App Engine would be a good thing to have before jumping into the code.

Although oohEmbed is a Google App Engine app, it contains very little App Engine specific code. Apart from the use of `urlfetch`, everything else is standard Python and should run anywhere else that Python runs.

The codebase is so small that hopefully, it is self-explanatory :-) If you have any questions, please feel free to ask!