from django.conf.urls.defaults import *

from coltrane.feeds import *

# Feed index page
urlpatterns = patterns('django.views.generic',
	(r'^list/$', 'simple.direct_to_template', {'template': 'coltrane/feed_list.html'}),
)

# Google sitemap and RSS feeds
feeds = {
	# Bundles
	'the-full-feed': FullFeed,
	'less-noise': LessNoise,
	# Singletons
	'posts': RecentPosts,
	'comments': RecentComments,
	'shouts': RecentShouts,
	'links': RecentLinks,
	'photos': RecentPhotos,
	'tracks': RecentTracks,
	'books': RecentBooks,
	'commits': RecentCommits,
	'tag': TagFeed,
	'category': CategoryFeed,
}

urlpatterns += patterns('',
	url(r'(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}, name='coltrane_feeds'),
)





