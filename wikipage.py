import basehandler
import utils 
import users
import logging

from google.appengine.ext import db
from google.appengine.api import memcache

class Page(db.Model):
    path = db.StringProperty(required=True)
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_edited = db.DateTimeProperty(auto_now = True)


PAGE_KEY_PREFIX = "pg:"

def new_page(path,content=""):
    return Page(path=path,content=content)

def get_page_history(path):
    return Page.all().filter(' path = ', path).order('-created').run()

def get_page_by_id(pageId):
    return Page.get_by_id(long(pageId))

def get_page(path,create=False):
    key = PAGE_KEY_PREFIX + path
    page = memcache.get(key)
    if page:
        return page
    else:
        page = Page.all().filter(' path = ', path).order('-created').get()
        if page:
            memcache.set(key,page)
            return page
        elif create:
            page = new_page(path)
            ## Don't put in memcache yet, since it hasn't been put to DB
            return page
        else:
            return None

def set_page(page):
    key = PAGE_KEY_PREFIX + page.path
    page.put()
    memcache.set(key,page)   
    

class WikiPage(basehandler.BaseHandler):
    def show_wiki_page(self,page,username=None):
        if username:
            logged_in = True
        else:
            logged_in = False
        self.render("wikipage.html",logged_in=logged_in,wikipage=page,username=username)
    def get(self,path="/"):
        user_id_cv = self.request.cookies.get(str('user_id'))
        user_id = None
        if user_id_cv:
            user_id = utils.check_secure_val(user_id_cv)
            
        username = None
        if user_id: #user logged in
            user = users.get_user_by_id(user_id)
            if user:
                username = user.login_name

        ## Check if page referred by the path exists
        ver = self.request.get('v')
        if ver:
            page = get_page_by_id(ver)
        else:
            page = get_page(path)

        if page:
            self.show_wiki_page(page,username)
        else:
            self.redirect("/_edit"+path)


class EditPage(basehandler.BaseHandler):
    def show_edit_page(self,username,page):
        self.render("wikiedit.html",username=username,wikipage=page)

    def get(self,path="/"):
        user_id_cv = self.request.cookies.get(str('user_id'))
        user_id = None
        if user_id_cv:
            user_id = utils.check_secure_val(user_id_cv)
        username  = None
        if user_id:
            user = users.get_user_by_id(user_id)
            if user:
                username = user.login_name
            
        if username: #if valid user logged in
            ver = self.request.get('v')
            if ver:
                page = get_page_by_id(ver)
            else:
                page = get_page(path,True)
            self.show_edit_page(username,page)
                
        else:
            self.redirect("/login")

    def post(self,path="/"):
         content = self.request.get('content')
         wpage = new_page(path,content)
         set_page(wpage)
         self.redirect(path)
            
        
class HistoryPage(basehandler.BaseHandler):
    def show_history_page(self,username,pages,path):
        self.render("wikihistory.html",username=username,wikipages=pages,path=path)
        
    def get(self,path="/"):
        user_id_cv = self.request.cookies.get(str('user_id'))
        user_id = None
        if user_id_cv:
            user_id = utils.check_secure_val(user_id_cv)
        username  = None
        if user_id:
            user = users.get_user_by_id(user_id)
            if user:
                username = user.login_name
            
        if username: #if valid user logged in
            wpages = get_page_history(path)
            self.show_history_page(username,wpages,path)
                
        else:
            self.redirect("/login")
        
            
        
