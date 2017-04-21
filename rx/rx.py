import sys, os, time, json, logging
from optparse import OptionParser
from uritools import uricompose

import vlc

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(filename='rx.log', format='%(asctime)s -- RX/%(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

SLEEP_sec = 3
TIMOUT_STATUS_sec = 5 * 60

def parse_config(options):

	with open(options.config) as config:
		c = json.load(config)
		options.host = c['host']
		options.port = c['port']
		options.mnt = c['mnt']

@vlc.callbackmethod
def vlc_error(event, data):
	print event

def run(options):	


	url = uricompose(scheme='http', host=options.host, port=int(options.port), path='/'+options.mnt)

	vi = vlc.Instance()

	stream = vi.media_new(url)
	machine = vi.media_player_new()
	machine.set_media(stream)

	logging.info('open ' + url)

	status = machine.play()

	time.sleep(SLEEP_sec)

	tick = 0
	while machine.get_state() == vlc.State.Playing:
		time.sleep(SLEEP_sec)
		tick += SLEEP_sec
		if tick > TIMOUT_STATUS_sec:
			tick = 0
			logging.info(machine.get_state())				

	if machine.get_state() == vlc.State.Error:
		logging.error(machine.get_state())
	else:
		logging.info(machine.get_state())
	

if __name__ == "__main__":

    p = OptionParser();
    p.add_option('-c', '--config', action="store", help="configuration file", default="config.in")
    p.add_option('-i', '--host', action="store", help="host address")    
    p.add_option('-p', '--port', action="store", help="port")
    p.add_option('-m', '--mnt', action="store", help="mount point")

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

    logging.info('start rx')

    run(options)

    logging.info('end rx \n\n')
