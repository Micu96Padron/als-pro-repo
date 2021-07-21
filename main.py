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


class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Review(ndb.Model):
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class Game(ndb.Model):
    reviews = ndb.StructuredProperty(Review, repeated=True)
    name = ndb.StringProperty(required=True)
    genre = ndb.StringProperty(repeated=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        game_name = self.request.get('game_name', DEFAULT_GAME_NAME)

        if (game_name is DEFAULT_GAME_NAME) and (Game.query().get() is None):
            game = Game(name=DEFAULT_GAME_NAME, genre=DEFAULT_GAME_GENRES, reviews=[])
            game.put()

        game = Game.query(Game.name == game_name).get()
        reviews = game.reviews

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


class ReviewForum(webapp2.RequestHandler):

    def post(self):
        game_name = self.request.get('game_name', DEFAULT_GAME_NAME)

        if (game_name is DEFAULT_GAME_NAME) and (Game.query().get() is None):
            game = Game(name=DEFAULT_GAME_NAME, genre=DEFAULT_GAME_GENRES, reviews=[])
            game.put()

        review = Review()

        if users.get_current_user():
            review.author = Author(
                identity=users.get_current_user().user_id(),
                email=users.get_current_user().email())

        review.content = self.request.get('content')
        key = review.put()
        game = Game.query(Game.name == game_name).get()
        game.reviews.append(key)
        game.put()

        query_params = {'game_name': game_name}

        self.redirect('/?' + urllib.urlencode(query_params))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', ReviewForum),
], debug=True)
