import datetime
import sys

from google.appengine.ext import db

FETCH_THEM_ALL = sys.maxint - 1

class Article(db.Model):

    title = db.StringProperty(required=True)
    body = db.TextProperty()
    published_when = db.DateTimeProperty(auto_now_add=True)
    tags = db.ListProperty(db.Category)
    id = db.IntegerProperty(required=True)
    draft = db.BooleanProperty(required=True, default=False)

    def __init__(self, *args, **kw):
        if not ('id' in kw):
            id = Article.max_id() + 1
            kw['id'] = id
        db.Model.__init__(self, *args, **kw)

    @classmethod
    def max_id(cls):
        q = db.Query(Article)
        q.order('-id')
        articles = q.fetch(1)
        if not articles:
            id = 0
        else:
            id = articles[0].id

        return id

    @classmethod
    def get_all(cls):
        q = db.Query(Article)
        q.order('-published_when')
        return q.fetch(FETCH_THEM_ALL)

    @classmethod
    def get(cls, id):
        q = db.Query(Article)
        q.filter('id = ', id)
        articles = q.fetch(1)
        return articles[0] if articles else None

    @classmethod
    def published_query(cls):
        q = db.Query(Article)
        q.filter('draft = ', False)
        return q

    @classmethod
    def published(cls):
        return Article.published_query()\
                      .order('-published_when')\
                      .fetch(FETCH_THEM_ALL)

    @classmethod
    def get_all_tags(cls):
        """
        Return all tags, as TagCount objects, optionally sorted by frequency
        (highest to lowest).
        """
        tag_counts = {}
        for article in Article.published():
            for tag in article.tags:
                try:
                    tag_counts[tag] += 1
                except KeyError:
                    tag_counts[tag] = 1

        return tag_counts

    @classmethod
    def latest(cls):
        # Surely there's an easier way...
        article = Article.published()
        return article[0] if articles else []

    @classmethod
    def get_all_datetimes(cls):
        dates = {}
        for article in Article.published():
            date = datetime.datetime(article.published_when.year,
                                     article.published_when.month,
                                     article.published_when.day)
            try:
                dates[date] += 1
            except KeyError:
                dates[date] = 1

        return dates

    @classmethod
    def all_for_month(cls, year, month):
        start_date = datetime.date(year, month, 1)
        if start_date.month == 12:
            next_year = start_date.year + 1
            next_month = 1
        else:
            next_year = start_date.year
            next_month = start_date.month + 1

        end_date = datetime.date(next_year, next_month, 1)
        return Article.published_query()\
                       .filter('published_when >=', start_date)\
                       .filter('published_when <', end_date)\
                       .order('-published_when')\
                       .fetch(FETCH_THEM_ALL)

    @classmethod
    def all_for_tag(cls, tag):
        return Article.published_query()\
                      .filter('tags = ', tag)\
                      .order('-published_when')\
                      .fetch(FETCH_THEM_ALL)

    @classmethod
    def convert_string_tags(cls, tags):
        new_tags = []
        for t in tags:
            if type(t) == db.Category:
                new_tags.append(t)
            else:
                new_tags.append(db.Category(unicode(t)))
        return new_tags

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return '[%s] %s' %\
               (self.published_when.strftime('%Y/%m/%d %H:%M'), self.title)

    def save(self):
        previous_version = Article.get(self.id)
        try:
            draft = previous_version.draft
        except AttributeError:
            draft = False

        if draft and (not self.draft):
            # Going from draft to published. Update the timestamp.
            self.published_when = datetime.datetime.now()

        self.put()

    def put(self):
        import time
        if not self.id:
            self.id = str(int(time.time()))
        db.Model.put(self)
