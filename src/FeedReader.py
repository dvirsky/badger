## Generic class to read the feed of a facebook entity (event, user, group, etc):

import datetime, time, logging, json, functools
import tornado.httpclient 
import tornado.ioloop
import redis

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
        try:
            
            self.time = time.strptime(str(postTime), format)
            self.timeString = postTime
            
        except Exception, e:
            logging.exception(e)
            self.time = datetime.datetime.now()
            
        
        self.picture = extra.get('picture', None)
        self.link = extra.get('link', None)
        if self.itype == 'status':
            self.text = extra.get('message', '')
        elif self.itype == 'link':
            self.text = extra.get('message', '')
            self.title = extra.get('name', '')
        elif self.itype == 'photo':
            self.text = extra.get('message', '')
        else:
            raise ValueError("unrecoginzed type: %s" % self.itype)
        
        #if not self.title and not self.text:
        #    raise ValueError("Invalid item... %s" % extra)
        
    def __repr__(self):
        
        return "%s(%s,%s,%s)" % (self.itype, self.fbId, self.title, self.text)
    
    def key(self):
        
        return '%s:%s' % (self.itype, self.fbId)
    
    def save(self, redisConn):
        
        redisConn.hmset(self.key(), dict((x, getattr(self, x, None)) for x in ('fbId', 'itype', 'userId', 'userName',
                                                                    'title', 'text', 'link', 'picture', 'timeString',
                                                                    'feedId', 'feedName')))
        
        redisConn.zadd('messageIndex', self.key(), time.mktime(self.time))
        
       
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
            
        #tornado.ioloop.IOLoop.instance().add_timeout(30, self.onTimeout)
        
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
        if self.collectedItems:
            self.collectedItems.sort(lambda x,y: cmp(y.time, x.time))
        
        r = redis.Redis()
        p = r.pipeline()
        for item in self.collectedItems:
            item.save(p)
            #print item.title or item.text or item.link
            #print "\n--------------------------------\n\n"
            
        p.execute()
            
    
    
def getFeeds():
    
    r = FeedCollector([169350816471243, 156008021140159], '')
    
    #/feed?access_token=
if __name__ == '__main__':
    
    logging.basicConfig(level = 0)
    tornado.ioloop.IOLoop.instance().add_callback(getFeeds)
    
    tornado.ioloop.IOLoop.instance().start()