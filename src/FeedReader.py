## Generic class to read the feed of a facebook entity (event, user, group, etc):

import datetime, time, logging, json, functools
import tornado.httpclient 
import tornado.ioloop
import tornado.web

import redis
import codecs

from utils import parseValue, readConfig
import settings
from multiprocessing import Process

class FeedMessage(object):
    
    def __init__(self, feedName, feedId, fbId, postTime, itype, userId, userName, extra):
        
        self.feedName = feedName
        self.feedId = feedId
        self.fbId = fbId
        self.itype = itype
        self.userId = userId
        self.userName =userName
        self.title = ''
        self.text = ''
        self.link = ''
        self.picture = None
        #time format: 2011-08-14T11:51:41+0000
        format = '%Y-%m-%dT%H:%M:%S+0000'
        if postTime:
            try:
                
                self.time = time.strptime(str(postTime), format)
                self.timeString = postTime
                
            except Exception, e:
                logging.exception(e)
                self.time = datetime.datetime.now()
                
        extra = extra or {}
        self.picture = extra.get('picture', None)
        self.link = extra.get('link', None)
        if self.itype == 'status':
            self.text = extra.get('message', '')
        elif self.itype == 'link':
            self.text = extra.get('message', '')
            self.title = extra.get('name', '')
        elif self.itype == 'photo':
            self.text = extra.get('message', '')
        elif self.itype == None:
            pass
        else:
            raise ValueError("unrecoginzed type: %s" % self.itype)
        
        #if not self.title and not self.text:
        #    raise ValueError("Invalid item... %s" % extra)
        
    def __repr__(self):
        
        return "%s(%s,%s,%s)" % (self.itype, self.fbId, self.title, self.text)
    
    def key(self):
        
        return '%s:%s' % (self.itype, self.fbId)
    
    def _valuesDict(self):
        
        return dict((x, getattr(self, x, '')) for x in ('fbId', 'itype', 'userId', 'userName',
                                                                    'title', 'text', 'link', 'picture', 'timeString',
                                                                    'feedId', 'feedName'))
        
    def save(self, redisConn):
        
        
        
        redisConn.hmset(self.key(), self._valuesDict())
        
        redisConn.zadd('messageIndex', self.key(), time.mktime(self.time))
        
    def setParams(self, dict_):
        
        self.__dict__.update(dict_)
        
    @staticmethod
    def load(key, redisConn):
        
        try:
            d = redisConn.hgetall(key)
            if d:
                i = FeedMessage(None, None, None, None, None, None, None, None)
                i.setParams(d)
                return i
            
        except Exception, e:
            logging.exception("Could not load message: %s", e)
            
        return None
                
        
        
class AggregatedFeed(object):
    
    
    def __init__(self):
        
        self._redis = redis.Redis()
        self._items = []
        self.first = 0
        self.num = 0
        self.limit = 0
        self.max = 0
        
    def loadItems(self, first = 0, limit = 20):
        
        keys = self._redis.zrange('messageIndex', first, limit - 1, True)
        
        self.items = []
        self.first = first
        self.limit = limit
        self.max = 0
        for k in keys:
            itm = FeedMessage.load(k, self._redis)
            if itm:
                self.items.append(itm)
                
        self.num = len(self.items)
        self.max = self._redis.zcard('messageIndex')
        
    
    def toJSON(self):
        
        d = {'first': self.first, 'limit': self.limit, 'num': self.num, 'max': self.max, 'items': [x._valuesDict() for x in self.items] }
        return json.dumps(d, encoding = 'utf-8')
    
       
