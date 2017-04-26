import sys, logging

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(filename='rx.log', format='%(asctime)s -- RX/%(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
