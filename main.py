
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


DEFAULT_GAME_NAME = "TLOZ: Breath of the Wild"
DEFAULT_GAME_GENRES = ['Action', 'Adventure']


def game_key(game_name=DEFAULT_GAME_NAME):
    return ndb.Key('Game', game_name)


class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Review(ndb.Model):
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class Game(ndb.Model):
    name = ndb.StringProperty()
    genre = ndb.StringProperty(repeated=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        game_name = self.request.get('game_name',
                                     DEFAULT_GAME_NAME)

        review_query = Review.query(ancestor=game_key(game_name)).order(-Review.date)
        reviews = review_query.fetch(10)

        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'reviews': reviews,
            'game_name': game_name,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class GameReview(webapp2.RequestHandler):

    def post(self):
        game_name = self.request.get('game_name',
                                     DEFAULT_GAME_NAME)

        review = Review(parent=game_key(game_name))

        if users.get_current_user():
            review.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        review.content = self.request.get('content')
        review.put()

        query_params = {'game_name': game_name}
        self.redirect('/?' + urllib.urlencode(query_params))


class AddGame(webapp2.RequestHandler):

    def post(self):
        pass






app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', GameReview),
    ('/addgame', AddGame)
], debug=True)

