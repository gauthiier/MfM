import os, platform, subprocess, time, json, logging
from optparse import OptionParser
from lib.monitor import Monitor
import log
	   
class TXMonitor(Monitor):

    p = None

    def run(self, config, status_cb, ends_cb):

        if platform.system() == 'Linux':
            self.p = subprocess.Popen(['liquidsoap', 'tx.li'])
        else:
            self.p = subprocess.Popen(['sleep', '20'])

        sig = self.p.poll()
        while sig is None:
            sig = self.p.poll()
            time.sleep(2)
            self.thread_status('ON AIR')

        self.thread_status('OFF AIR')
        self.thread_ends()

    def stop(self):
        if self.p is not None:
            self.p.terminate()

def parse_config(options):

	with open(options.config) as config:
		c = json.load(config)
		options.host = c['host']
		options.port = c['port']
		options.mnt = c['mnt']
		options.name = c['name']
		options.server = c['server']	

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

    txmonitor = TXMonitor(name=options.name, config=options)
    txmonitor.monitor(None, None)
