String.prototype.supplant = function (o) {
    /* http://javascript.crockford.com/remedial.html */
    return this.replace(/{([^{}]*)}/g,
        function (a, b) {
            var r = o[b];
            return typeof r === 'string' || typeof r === 'number' ? r : a;
        }
    );
};
            
String.prototype.trim = function() {
  return this.replace(/^\s+|\s+$/g, "");
}

var DUMBLE_DEBUG = false;
if (location.hostname.toLowerCase() == 'localhost') {
    DUMBLE_DEBUG = true;
}

var firelog = function(str) {
    if(DUMBLE_DEBUG) {
       if (window.console && window.console.firebug) {
           console.log(str);
       }
    }
}

var getUrlParam = function(param) {
    var regex = '[?&]' + param + '=([^&#]*)';
    var results = (new RegExp(regex)).exec(window.location.search);
    if(results) return results[1];
    return '';
}
    
$.ajaxSetup({
    cache: true
});

OohembedProvider = function(url, caption, notes) {
    var url = url
    var caption = caption
    var notes = notes.trim()

    var ratings = /(\d{1,2}) ?\/ ?(\d{1,2})/i .exec(notes)
    var stars = ''

    if (ratings && (parseInt(ratings[1]) <= parseInt(ratings[2]))) {
        stars = ' <img src="images/' + Math.round(5*ratings[1]/ratings[2]) +
                    '_stars.png" height=16 class="stars" />'
        notes = notes.replace(ratings[0], '')
    } else {
        // the note starts with *, ends with * or is entirely *
        ratings = /^\*{2,5}\s|\s\*{2,5}$|^\*{2,5}$/i .exec(notes)
        if (ratings) {
            stars = ' <img src="images/' + ratings[0].trim().length 
                        + '_stars.png" height=16 class="stars" /> '
            notes = notes.replace(ratings[0], '').trim()
        }
    }

    if (stars) {
        firelog('stars are: ' + stars)
        notes = notes ? notes + '<br/>' + stars : stars
    }

    this.template = '<div class="link"><h3><a href="{url}" target="_blank">{caption}</a></h3>{notes}</div>'

    var elem = $(this.template.supplant({url: url, caption: caption, notes: notes}));
    
    this.video_template = '<div class="video">{embed}<span class="caption">{caption}</span>{notes}</div>'
    this.photo_template = '<div class="photo"><a href="{url}" target="_blank"><img src="{img_url}" alt="{caption}" title="{caption}" width="{width}" height="{height}" /></a><span class="caption">{caption}</span>{notes}</div>{html}'
    this.quote_template = '<div class="quote">&#8220;{text}&#8221;&nbsp;&nbsp;' + 
                '<span class="source"><a href="{url}" target="_blank">{source}</a></span></div><div style="margin: 1em;">{notes}</div>{html}'; 

    $.getJSON('http://'+location.host+'/oohembed/?url=' + escape(url) + '&format=json&maxwidth=480&callback=?', 
        function(data) {
            firelog('received data: ' + data.provider_name);
            if (data.type == 'video') {
                var snip = video_template.supplant({ 
                          embed: data.html,
                          caption: caption,
                          notes: notes?notes:''});
                firelog('replacing elem with: ' + snip);
                elem.html(snip);
            } else if (data.type == 'photo') {
                var credit = ''
                if (data.title && data.author_name) {
                    credit = '<em>'+data.title+' by '+data.author_name+'</em>'
                }
                notes = notes ? (notes + (credit ? '<br/>'+credit : '')) : credit
                var snip = photo_template.supplant({
                             url: url,
                             img_url: data.url,
                             width: data.width,
                             height: data.height,
                             caption: caption,
                             notes: notes,
                             html: data.html?'<div><blockquote>'+data.html+'</blockquote></div>':''});
                firelog('replacing elem with: ' + snip);
                elem.html(snip);
            } else if (data.type == 'link') {
                if (data.title) {
                    var source = data.author_name ? data.author_name : 'source'
                    var snip = quote_template.supplant({
                            url: url,
                            text: data.title,
                            html: data.html?'<div><blockquote>'+data.html+'</blockquote></div>':'',
                            source: source,
                            notes: notes?notes:''});
                    firelog('replacing elem with: ' + snip);
                    elem.html(snip);
                }
            }
        }
    );
    return elem;
}

