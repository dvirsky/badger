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
        
        
        ufp = urllib2.urlopen(self.imageURL)
        ofp = open('/tmp/%s' % hash(self.imageURL), 'w+')
        while True:
            data = ufp.read(4096)
            if not data:
                break
            ofp.write(data)
            
        ufp.close()
        ofp.close()
        self.image = self.loadWebImage(self.imageURL)
        if self.badgeURL:
            self.badge = self.loadWebImage(self.badgeURL)
        
        print self.image, self.badge.size
        
    def splatBadge(self):
        
        
        badgeDesiredWidth = min(self.image.size[0], self.badge.size[0])
        badgeDesiredHeight = int(self.badge.size[1] * (float(badgeDesiredWidth) / float(self.badge.size[0])))
        print badgeDesiredWidth, badgeDesiredHeight
        resizedBadge = self.badge.resize((badgeDesiredWidth, badgeDesiredHeight), Image.ANTIALIAS)
        print resizedBadge
        
        self.image.paste(resizedBadge, (0, self.image.size[1] - resizedBadge.size[1], 
                                        self.image.size[0], self.image.size[1]), resizedBadge)
        self.image.save('./html/%s.jpg' % hash(self.imageURL))
        self.image.show()
        #x,y = 
        #_badge = self.badge.resize(min(self.badge))
        
    def loadWebImage(self, url):
       
        try:
            ufp = urllib2.urlopen(url)
            ofp = open('/tmp/%s' % hash(url), 'w+')
            while True:
                data = ufp.read(4096)
                if not data:
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