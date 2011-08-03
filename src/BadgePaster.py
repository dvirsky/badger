'''
Created on Aug 3, 2011

@author: dvirsky
'''
import Image
import urllib2
import urllib
import logging
class BadgePaster(object):
    '''
    classdocs
    '''


    def __init__(self, imageURL, badgeURL):
        '''
        Constructor
        '''
        self.imageURL = imageURL
        self.badgeURL = badgeURL
        self.image = None
        self.badge = None
        Image.init()
        
    def loadImage(self):
        
        
        
        self.image = self.loadWebImage(self.imageURL)
        if self.badgeURL:
            self.badge = self.loadLocalImage(self.badgeURL)
        
        print self.image, self.badge.size
        
    def splatBadge(self):
        
        
        badgeDesiredWidth = min(self.image.size[0], self.badge.size[0])
        badgeDesiredHeight = int(self.badge.size[1] * (float(badgeDesiredWidth) / float(self.badge.size[0])))
        print badgeDesiredWidth, badgeDesiredHeight
        resizedBadge = self.badge.resize((badgeDesiredWidth, badgeDesiredHeight), Image.ANTIALIAS)
        print resizedBadge
        
        self.image.paste(resizedBadge, (0, self.image.size[1] - resizedBadge.size[1], 
                                        self.image.size[0], self.image.size[1]), resizedBadge)
        
        imgName = '%s.jpg' % hash(self.imageURL)
        self.image.save('./html/%s' % imgName, "JPEG", quality = 95)
        return imgName
        
        #x,y = 
        #_badge = self.badge.resize(min(self.badge))
        
    def loadLocalImage(self, path):
        try:
            print path
            fp = open(path)
            
            img = Image.open(path)
            img.load()
            return img
            
        except Exception, e:
            logging.exception(e)
            return None
            
        
    
    
    def loadWebImage(self, url):
       
        try:
            print url
            ufp = urllib2.urlopen(url)
            ofp = open('/tmp/%s' % hash(url), 'w+')
            while True:
                data = ufp.read(4096)
                print len(data)
                if not data:
                    print "finished..."
                    break
                ofp.write(data)
                
            ufp.close()
            ofp.close()
            img = Image.open('/tmp/%s' % hash(url))
            img.load()
            return img
            
        except Exception, e:
            logging.exception(e)
            return None
            
        return img
        
        
if __name__ == '__main__':
    
    badger = BadgePaster('http://profile.ak.fbcdn.net/hprofile-ak-snc4/274451_751778017_3375252_n.jpg', 'http://dviro.zapto.org/static/just_badge.png')
    
    badger.loadImage()
    badger.splatBadge()