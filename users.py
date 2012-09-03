import hashlib
import random
import string
from google.appengine.ext import db
from google.appengine.api import memcache


def make_salt():
    return "".join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s,%s" % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(",")[1]
    if h == make_pw_hash(name, pw, salt):
        return True
    else:
        return False
    
####  USER MODEL #######

class User(db.Model):
    login_name = db.StringProperty(required=True)
    password = db.TextProperty(required=True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)

USER_KEY_PREFIX = "usr:"

def get_user_by_id(user_id):
    key = USER_KEY_PREFIX + user_id
    user = memcache.get(key)
    if user:
        return user
    else:
        user = User.get_by_id(int(user_id))
        memcache.set(key,user)
        return user

def set_user(user):
    user.put()
    key = USER_KEY_PREFIX + str(user.key().id())
    memcache.set(key,user)
    return user

def get_user_by_name(username):
    return User.all().filter('login_name = ', username).get()

def put_user(username, password, email):
    user = User(login_name=username, password=make_pw_hash(username,password),
                            email = email)
    return set_user(user)

def get_valid_user(username,password):
    u = get_user_by_name(username)
    if u and valid_pw(username,password,u.password):
        return u
