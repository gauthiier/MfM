import sys, logging

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(format='%(asctime)s -- %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

def info(msg):
	logging.info(msg)

def err(msg):
	logging.error(msg)

def warn(msg):
	logging.warning(msg)

def crit(msg):
	logging.critical(msg)
