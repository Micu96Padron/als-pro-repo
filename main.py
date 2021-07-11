import os
import time

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=["jinja2.ext.autoescape"],
    autoescape=True)

class User(ndb.Model):
    id_user = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            self.redirect("/list")
        else:
            labels = {
                "user_login": users.create_login_url("/")
            }

            template = JINJA_ENVIRONMENT.get_template("index.html")
            self.response.write(template.render(labels))

class ListHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user is None:
            self.redirect("/")
        else:
            user_id = user.user_id()
            name_info = user.nickname()
            stored_user = User.query(User.id_user == user_id)
            if stored_user.count() == 0:
                img = User(id_user = user_id, name = name_info)
                img.put()
                time.sleep(1)

            people = User.query().order(User.name)
            labels = {
                "people": people,
                "user_logout": users.create_logout_url("/")
            }

            template = JINJA_ENVIRONMENT.get_template("answer.html")
            self.response.write(template.render(labels))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/list', ListHandler)
], debug=True)