import sys, os, subprocess, time, json, logging
from optparse import OptionParser
from uritools import uricompose
import lib.vlc as vlc
import lib.log as log

SLEEP_sec = 3
TIMOUT_STATUS_sec = 1 * 60

STOP = False

def parse_config(options):

	with open(options.config) as config:
		c = json.load(config)
		options.host = c['host']
		options.port = c['port']
		options.mnt = c['mnt']

def stop():
	global STOP
	STOP = True

def run(options, status_cb, exit_cb):

	global STOP

	# volume (for rpi + hifiberry)
	if sys.platform == 'linux2':
		subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "45%"])

	def cb_status(status, status_cb):
		if status_cb is not None:
			status_cb(status)

	url = uricompose(scheme='http', host=options.host, port=int(options.port), path=options.mnt)

	vi = vlc.Instance()

	stream = vi.media_new(url)
	machine = vi.media_player_new()
	machine.set_media(stream)

	log.info('[rx] open ' + url)

	status = machine.play()

	time.sleep(SLEEP_sec)

	log.info("[rx] " + str(machine.get_state()))
	cb_status(str(machine.get_state()), status_cb)	

	tick = 0
	while machine.get_state() == vlc.State.Playing:
		time.sleep(SLEEP_sec)
		tick += SLEEP_sec
		if tick > TIMOUT_STATUS_sec:
			tick = 0
			log.info("[rx] " + str(machine.get_state()))
			cb_status(str(machine.get_state()), status_cb)
		if STOP:
			machine.stop()
			STOP = False			
			time.sleep(1)
			break

	if machine.get_state() == vlc.State.Error:
		log.err("[rx] " + str(machine.get_state()))
		cb_status(str(machine.get_state()), status_cb)
	else:
		log.info("[rx] " + str(machine.get_state()))
		cb_status(str(machine.get_state()), status_cb)

	if exit_cb is not None:
		exit_cb()


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

    log.info('[rx] start')

    run(options, None, None)

    log.info('[rx] end')
