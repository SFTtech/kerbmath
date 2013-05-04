from math import *
from kerbmath.util import *

from kerbmath.orbit import Orbit
from kerbmath.atmosphere import Atmosphere

G = 6.67384e-11

class Body:
	#the system that the body belongs to
	#the class can not be instantiated while this variable is None
	system = None

	def __init__(self, name, mass, radius, maxelev = 0, rotperiod = inf, atm = None):
		"""
		name            Name (will also be used as variable name)
		mass            Mass (kg)
		radius          Radius (m)
		maxelev         Highest elevation over surface (m)
		rotperiod	Siderial rotation period (s)
		atm             Atmosphere (Atmosphere object)
		"""
		if self.system == None:
			raise Exception("Can not instantiate systemless body")

		if atm == None:
			atm = Atmosphere(cutoff = 0)
		atm.body = self

		self.__dict__.update(locals())

		self.system.addbody(self)

	def __str__(self):
		return self.name

	def __repr__(self):
		rep = self.name + ": "
		rep += diststr(self.radius)
		minorbith = self.minorbitr() - self.radius
		if minorbith > 0.0001 * self.radius:
			rep += " + " + diststr(minorbith)

		return rep

	def mu(self):
		"""
		returns         µ = GM
		"""
		return G * self.mass

	def accel(self, r):
		"""
		h               height over surface (m)
		returns         acceleration (m/s^2)
		"""
		return self.mu()/(r * r)

	def minorbitr(self):
		"""
		returns         radius of the lowest stable orbit (outside atmosphere and above the highest elevation)
		"""
		return self.radius + max(self.atm.cutoff, self.maxelev)

	def minorbit(self):
		"""
		returns         lowest stable orbit object, with an inclination of 0 deg
		"""
		return self.orb(ra = self.minorbitr(), rp = self.minorbitr(), name = "lowest" + self.name)

	def orb(self, hp = None, ha = None, **kw):
		"""
		creates an orbit around this object

		see the documentation for the Orbit() constructor for valid parameters
		"""
		body = self
		del self
		kw.update(locals())
		Orbit(**kw)