GenericImageProvider = function(url, caption, notes) {
    this.re = /.*(jpeg|jpg|png|bmp|gif)$/i
    this.template = '<div class="photo"><img src="{url}" alt="{caption}" title="{caption}" /><span class="caption">{caption}</span>{notes}</div>'
    
    var matches = this.re.exec(url);
    if (!matches) {
        return false;
    }

    var elem = this.template.supplant({url: url, caption: caption, notes: notes});
    return $(elem);
}

var Providers = new Array(
            GenericImageProvider,
            OohembedProvider
        );

var Analytics = Analytics ? Analytics : {
    pageTracker: null,
    init: function(page) {
        if (DUMBLE_DEBUG) {return}
        $.getScript("http://www.google-analytics.com/ga.js", function(page) {
            Analytics.pageTracker = _gat._getTracker("UA-1736551-3");
            Analytics.pageTracker._initData();
            if(page) { Analytics.trackPage(page); }
        });
    },
    trackPage: function(page) {
        if (DUMBLE_DEBUG) {return}
        if (!this.pageTracker) {
            this.init(page);
        } else {
            this.pageTracker._trackPageview(page);
        }
    }
}

var Dumble = Dumble ? Dumble : {
    currentUser: 'antrix',
    currentTag: 'linker',
    currentData: [],
    currentURL: function() {
            return this.urlFor(this.currentUser, this.currentTag);
            },
    urlFor: function(user, tag) {
                return 'http://feeds.delicious.com/v2/json/' + user + ( tag ? '/' + tag : '');
            },
    friendsURLFor: function(user) {
                return 'http://feeds.delicious.com/v2/json/networkmembers/' + user;
            },
    tagsURLFor: function(user) {
                return 'http://feeds.delicious.com/v2/json/tags/' + user;
            },
    permalink: function(user, tag) {
                if(!user) {user = this.currentUser}
                if(!tag && user == this.currentUser)  {tag = this.currentTag}
                return location.protocol + '//' + location.host + location.pathname + '?u=' + user
                  + (tag ? '&t=' + tag : '');
            },
    writeCookie: function() {
                $.cookie('dumble010608', 'u='+this.currentUser+';t='+this.currentTag, {expires: 365});
                /* Google Analytics */
                Analytics.trackPage("/dumble/"+this.currentUser+"/"+this.currentTag); 
            },
    readCookie: function() {
                var prefs = $.cookie('dumble010608');
                if (!prefs) return;
                var data = prefs.split(';');
                for (i=0; i<data.length; i++) {
                    if (data[i].charAt(0)=='u') {
                        this.currentUser = data[i].substring(2, data[i].length);
                    }
                    if (data[i].charAt(0)=='t') {
                        this.currentTag = data[i].substring(2, data[i].length);
                    }
                }
            },
    updatePageFor: function(user, tag) {
                if (typeof _lastUser == 'undefined' || _lastUser != user) {
                    _lastUser = user;
                    this.currentUser = user;
                    this.updateFriends();
                    this.updateTags();
                }
                this.currentTag = tag ? tag : '';
                this.currentData = [];                
                $('#sourceUser').val(this.currentUser);
                $('#sourceTag').val(this.currentTag);
                $('#permalink').attr('href', this.permalink());
                $('#rss-feed-body').attr('href', 'http://feeds.delicious.com/v2/rss/'+this.currentUser+'/'+this.currentTag);
                $('#header h2').html('auto tumbling <em>'+this.currentUser+'&rsquo;s</em> delicious links'
                    + (tag ? ' tagged <em>' + tag + '</em>' : ''));
                this.writeCookie();
                this.updateHistory();
                this.updatePage();
            },

    insertItems: function() {
            var count = 0;
            while (this.currentData.length > 0) {
                var item = this.currentData.shift();
            
                $.each(Providers, function() {
                    var v = this(item.u, item.d, item.n ? item.n : '');
                    if (v) {
                        $('#dynposts').append(
                            $('<div class="post"></div>\n').hide().prepend(v));
                        count += 1;
                        return false;
                    }
                });
                if (count >= (DUMBLE_DEBUG ? 5 : 20)) {
                    break;
                }
            }
            if (this.currentData.length > 0) {
                $('#previous-next').fadeIn(1000);
            }
            $('.post').fadeIn(3000);
        },

    updateHistory: function() {
        var string = this.currentUser + (this.currentTag ? '/' + this.currentTag : '');
        var e = $('<li><a href="{l}" onClick="javascript:Dumble.updatePageFor(\'{n}\', \'{t}\');return false;">'.supplant({n: this.currentUser, t: this.currentTag, l: this.permalink()})
                     +string+ '</a></li>');
        $('#history ul').prepend(e);

        if ($('#history ul li').length == 2) {
            $('#history ul').slideDown('fast');
            $('#history-clear').show();
            $('#history').fadeIn('slow');
        }
    },

    updateTags: function() {
        $('#tags-list').fadeOut(1000);
        $('#tags h3').text("{name}'s top tags".supplant({name: this.currentUser}));
        
        $.getJSON(this.tagsURLFor(this.currentUser) + '?count=20&sort=count&callback=?', 
            function(tags) {
                var tgt = $('#tags-list');
                tgt.empty();
                if(tags) { /* Delicious returns tags as {tag1: count1, 'foo': 20, 'bar': 30} */
                    $.each(tags, function(tag, count) {
                        var e = $('<li><a href="' +Dumble.permalink(Dumble.currentUser, tag)+ '" onClick="javascript:Dumble.updatePageFor(\'{name}\', \'{tag}\');return false;">{tag}</a></li>'.supplant({name: Dumble.currentUser, tag: tag}));
                        tgt.append(e);
                    });
                }
                if(tgt.html() == '') {
                    tgt.text(Dumble.currentUser + " hasn't tagged any links!");
                }
                $('#tags-list').fadeIn(1000);
            });
    },
    updateFriends: function() {        
        $('#friends-list').fadeOut(1000);
        $('#friends h3').text("Explore {name}'s network".supplant({name: this.currentUser}));
        $('#networklink a').attr('href', 'http://delicious.com/network?add=' + this.currentUser)
                    .text("Add {name} to your delicious network".supplant({name: this.currentUser}));

        $.getJSON(this.friendsURLFor(this.currentUser) + '?callback=?', 
            function(names) {
                var tgt = $('#friends-list');
                tgt.empty();
                $.each(names, function() {
                    var name = this.user;
                    var e = $('<li><a href="' +Dumble.permalink(name)+ '" onClick="javascript:Dumble.updatePageFor(\'{name}\');return false;">{name}</a></li>'.supplant({name: name}));
                    tgt.append(e);
                });
                if (!tgt.text()) {
                    tgt.text(Dumble.currentUser + "'s network is empty! Is this an anti-social person? ;-)");
                }
                $('#friends-list').fadeIn(1000);
            });
    },
    updatePage:  function(URL) {
        $('body').css({ cursor: 'wait' });
        $('#previous-next').fadeOut(2000);
        
        if (this.currentData.length <= 0) {
            $('#dynposts').fadeOut(1000).empty().fadeIn(1);
            $.getJSON((URL ? URL : this.currentURL())+'?count=100&callback=?', 
                function(data) {
                    if (data.length > 0) {
                        Dumble.currentData = data;
                        Dumble.insertItems();
                    } else {
                        $('#dynposts').append(
                            $('<div class="post"> \
                            <h3 style="text-align: center;">\
                            No items found :-(</h3></div>\n').hide());
                         $('.post').fadeIn(3000);
                    }
                    $('#about').slideUp('fast');
                    $('body').css({ cursor: 'default' });
                });
        } else {
            this.insertItems();
            $('body').css({ cursor: 'default' });
        }
    } 
}  /* End Dumble namespace */

