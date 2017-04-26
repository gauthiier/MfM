import threading, time, logging, traceback
from pySpacebrew import spacebrew
from fsm import StateMachine

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
		print "---- state_signal ----"
		self.STATE = bool(value)

	def monitor_signal(self, value):
		print "++++ monitor_signal ++++"
		print value
		self.EXIT = bool(value)
		print self.EXIT

	def thread_ends(self):
		self.STATE = False

	def thread_status(self, str_msg):
		self.emit("status", str_msg)

	def run(self, config, status_cb, ends_cb):
		print "override this (parent) function - run"
		time.sleep(2)

	def stop(self):
		print "override this (parent) function - stop"		
		time.sleep(2)

	def state_on(self, c):

		print "state_on"

		# on transition
		if self.STATE and self._thread is None:
			self._thread = threading.Thread(target=self.run, args=(self.config, self.status_cb, self.ends_cb))
			self._thread.start()
			self.emit("state", strbool(True))

		# transit?
		if self.EXIT:
			# exit transition
			self.STATE = False
			return ("state_exit", None)
		elif not self.STATE:
			# off transition
			return ("state_off", None)
		else:
			# on transition (re-entry)
			time.sleep(2)
			return ("state_on", None)

	def state_off(self, c):

		print "state_off"

		# on transition
		if not self.STATE and self._thread is not None:
			if self._thread.is_alive():
				print "thread still alive..."
				self.stop()
				self._thread.join()
			else:
				print "thread already terminated..."
			self._thread = None
			self.emit("state", strbool(False))

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

	def monitor(self, status_cb, ends_cb):

		self._sb = spacebrew.Spacebrew(name=self.name, server=self.config.server)
		self.register()

		self.status_cb = status_cb
		self.ends_cb = ends_cb

		try:
			self._sb.start()

			while not self.EXIT:

				self.emit("monitor", strbool(True))

				m = StateMachine()
				m.add_state("state_on", self.state_on)
				m.add_state("state_off", self.state_off)
				m.add_state("state_exit", None, end_state=1)
				m.set_start("state_off")
				m.run(None)

		except Exception as e:
			print e
			print traceback.format_exc()
		finally:
			print "Exiting"
			self._sb.stop()
			self.emit("monitor", False)









