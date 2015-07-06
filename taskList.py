
import os
import urllib
import time
import uuid

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)



class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=False)


class Task(ndb.Model):
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    checked=ndb.BooleanProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        
        user = users.get_current_user()
        tasks=None
        if user:
            tasks_query=Task.query(Task.author.identity == user.user_id()).order(Task.date)
            tasks = tasks_query.fetch(10000)

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'tasks': tasks,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Tasks(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.

        task = Task()

        if users.get_current_user():
            task.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        task.content = self.request.get('content')
        task.checked=False
        task.put()

        self.redirect('/')
        
class DeleteTasks(webapp2.RequestHandler):
    def post(self):
        taskId = int(self.request.get("taskId"))
        task=Task.get_by_id(taskId)
        ndb.Key(Task, taskId).delete()
        self.redirect('/')
class UpdateTasks(webapp2.RequestHandler):
    def post(self):
        taskId = int(self.request.get("taskId"))
        task=Task.get_by_id(taskId)
        check=self.request.get("checked")
        if check=="true":
            task.checked=True;
        else:
            task.checked=False;
            
        task.put()
        self.redirect('/')
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/addTask', Tasks),
    ('/deleteTask', DeleteTasks),
    ('/updateTask', UpdateTasks),
], debug=True)