$(document).ready(function() {

    /* Some page setup first */
    $('#about').hide();
    $('#previous-next').hide();
    $('#history').hide();

    /* Is our location URL the base Dumble app url or does it have u=? & t=? */
    var isBaseURL = true;
    
    var m = getUrlParam('u');
    if (m) {
       Dumble.currentUser = m;
       Dumble.currentTag = '';
       isBaseURL = false;
    }
    m = getUrlParam('t');
    if (m) {
       Dumble.currentTag = m;
       isBaseURL = false;
    }
    m = unescape(getUrlParam('title'));
    if (m) {
       $('#header h1 a').text(m);
       window.document.title = m;
    }

    if (isBaseURL) {
        /* The initial page loaded via the root Dumble app url */
        Dumble.readCookie();
    } 

    $('#aboutHeader,#updateSource').hover(
        function() {
            $(this).css({ cursor: 'pointer' });
        }, 
        function() {
            $(this).css({ cursor: 'default' });
        }) 
    $('#aboutHeader').click(
        function() {
         $('#about').slideToggle('fast');
         Analytics.trackPage("/dumble/--about-header--/");
    });

    $('#sourceForm').submit(function() {
         Dumble.updatePageFor($('#sourceUser').val(), $('#sourceTag').val());
         $('#sourceUser').blur(); $('#sourceTag').blur();
         return false;
    });
    
    Dumble.updatePageFor(Dumble.currentUser, Dumble.currentTag);

});  /* End $(document).ready() block */
