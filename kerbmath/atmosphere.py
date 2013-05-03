from math import *
from kerbmath.util import *

class Atmosphere:
	def __init__(self, cutoff = 0, scaleh = 0, p0 = 0, rho0 = 0):
		"""
		cutoff          The cutoff height (m)
		scaleh		The scale height (where pressure/density decreses by e; m)
		p0		The surface pressure (N/m^2)
		rho0            The surface density (kg/m^3)
		"""
		self.__dict__.update(locals())

	def p(self, h):
		"""
		h               Height (m)
		returns         Pressure at h (N/m^2)
		"""
		if h >= self.cutoff:
			return 0
		return self.p0 * exp(-h / self.scaleh)

	def rho(self, h):
		"""
		h		Height (m)
		returns		Air density at h (kg/m^3)
		"""
		#TODO check whether this is really true
		#in RL, rho ~ 1/T and rho ~ p
		return self.rho0 * self.p(h)/self.p0

	def accel(self, h, v, d = 0.2):
		"""
		h               Height (m)
		v               Velocity relative to atmosphere (m/s)
		d               Drag coefficient of the ship (usually 0.2, unitless)
		returns         Acceleration due to drag (m/s^2, positive)
		"""
		return 0.5 * self.rho(h) * v * v * d

	def vterm(self, h, d = 0.2):
		"""
		h               Height (m)
		d               Drag coefficient of the ship (usually 0.2, unitless)
		returns         Terminal velocity (F_G = F_D, m/s)
		"""
		if h > self.cutoff:
			return inf
		return sqrt(self.body.accel(h)/(0.5 * self.rho(h) * d))
