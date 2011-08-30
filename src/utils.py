import logging, ConfigParser, ast

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
    
