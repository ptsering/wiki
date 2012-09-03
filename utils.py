import hmac
import seckey
import string

def make_secure_val(s):
    return "%s|%s" % (s, hmac.new(seckey.SECRET,s).hexdigest())

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val
