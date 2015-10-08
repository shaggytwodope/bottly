import logging
import logging.handlers
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

def log_setup():
    logger = logging.getLogger('myapp')
    hdlr = logging.FileHandler(base_dir + "/log/command.log")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)

    return logger

def log(logger, user, msg_type, destination, command, arg):
    arg = " ".join(arg)    
    logger.info(user + "| " + msg_type + "/" + destination + ": " + command + " " + arg)