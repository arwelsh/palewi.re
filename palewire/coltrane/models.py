import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

from tagging.fields import TagField
from tagging.models import Tag

### MANAGERS	
from django.db import models
from django.db.models import signals
from django.dispatch import dispatcher


class Tumbler(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	pub_date = models.DateTimeField()
	
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	def get_rendered_html(self):
		template_name = 'coltrane/tumbler_item_%s.html' % (self.content_type.name)
		return render_to_string(template_name, { 'object': self.content_object })
		
	def __unicode__(self):
		return u'%s: %s' % (self.content_type.model_class().__name__, self.content_object)
		
		
class Slogan(models.Model):
	title = models.CharField(max_length=250, help_text='Maximum 250 characters.')

	class Meta:
		ordering = ['title']
		
	def __unicode__(self):
		return self.title


class Category(models.Model):
	title = models.CharField(max_length=250, help_text='Maximum 250 characters.')
	slug = models.SlugField(unique=True, help_text='Suggested value automatically generated from title. Must be unique.')
	description = models.TextField(null=True, blank=True)
	
	class Meta:
		ordering = ['title']
		verbose_name_plural = 'Categories'
		
	def __unicode__(self):
		return self.title
		
	def get_absolute_url(self):
		return u"/categories/%s/" % self.slug

	def live_post_set(self):
		from coltrane.models import Post
		return self.entry_set.filter(status=Post.LIVE_STATUS)


class LivePostManager(models.Manager):
	

	def get_query_set(self):
		return super(LivePostManager, self).get_query_set().filter(status=self.model.LIVE_STATUS)


class Post(models.Model):
	LIVE_STATUS = 1
	DRAFT_STATUS = 2
	HIDDEN_STATUS = 3
	STATUS_CHOICES = (
		(LIVE_STATUS, 'Live'),
		(DRAFT_STATUS, 'Draft'),
		(HIDDEN_STATUS, 'Hidden'),
	)
	
	wordpress_id = models.IntegerField(unique=True, null=True, blank=True, help_text='The junky old wp_posts id from before the migration', editable=False)
	title = models.CharField(max_length=250, help_text='Maximum 250 characters.')
	slug = models.SlugField(max_length=300, unique_for_date='pub_date', help_text='Suggested value automatically generated from title.')
	body = models.TextField()
	pub_date = models.DateTimeField(default=datetime.datetime.now)
	author = models.ForeignKey(User)
	enable_comments = models.BooleanField(default=True)
	status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE_STATUS, help_text="Only entries with 'Live' status will be publicly displayed.")
	categories = models.ManyToManyField(Category)
	tags = TagField(help_text='Separate tags with spaces.', blank=True)
	live = LivePostManager()
	objects = models.Manager()

	class Meta:
		ordering = ['-pub_date']
	
	def __unicode__(self):
		return self.title
				
	def get_absolute_url(self):
		return ('coltrane_post_detail', (), { 'year': self.pub_date.strftime("%Y"),
												'month': self.pub_date.strftime("%m"),
												'day': self.pub_date.strftime("%d"),
												'slug': self.slug })
												
	get_absolute_url = models.permalink(get_absolute_url)
	
	def get_tags(self):
		return Tag.objects.get_for_object(self)


class Tweet(models.Model):
	body = models.TextField(max_length=140)
	posted_by = models.ForeignKey(User)
	slug = models.SlugField(unique_for_date='pub_date', help_text='Suggested value automatically generated from title.')
	pub_date = models.DateTimeField(default=datetime.datetime.now)
	enable_comments = models.BooleanField(default=True)
	post_elsewhere = models.BooleanField('Post to Twitter', default=True, help_text='If checked, this link will be posted to both the blog and Twitter.')

	def __unicode__(self):
		return u'%s' % (self.body)

	def sendtwit(self):
		import twitter
		twitter_api=twitter.Api(username=settings.TWITTER_USER, password=settings.TWITTER_PASSWORD)
		twitter_api.PostUpdate(self.body)
		return

	def save(self):
		if not self.id and self.post_elsewhere:
			self.sendtwit()
		super(Tweet, self).save()

	def get_absolute_url(self):
		return ('coltrane_tweet_detail', (), { 'year': self.pub_date.strftime("%Y"),
												'month': self.pub_date.strftime("%m"),
												'day': self.pub_date.strftime("%d"),
												'slug': self.slug })
	get_absolute_url = models.permalink(get_absolute_url)


class Video(models.Model):
	title = models.CharField(max_length=250)
	url = models.URLField(unique=True)
	posted_by = models.ForeignKey(User)
	pub_date = models.DateTimeField(default=datetime.datetime.now)
	slug = models.SlugField(unique_for_date='pub_date', help_text='Suggested value automatically generated from title.')
	tags = TagField(help_text='Separate tags with spaces.')
	enable_comments = models.BooleanField(default=True)
	via_name = models.CharField('Via', max_length=250, blank=True, help_text='The name of the person whose site you spotted the link on. Optional.')
	via_url = models.URLField('Via URL', blank=True, help_text='The URL of the site where you spotted the link. Optional.')

	class Meta:
		ordering = ['-pub_date']

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return ('coltrane_video_detail', (), { 'year': self.pub_date.strftime("%Y"),
												'month': self.pub_date.strftime("%m"),
												'day': self.pub_date.strftime("%d"),
												'slug': self.slug })
	get_absolute_url = models.permalink(get_absolute_url)