class FBFeedReader(object):
    
    def __init__(self, accessToken):
        self.accessToken = accessToken
        
    def getItems(self, feedFbId, callBack):
        
        
        request = tornado.httpclient.HTTPRequest('https://graph.facebook.com/%s/feed?access_token=%s' % 
                                                    (feedFbId, self.accessToken), 
                                                         method = 'GET', 
                                                         request_timeout = 10,
                                                         follow_redirects = True,
                                                         
                                                )
                
        client = tornado.httpclient.AsyncHTTPClient()
        self.callBack = callBack
        self.fbId = feedFbId
        print "Sending request..."
        client.fetch(request, callback = self.onItems)
        print "sent!"
        
        
    def onItems(self, response):
        
        logging.debug("Returned! response: %s", response)
        collectedItems = []
        if response and response.code == 200:
            try:
                obj = json.loads(response.body)
                items = obj['data']
                
                for i in items:
                    
                    if not i.has_key('to'):
                        print json.dumps(i, indent = 4)
                    try:
                        item = FeedMessage(i['to']['data'][0]['name'] if i.has_key('to') else '', 
                                           i['to']['data'][0]['id'] if i.has_key('to') else self.fbId,
                                           i['id'], i['updated_time'], i['type'], i['from']['id'],i['from']['name'], i)
                        
                        collectedItems.append(item)
                    except Exception, e:
                        logging.warn(e)
                    
                
                
            except Exception, e:
                logging.exception(e)
        else:
            logging.error("Could not perform request: %s" % response)
            
        if self.callBack:
            self.callBack(collectedItems)
        

class FeedCollector(object):
    
    def __init__(self, feedIds, accessToken, collectTimeout = 30000):
        
        self.collectedItems = []
        self.feedIds = feedIds
        self.finishedFeeds = 0
        self.isWorking = True
        
        for f in feedIds:
            
            r = FBFeedReader(accessToken)
            r.getItems(f, self.onFeedFinish)
            
        
        self._timeout = tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 30, self.onTimeout)
        
    def onFeedFinish(self, items):
        
        print "One feed finished! %d items" % (len(items))
         
        self.collectedItems += items
        self.finishedFeeds += 1
        print "Finished: %s/%s" % (self.finishedFeeds, len(self.feedIds))
        
        if  len(self.feedIds) == self.finishedFeeds :
            print "Done!"
            
            tornado.ioloop.IOLoop.instance().add_callback(self.onAllFinished)
            
    def onTimeout(self):
        
        if self.isWorking:
            print "Timeout! got %s/%s feeds only!"
            tornado.ioloop.IOLoop.instance().add_callback(self.onAllFinished)
            
        
    def onAllFinished(self):
        
        self.isWorking = False
        if self._timeout:
            logging.debug("Removing timeout %s" % self._timeout)
            tornado.ioloop.IOLoop.instance().remove_timeout(self._timeout)
        if self.collectedItems:
            self.collectedItems.sort(lambda x,y: cmp(y.time, x.time))
        
        try:
            r = redis.Redis()
            p = r.pipeline()
            for item in self.collectedItems:
                item.save(p)
                #print item.title or item.text or item.link
                #print "\n--------------------------------\n\n"
            
            p.execute()
        except Exception, e:
            logging.exception("Could not save feed: %s", e)

            
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + settings.refresh_interval, getFeeds)
            
    
class RootHandler(tornado.web.RequestHandler):
    
    def get(self):
        feed = AggregatedFeed()
        feed.loadItems(int(self.get_argument('f', 0) or 0), int(self.get_argument('l', 20) or 0))
        self.write(feed.toJSON())
        
    
def getFeeds():
    print("Get feeds called!")
    
    r = FeedCollector(settings.feed_ids, settings.access_token)
    
    #/feed?access_token=
    
def startServer(port):
    logging.basicConfig(level = 0)#logging.info)
    tornado.ioloop.IOLoop.instance().add_callback(getFeeds)
        
    application = tornado.web.Application([
                        (r"/", RootHandler)])
    application.listen(port)
        
    
    tornado.ioloop.IOLoop.instance().start()
    
    
import sys
if __name__ == '__main__':
    
    
    if len(sys.argv) > 1:
        readConfig(settings, 'fbfeedr', sys.argv[1])
    
    workers = []
    for i in range(settings.num_workers):
        port = settings.base_port + 100 + i
        print port
        w = Process(target = startServer, args = [port,])
        w.daemon = True
        w.start()
        workers.append(w)

    try:
        for w in workers:
            w.join()
    except:
        pass
    
    
    
    