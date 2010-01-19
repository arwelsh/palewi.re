from django.conf.urls.defaults import *

from coltrane.models import Book

index_dict = {
	'queryset': Book.objects.all().order_by("-pub_date"),
	'paginate_by': 25,
}


urlpatterns = patterns('django.views.generic',

	# The root url
	url(r'^$', 'simple.redirect_to', { 'url': '/books/page/1/' }, name='coltrane_book_root'),

	# List
	url(r'^page/(?P<page>[0-9]+)/$', 'list_detail.object_list', index_dict, name='coltrane_book_list'),

)





