import threading, time, logging, traceback
from pySpacebrew import spacebrew
from fsm import StateMachine
import log

def bool(str):
	return str == 'true'

def strbool(bool):
	if bool:
		return "true"
	return "false"

class Monitor:

	EXIT = False
	STATE = False
	_thread = None
	_sb = None

	def __init__(self, name, desc='', config=None):
		self.name = name
		self.desc = desc
		self.config = config

		if config is None or config.server is None:
			raise Exception('No host specified in config file.')

		self.end_lock = threading.Lock()

	def register(self):

		self._sb.addPublisher("monitor", "boolean")
		self._sb.addPublisher("state", "boolean")
		self._sb.addPublisher("status", "string")
		self._sb.addPublisher("config", "string")

		self._sb.addSubscriber("state", "boolean")
		self._sb.subscribe("state", self.state_signal)
		self._sb.addSubscriber("monitor", "boolean")
		self._sb.subscribe("monitor", self.monitor_signal)

	def emit(self, tag, value):
		try:
			self._sb.publish(tag, value)
		except Exception as e:
			print e
			pass

	def state_signal(self, value):
		log.info(self.idstr() + " state_signal - " + str(value))		
		with self.end_lock:
			self.STATE = bool(value)

	def monitor_signal(self, value):
		log.info(self.idstr() + " monitor_signal - " + str(value))
		self.EXIT = bool(value)
		print self.EXIT

	def thread_ends(self):
		self.end_lock.acquire()
		self.STATE = False

	def thread_status(self, str_msg):
		self.emit("status", str_msg)

	# override this (parent) function - run
	def run(self, config, status_cb, ends_cb):		
		time.sleep(2)

	# print "override this (parent) function - stop
	def stop(self):		
		time.sleep(2)

	def state_on(self, c):

		log.info(self.idstr() + " state_on")
		self.emit("state", strbool(True))

		# on transition
		if self.STATE and self._thread is None:
			self._thread = threading.Thread(target=self.run, args=(self.config, self.status_cb, self.ends_cb))
			self._thread.start()
			self.emit("state", strbool(True))

		# transit?
		if self.EXIT:
			# exit transition
			self.STATE = False
			self.stop()
			return ("state_exit", None)
		elif not self.STATE:
			# off transition
			return ("state_off", None)
		else:
			# on transition (re-entry)
			time.sleep(2)
			return ("state_on", None)

	def state_off(self, c):

		log.info(self.idstr() + " state_off")
		self.emit("state", strbool(False))

		# on transition
		if not self.STATE and self._thread is not None:
			if self._thread.is_alive():
				log.info(self.idstr() + " thread still alive...")
				log.info(self.idstr() + " stop & join...")
				self.stop()
				self._thread.join()
			else:
				log.info(self.idstr() + "thread already terminated...")
			log.info(self.idstr() + "thread exited")
			self._thread = None
			self.emit("state", strbool(False))
			self.end_lock.release()

		# transit?
		if self.EXIT:
			# exit transition
			self.STATE = False
			return ("state_exit", None)
		elif self.STATE:
			# on transition
			return ("state_on", None)
		else:
			# off transition (re-entry)
			time.sleep(2)
			return ("state_off", None)

	def idstr(self):
		return "[monitor/" + self.name + "]"

	def monitor(self, status_cb, ends_cb, fsm_start_state_on=False):

		log.info(self.idstr() + " start")		

		self._sb = spacebrew.Spacebrew(name=self.name, server=self.config.server)

		log.info(self.idstr() + " registering spacebrew")

		self.register()

		self.status_cb = status_cb
		self.ends_cb = ends_cb

		try:
			log.info(self.idstr() + " start spacebrew")

			self._sb.start()

			while not self.EXIT:

				log.info(self.idstr() + " monitor loop/alive")

				self.emit("monitor", strbool(True))

				m = StateMachine()
				m.add_state("state_on", self.state_on)
				m.add_state("state_off", self.state_off)
				m.add_state("state_exit", self.stop, end_state=1)
				if fsm_start_state_on:
					self.STATE = True
					m.set_start("state_on")
					print "fsm start state_on"
				else:
					self.STATE = False
					m.set_start("state_off")
					print "fsm start state_off"
				m.run(None)

		except Exception as e:
			log.err(traceback.format_exc())
		finally:
			log.info(self.idstr() + " end spacebrew")
			self._sb.stop()
			self.emit("monitor", False)
			log.info(self.idstr() + " end")