class Photo(models.Model):
	title = models.CharField(max_length=250)
	url = models.URLField(unique=True)
	posted_by = models.ForeignKey(User)
	pub_date = models.DateTimeField(default=datetime.datetime.now)
	slug = models.SlugField(unique_for_date='pub_date', help_text='Suggested value automatically generated from title.')
	tags = TagField(help_text='Separate tags with spaces.')
	enable_comments = models.BooleanField(default=True)
	via_name = models.CharField('Via', max_length=250, blank=True, help_text='The name of the person whose site you spotted the link on. Optional.')
	via_url = models.URLField('Via URL', blank=True, help_text='The URL of the site where you spotted the link. Optional.')

	class Meta:
		ordering = ['-pub_date']

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return ('coltrane_photo_detail', (), { 'year': self.pub_date.strftime("%Y"),
												'month': self.pub_date.strftime("%m"),
												'day': self.pub_date.strftime("%d"),
												'slug': self.slug })
	get_absolute_url = models.permalink(get_absolute_url)


class SyncManager(models.Manager):

	def get_last_update(self, **kwargs):
		"""
		Return the last time a given model's items were updated. Returns the
		epoch if the items were never updated.
		"""
		qs = self
		if kwargs:
			qs = self.filter(**kwargs)
		try:
			return qs.order_by('-pub_date')[0].pub_date
		except IndexError:
			return datetime.datetime.fromtimestamp(0)


class Track(models.Model):
	"""A track you listened to. The model is based on last.fm."""

	artist_name = models.CharField(max_length=250)
	track_name = models.CharField(max_length=250)
	url = models.URLField(blank=True)
	pub_date = models.DateTimeField(default=datetime.datetime.now)
	track_mbid = models.CharField("MusicBrainz Track ID", max_length=36, blank=True)
	artist_mbid = models.CharField("MusicBrainz Artist ID", max_length=36, blank=True)
	sync = SyncManager()
	objects = models.Manager()

	class Meta:
		ordering = ("-pub_date",)

	def __unicode__(self):
		return u"%s - %s" % (self.artist_name, self.track_name)


class Link(models.Model):
	title = models.CharField(max_length=250)
	description = models.TextField(blank=True, null=True)
	url = models.URLField(unique=True)
	posted_by = models.ForeignKey(User)
	pub_date = models.DateTimeField(default=datetime.datetime.now)
	slug = models.SlugField(unique_for_date='pub_date', help_text='Suggested value automatically generated from title.')
	tags = TagField(help_text='Separate tags with spaces.')
	enable_comments = models.BooleanField(default=True)
	post_elsewhere = models.BooleanField('Post to del.icio.us', default=True, help_text='If checked, this link will be posted to both the blog and del.icio.us.')
	via_name = models.CharField('Via', max_length=250, blank=True, help_text='The name of the person whose site you spotted the link on. Optional.')
	via_url = models.URLField('Via URL', blank=True, help_text='The URL of the site where you spotted the link. Optional.')
	
	class Meta:
		ordering = ['-pub_date']

	def __unicode__(self):
		return self.title
	
	def save(self):
		if not self.id and self.post_elsewhere:
			import pydelicious
			from django.utils.encoding import smart_str
			pydelicious.add(settings.DELICIOUS_USER, settings.DELICIOUS_PASSWORD,
							smart_str(self.url), smart_str(self.title),
							smart_str(self.tags))
		super(Link, self).save()
	
	def get_absolute_url(self):
		return ('coltrane_link_detail', (), { 'year': self.pub_date.strftime("%Y"),
												'month': self.pub_date.strftime("%m"),
												'day': self.pub_date.strftime("%d"),
												'slug': self.slug })
	get_absolute_url = models.permalink(get_absolute_url)

from coltrane.models import Link, Tweet, Photo, Post, Track, Video

def create_tumbler_item(sender, instance, signal, *args, **kwargs):
	# Check to see if the object was just created for the first time
	if 'created' in kwargs:
		if kwargs['created']:
			create = True

			# Get the instance's content type
			ctype = ContentType.objects.get_for_model(instance)

			# Special cases for different date fields
			#if ctype.name == 'link':
			#	pub_date = instance.submit_date

			#elif ctype.name == 'post':
			#	pub_date = instance.time

			#else:
			pub_date = instance.pub_date

			# Special case for FreeComments to ensure the comment is public
			# This prevents comments in moderation or thought to be spam from appearing
			#if ctype.name == 'free comment':
			#	if instance.is_public == False:
			#		create = False

			if create:
				tumble = Tumbler.objects.get_or_create(content_type=ctype, object_id=instance.id, pub_date=pub_date)

# Send a signal on post_save for each of these models
for modelname in [Link, Photo, Post, Tweet, Track, Video]:		
	signals.post_save.connect(create_tumbler_item, sender=modelname)
