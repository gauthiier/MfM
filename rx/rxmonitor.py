import os, threading, time, json, logging, signal
from optparse import OptionParser
from lib.monitor import Monitor
import lib.log as log
import rx

class RXMonitor(Monitor):

	def run(self, config, status_cb, ends_cb):
		rx.run(options, status_cb, ends_cb)

	def stop(self):
		rx.stop()

def ends_callback():
	rxmonitor.thread_ends()

def status_callback(msg):
	rxmonitor.thread_status(msg)

def parse_config(options):

	with open(options.config) as config:
		c = json.load(config)
		options.host = c['host']
		options.port = c['port']
		options.mnt = c['mnt']
		options.name = c['name']
		options.server = c['server']	

def handle_SIGTERM(signum, frame):
    log.info("--------------------------------> handle_SIGTERM")
    rxmonitor.exit() 

def handle_SIGINT(signum, frame):
    log.info("--------------------------------> handle_SIGINT") 
    rxmonitor.exit()

def handle_SIGSTOP(signum, frame):
    log.info("--------------------------------> handle_SIGSTOP")    
    rxmonitor.exit() 

def handle_SIGHUP(signum, frame):
    log.info("--------------------------------> handle_SIGHUP") 
    rxmonitor.exit() 

def handle_SIGKILL(signum, frame):
    log.info("--------------------------------> handle_SIGKILL")
    rxmonitor.exit()    

def handle_SIGQUIT(signum, frame):
    log.info("--------------------------------> handle_SIGQUIT")
    rxmonitor.exit() 

def handle_CTRL_C_EVENT(signum, frame):
    log.info("--------------------------------> CTRL_C_EVENT")
    rxmonitor.exit() 


if __name__ == "__main__":

    p = OptionParser();
    p.add_option('-c', '--config', action="store", help="configuration file", default="config.in")
    p.add_option('-i', '--host', action="store", help="host address")    
    p.add_option('-p', '--port', action="store", help="port")
    p.add_option('-m', '--mnt', action="store", help="mount point")
    p.add_option('-n', '--name', action="store", help="name of the rx monitor")
    p.add_option('-s', '--server', action="store", help="sb server address")

    options, args = p.parse_args()

    if os.path.isfile(options.config):
    	parse_config(options)

    if options.host is None:
    	p.print_help()
    	p.error('No host specified.')    	

    if options.port is None:
    	p.print_help()
    	p.error('No port specified.')    	

    if options.mnt is None:
    	p.print_help()
    	p.error('No mount point specified.')

    signal.signal(signal.SIGTERM, handle_SIGTERM)
    signal.signal(signal.SIGINT, handle_SIGINT)
    #signal.signal(signal.SIGSTOP, handle_SIGSTOP)
    signal.signal(signal.SIGHUP, handle_SIGHUP)
    #signal.signal(signal.SIGKILL, handle_SIGKILL)
    signal.signal(signal.SIGQUIT, handle_SIGQUIT)
    signal.signal(signal.CTRL_C_EVENT, handle_CTRL_C_EVENT)

    log.info("[rxmonitor] start - " + options.name)

    rxmonitor = RXMonitor(name=options.name, config=options)
    rxmonitor.monitor(status_callback, ends_callback)

    log.info("[rxmonitor] end")
