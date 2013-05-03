from kerbmath.util import *

class System:
	"""
	Stores all orbits and bodies e.g. of an interactive session
	Very well-suited to be used as global namespace for interactive session
	"""
	def __init__(self, globalorbits = True, printorbits = True, globalbodies = True, printbodies = True):
		"""
		globalorbits  orbits are not only added to the orbits dict, but to the system itself
		printorbits   orbits are printed when added
		globalbodies  bodies are not only added to the bodies dict, but to the system itself
		printbodies   bodies are printed when added
		"""
		orbits = {}
		bodies = {}

		#create a subclass of Body, which changes only the 'system' member variable
		from kerbmath.body import Body as SuperBody
		class Body(SuperBody):
			system = self
		del SuperBody
		#add constructors for all other classes to our namespace
		from kerbmath.orbit import Orbit
		from kerbmath.atmosphere import Atmosphere

		self.__dict__.update(locals())

	def freeorbname(self, prefix):
		"""
		finds a free name for an orbit

		prefix    prefix for the name
		"""
		idx = 0
		while True:
			name = str(prefix) + str(idx)
			if name not in self.orbits and name not in self.__dict__:
				break
			idx += 1

		return name

	def addbody(self, body):
		"""
		add a body to the system

		body      the body
		"""
		self.bodies[body.name] = body
		if self.globalbodies:
			self.__dict__[body.name] = body

		if self.printbodies:
			colprint(repr(body), 33)

	def addorb(self, orb, prefix = "orb"):
		"""
		add an orbit to the system
		automatically chooses a free name

		orb       the orbit
		prefix    a prefix for the auto-generated name
		"""
		if orb.name != None:
			if orb.name in self.orbits:
				orb.name = self.freeorbname(orb.name)
		else:
			orb.name = self.freeorbname(prefix)

		self.orbits[orb.name] = orb
		if self.globalorbits:
			self.__dict__[orb.name] = orb

		if self.printorbits:
			colprint(repr(orb), 32)

	def readconf(self, conffile = "system.conf"):
		"""
		(re-)read the system configuration file

		conffile:   the configuration file path
		"""
		exec(open(conffile).read(), self.__dict__)

	def clearorbits(self, filterfun = lambda orb: True):
		"""
		delete orbits

		filterfun:  orbits are deleted if filterfun(orb) returns True
		"""
		for name in self.orbits:
			if filterfun == None or filterfun(self.orbits[name]):
				self.orbits.delete(name)
				self.__dict__.delete(name)
