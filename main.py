import os
import urllib

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_REVIEW_TITLE = 'default_review'

def review_key(review_title=DEFAULT_REVIEW_TITLE):
    return ndb.Key('Review', review_title)

class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

class Review(ndb.Model):
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        review_title = self.request.get('review_title',
                                       DEFAULT_REVIEW_TITLE)
        review_query = Review.query(
            ancestor=review_key(review_title)).order(-Review.date)
        review = review_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'review': review,
            'review_title': urllib.quote_plus(review_title),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Reviews(webapp2.RequestHandler):

    def post(self):
        review_title = self.request.get('review_title',
                                        DEFAULT_REVIEW_TITLE)
        review = Review(parent=review_key(review_title))

        if users.get_current_user():
            review.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        review.content = self.request.get('content')
        review.put()

        query_params = {'review_title': review_title}
        self.redirect('/?' + urllib.urlencode(query_params))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Reviews),
], debug=True)
