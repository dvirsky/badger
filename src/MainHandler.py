'''
Created on Aug 2, 2011

@author: dvirsky
'''
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.httpclient
import logging
import settings
import Image
import ConfigParser
import ast
import sys
import json
import BadgePaster
import mimetypes
from tornado.httputil import url_concat

class FacebookGraphLoginHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
  
  #_OAUTH_AUTHORIZE_URL = 'https://www.facebook.com/dialog/oauth?'
  
  def __init__(self, application, request, **kwargs):
      
      tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
      
      self._url_ = 'http://%s/login/' % settings.domain
      
  @tornado.web.asynchronous
  def get(self):
      self.post()
  

  @tornado.web.asynchronous
  def post(self):
      
      if self.get_argument("code", False):
          #print "Got code: %s url: %s" % (self.get_argument("code", False), self._url_)
          self.get_authenticated_user(
            redirect_uri=settings.canvas_page,
            client_id=settings.fb_appid,
            client_secret=settings.fb_secret,
            code=self.get_argument("code"),
            callback=self.async_callback(
              self.onAuth))
          return
      
#      self.authorize_redirect(redirect_uri=self._url_,
#                              client_id=settings.fb_appid,
#                              extra_params={"scope": "publish_stream,offline_access"})

      args = {
          "redirect_uri": settings.canvas_page,

          "client_id": settings.fb_appid,
          "scope": "publish_stream"
        }
        
      print url_concat(self._OAUTH_AUTHORIZE_URL, args)
      self.write('<script> top.location.href = "' + url_concat(self._OAUTH_AUTHORIZE_URL, args) + '";</script>');
      self.finish()
       

       
  def onAuth(self, user):
    
    
    if user :
        print "Setting user: %s" % user
        self.set_secure_cookie("user", json.dumps(user), expires_days = 1)
        self.redirect('/select/')
        return
        #self.write('<img src="http://graph.facebook.com/%s/picture?type=large"/>' % user['id'])
    else:
        self.write("Sorry, we couldnot authenticate you...")
        
    self.finish()
    
    
class SelectImageHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
    
    @tornado.web.asynchronous
    def get(self):
      self.post()
      
    @tornado.web.asynchronous
    def post(self):
        
        print self.get_arguments('b')
        user = self.get_secure_cookie('user')
        print "User: %s" % user
        if user is None or user == 'null':
            print "Redirecting..."
            self.redirect('/login/')
            return
        try:
            user = json.loads(user)
        except Exception, e:
            logging.error("Could not parse user json: %s" % e)
            self.redirect('/login/')
            return
        
        print user  
   
        self.render('select.html.tpl', user = user,  appId = settings.fb_appid)
        #self.write("Haello %s" % user['name'])
        
        #self.finish()


class RenderImageHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
    
    badges = {
              '1': './html/bet_badge.png',
              '2': './html/just_badge.png'
              }
      
    def encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self.get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
    
    def get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
   
     
    @tornado.web.asynchronous
    def get(self):
        
        print self.get_arguments('b')
        user = self.get_secure_cookie('user')
        if not user:
            self.redirect('/login/')
            return
        try:
            user = json.loads(user)
        except Exception, e:
            logging.error("Could not parse user json: %s" % e)
            self.redirect('/login/')
            return
        
        print user
        if not self.get_argument('b', None) in self.badges:
            self.redirect('/select/')
            return
        
        self.badgeId = self.get_argument('b', '1')
        
        if user:
            userImg = 'http://graph.facebook.com/%s/picture?type=large' % user['id']
            
            badger = BadgePaster.BadgePaster(userImg, self.badges[self.badgeId])
            img = None
            try:
                badger.loadImage()
                img = badger.splatBadge()
                
                
                
                content_type, body = self.encode_multipart_formdata([('message', 'support the revolution - change your profile pic!')],
                                                       [('source', img, open('./html/%s'% img).read())])
                
                
                self.img = img
                self.user = user
                request = tornado.httpclient.HTTPRequest('https://graph.facebook.com/me/photos?access_token=%s' % user['access_token'], 
                                                         method = 'POST', 
                                                         body = body,
                                                         request_timeout = 60,
                                                         follow_redirects = True,
                                                         headers = { "Content-Type":content_type,
                                                                    'Content-Length': str(len(body))}
                                                         )
                
                client = tornado.httpclient.AsyncHTTPClient()
                client.fetch(request, callback = self.async_callback(self.onImageUpload))
                logging.info("Uploading...")
                return 
                                
                
#                self.facebook_request('/me/photos', 
#                                      access_token = user['access_token'], 
#                                      post_args= {'message': 'supporting the revolution badge',
#                                                  'source': 'http://%s/static/%s' % (settings.domain, img)},
#                                      callback= self.async_callback(self.onImageUpload))
#                
#                return
                
            except Exception, e:
                logging.exception("Could not render images... try again %s", e)
                self.finish()
                return
            
            
            
        else:
            self.write("Something went wrong")
                
        #self.write("Haello %s" % user['name'])
        
        self.finish()
        
    def onImageUpload(self, response): 
        
        if response and response.code == 200:
            try:
                obj = json.loads(response.body)
                self.render('render.html.tpl', imageURL = self.img, user = self.user, 
                            appId = settings.fb_appid, 
                            imageFbURL = 'http://www.facebook.com/photo.php?fbid=%s&makeprofile=1' % obj['id'])
                return
            except Exception, e:
                logging.exception(e)
                
        
        self.write("Could not upload photo...")
        self.finish()

def readConfig(settings, section, fileName):
    """
    Read the local config file and replace any setting Settings with the one from this file
    """
    #Create case sensitive config parser
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    try:
        #read the config file
        config.read(fileName)

        #add whatever we find there to Settings
        for (key, value) in config.items(section):
            logging.info("Reading %s => %s" ,key, value)
            try:
                setattr(settings, key, parseValue(value))
            except Exception, e:
                logging.error("could not set value %s. probably type mismatch...: %s" ,key, e)

    except Exception, e:
        logging.error("Could not read config file %s... %s" ,fileName, e)
        return False

    return True

def parseValue(value):
    try:
        return ast.literal_eval(value)
    except:
        return ast.literal_eval('"%s"' % value)
    
    
