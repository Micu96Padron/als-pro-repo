import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def get_default_name():
    toret = ''

    return toret


DEFAULT_GAME_NAME = get_default_name()


def guestbook_key(game_name=DEFAULT_GAME_NAME):
    return ndb.Key('Game', game_name)


class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

class Game(ndb.Model):
    name = ndb.StringProperty(required=True)
    genre = ndb.StringProperty(repeated=True)

class Review(ndb.Model):
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('game_name',
                                          DEFAULT_GAME_NAME)
        greetings_query = Review.query(
            ancestor=guestbook_key(guestbook_name)).order(-Review.date)
        greetings = greetings_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'game_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class ReviewForum(webapp2.RequestHandler):

    def post(self):
        guestbook_name = self.request.get('game_name',
                                          DEFAULT_GAME_NAME)
        greeting = Review(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'game_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', ReviewForum),
], debug=True)