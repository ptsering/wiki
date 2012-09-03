import basehandler
import re
import utils
import string
import users
import logging

#VALIDATION REGULAR EXPRESSIONS

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
   return USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,30}$")
def valid_password(password):
   return PASSWORD_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
   return EMAIL_RE.match(email)

#####################################




class Signup(basehandler.BaseHandler):
    def write_signup_form(self,**kw):
        self.render("signup.html",**kw)
    
    def get(self):
        formEntries = {'username':"",
                       'err_username':"",
                       'err_password':"",
                       'err_verify':"",
                       'email':"",
                       'err_email':""
                       }
        self.write_signup_form(**formEntries)

    def post(self):
        formentries = {'username':"",
                       'err_username':"",
                       'err_password':"",
                       'err_verify':"",
                       'email':"",
                       'err_email':""
                       }
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        username_match = valid_username(username)
        password_match = valid_password(password)
        email_match = valid_email(email)
        verify_match = False

        if password_match:
            verify_match = (password == verify)

        if username_match and password_match and verify_match and (email == "" or email_match): ## Form is well
            if users.get_user_by_name(username):
                formentries['username'] = username
                formentries['email'] = email;
                formentries['err_username']="That user already exists."
                self.write_signup_form(**formentries)
            else:
               
                user = users.put_user(username,password,email)
                user_id_cookie = utils.make_secure_val(str(user.key().id()))
                self.response.headers.add_header('Set-Cookie',str('user_id=%s; Path=/' % user_id_cookie))
                self.redirect("/")
        else:
            formentries['username']=username
            formentries['email']=email
            if username_match == None:
                formentries['err_username']="This is not a valid username."
            if password_match == None:
                formentries['err_password']="That wasn't a valid password."
            elif verify_match == False:
                formentries['err_verify']="Your passwords didn't match."
            if email and email_match == None:
                formentries['err_email'] = "That's not a valid email."
            self.write_signup_form(**formentries)
        
class Login(basehandler.BaseHandler):
    def render_login(self,username="",error=""):
        self.render("signin.html",username=username,error=error)
        
    def get(self):
        self.render_login()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        if username and password:
            u = users.get_valid_user(username,password)
            if u:
                self.response.headers.add_header('Set-Cookie',str('user_id=%s; Path=/' % utils.make_secure_val(str(u.key().id()))))
                self.redirect("/")
        error = "Invalid login!!!"
        self.render_login(username,error)    

class Logout(basehandler.BaseHandler):
    def get(self,path="/"):
        self.response.headers.add_header('Set-Cookie',str('user_id=; Path=/'))
        logging.error("Path in logout" + path)
        self.redirect(path)
