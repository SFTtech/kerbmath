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

	def minorbit(self, incl = 0, omega = 0):
		"""
		creates the lowest stable orbit
		"""
		self.orb(ra = self.minorbitr(), rp = self.minorbitr(), name = "min" + self.name, incl = incl, omega = omega)

	def rotvvector(self, rvector):
		"""
		returns the velocity vector of rotation at a certain position
		rvector       position vector in IRF
		returns       velocity vector in IRF

		x and y span the equatorial plane (arbitrary orientation)
		z is the axis of rotation
		"""
		#calculate absolute value of r
		rx, ry, rz = rvector
		r = sqrt(rx * rx + ry * ry + rz * rz)
		#length of radius projected on equator
		req = sqrt(rx * rx + ry * ry)
		#angle of radius against equator
		alpha = atan2(rz, req)
		#radius of rotation circle
		rrot = r * cos(alpha)
		#velocity of rotation
		vrot = rrot * 2 * pi / self.rotperiod
		#obviously, the rotation circle is centered around the z axis
		vz = 0
		#the velocity vector is 90 degrees ahead of the radius vector on the equatorial plane
		#hence, the velocity direction vector is given by
		vx = ry
		vy = -rx
		#and finally, scaled
		vx *= vrot / req
		vy *= vrot / req

		return vx, vy, vz
		

	def orb(self, hp = None, ha = None, **kw):
		"""
		creates an orbit around this object

		see Orbit.__init__
		"""
		kw["body"] = self
		kw["hp"] = hp
		kw["ha"] = ha
		Orbit(**kw)
