from MainHandler import *
from multiprocessing import Process

def startServer(port):
    application = tornado.web.Application([
                            (r"/login/?", FacebookGraphLoginHandler),
                            (r"/select/?", SelectImageHandler),
                            (r"/render/?", RenderImageHandler),
                            #(r"/compose_image/", Compose),
                            
                            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./html"}),
                            
                            ],
                            template_path = './templates',
                            login_url = 'http://%s/login/' % settings.domain,
                            cookie_secret = settings.cookie_secret)
    
    try:
        application.listen(port)
        print "Startng server on port %s" % port
        tornado.ioloop.IOLoop.instance().start()
    except (SystemExit, KeyboardInterrupt):
        print "Aborting..."
        return 0
    except Exception, e:
        logging.exception(e)
    

if __name__ == '__main__':
    
    
    if len(sys.argv) > 1:
        readConfig(settings, 'imgr', sys.argv[1])
    
    workers = []
    for i in range(settings.num_workers):
        port = settings.base_port + i
        w = Process(target = startServer, args = [port,])
        w.daemon = True
        w.start()
        workers.append(w)

    try:
        for w in workers:
            w.join()
    except:
        pass
    
    