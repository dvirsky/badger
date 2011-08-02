'''
Created on Aug 2, 2011

@author: dvirsky
'''
import tornado.ioloop
import tornado.web
import tornado.auth
import logging
import settings
import Image
import ConfigParser
import ast
import sys


class FacebookGraphLoginHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
  
  @tornado.web.asynchronous
  def get(self):
      if self.get_argument("code", False):
          self.get_authenticated_user(
            redirect_uri='http://dviro.zapto.org/auth/facebookgraph/',
            client_id=settings.fb_appid,
            client_secret=settings.fb_secret,
            code=self.get_argument("code"),
            callback=self.async_callback(
              self._on_login))
          return
      
      self.authorize_redirect(redirect_uri='http://dviro.zapto.org/auth/facebookgraph/',
                              client_id=settings.fb_appid,
                              extra_params={"scope": "publish_stream,offline_access"})

  def _on_login(self, user):
    if user:
        
        
    
        #self.set_cookie("user", '%s' % user, settings.domain,'/', expires_days = 1)
        self.write('<img src="http://graph.facebook.com/%s/picture?type=large"/>' % user['id'])
        
    self.finish()
    
    
class ComposeImageHandler(tornado.web.RequestHandler,
                  tornado.auth.FacebookGraphMixin):
    
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        self.get_authenticated_user(self.onAuth)
        
        self.facebook_request(
            "/me/feed",
            post_args={"message": "I am posting from my Tornado application!"},
            access_token=self.current_user["access_token"],
            callback=self.async_callback(self._on_post))

   
    def onAuth(self, user):
        logging.error(user)
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
    
    
if __name__ == '__main__':
    
    
    if len(sys.argv) > 1:
        readConfig(settings, 'imgr', sys.argv[1])
    
    application = tornado.web.Application([
                            (r"/auth/facebookgraph/", FacebookGraphLoginHandler),
                            #(r"/compose_image/", Compose),
                            
                            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./html"}),
                            
                            ])
    
    application.listen(9876)
    tornado.ioloop.IOLoop.instance().start()