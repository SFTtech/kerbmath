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
		return self.orbr(self.minorbitr(), self.minorbitr(), 0, name = "lowest" + self.name)

	def orbrr(self, ra, rp, incl = 0):
		"""
		creates an orbit object

		ra              height of apogee over center of mass (m)
		rp              height of perigee over center of mass (m)
		incl            inclination against equatorial plane (deg)
		"""
		Orbit(self, ra, rp, incl)

	def orbhh(self, ha, hp, incl = 0):
		"""
		creates an orbit object
		
		ha              height of apogee over surface (km)
		hp              height of perigee over surface (km)
		incl            inclination against equatorial plane (deg)
		"""
		rp = 1000 * hp + self.radius
		ra = 1000 * ha + self.radius
		self.orbrr(ra, rp, incl)

	def orbae(self, a, e, incl = 0):
		"""
		creates an Orbit object

		a               semi-major axis (m)
		e               eccentricity
		incl		inclination against equatorial plane (deg)
		"""
		rp = (1 - e) * a
		ra = 2 * a - rp
		self.orbrr(ra, rp, incl)

	def escorbr(self, rp, vinf = 0, incl = 0):
		"""
		creates an orbit object

		hp              height of perigee over center of mass (m)
		vinf            velocity at infinity (m/s)
		incl            inclination against equatorial plane (deg)
		"""
		a = -self.mu()/(vinf * vinf)
		ra = 2 * a - rp
		self.orbrr(ra, rp, incl)

	def escorbh(self, hp, vinf = 0, incl = 0):
		"""
		creates an orbit object

		hp              height of perigee over surface (km)
		vinf            velocity at infinity
		incl            inclination against equatorial plane (deg)
		"""
		rp = 1000 * hp + self.radius
		self.escorbr(hp, vinf, incl)
