from math import *
from kerbmath.util import *

class Orbit:
	def __init__(self, body, ra, rp, incl = 0, name = None):
		"""
		Note that the Body objects provide much more convenient member functions for orbits around them

		body            central body
		ha              height of apogee (m)
		hp              height of perigee (m)
		incl            inclination against equatorial plane (rads)
		"""
		if rp < 0:
			raise Exception("periapsis height must be >= 0")
		elif ra == +inf:
			#arbitrary convention: we use -inf for parabolic orbits
			ra = -inf
		elif ra < rp:
			raise Exception("apoapsis height must be >= periapsis height")

		self.__dict__.update(locals())

		body.system.addorb(self)

	def __repr__(self):
		#orbit name
		rep = self.name + ": "

		#body name
		rep += self.body.name

		#trajectory dimensions
		if self.ra < 0:
			#escape trajectory
			rep += " escape trajectory, " + diststr(self.ra - self.body.radius) + "/vinf=" + str(self.v(inf)) + "m/s"
		else:
			#orbit
			rep += " orbit, " + diststr(self.ra - self.body.radius) + "x" + diststr(self.rp - self.body.radius)

		#inclination
		if self.incl != 0:
			rep += ", incl = %.2f deg" % degrees(self.incl)

		return rep
		

	def e(self):
		"""
		returns         eccentricity
		"""
		return (1 - self.rp/self.ra) / (1 + self.rp/self.ra)

	def a(self):
		"""
		returns         semi-major axis (m)
		"""
		return (self.ra + self.rp)/2

	def specenergy(self):
		"""
		returns         specific energy of the orbit (J/kg)
		"""
		return -0.5 * self.body.mu() / self.a()

	def period(self):
		"""
		returns         orbital period (s)
		"""
		return 2 * pi * sqrt((self.a() ** 3) * self.body.mu())

	def v(self, r):
		"""
		r               height over center of mass (m)
		returns         v (m/s)
		"""
		return sqrt(self.body.mu() * (2/r - 1/self.a()))

	def vp(self):
		"""
		returns         periapsis velocity (m/s)
		"""
		return self.v(self.rp)

	def va(self):
		"""
		returns         apoapsis velocity (m/s)
		"""
		return self.v(self.ap)

	def vp(self):
		"""
		returns         periapsis velocity (m/s)
		"""
		return self.v(self.rp)

	def va(self):
		"""
		returns         apoapsis velocity or velocity at infinity (m/s)
		"""
		if self.ra < 0:
			#escape orbit
			return self.v(inf)
		else:
			return self.v(self.ra)

	def chrp(self, rpnew):
		"""
		rpnew           target periapsis height over center of mass (m)
		returns         apoapsis burn dv
		"""
		if self.ra < 0: 
			raise Exception("Can not optimally lower periapsis while on escape trajectory")
		if self.rpnew > self.ra:
			raise Exception("Can not raise periapsis over apoapsis")

		return Orbit(self.body, self.ra, rpnew, self.incl)

	def chra(self, ranew):
		"""
		ranew           target apoapsis height over center of mass (m)
		returns         apoapsis burn dv
		"""
		if ranew > 0 and ranew < self.rp:
			raise Exception("Can not lower apoapsis below periapsis")

		return Orbit(self.body, ranew, self.rp, self.incl)

	def chhp(self, hpnew):
		"""
		hpnew 	        target periapsis height over surface (km)
		returns         apoapsis burn dv (m/s)
		"""
		rpnew = 1000 * hpnew + self.body.radius
		chrp(self, rpnew)

	def chha(self, hanew):
		"""
		hanew           target apoapsis height over surface (km)
		returns         periapsis burn dv
		"""
		ranew = 1000 * hanew + self.body.radius
		chra(self, ranew)

	def deorbit(self):
		"""
		returns         apoapsis dv to de-orbit
		"""
		return self.chrp(self.body.minorbitr())

	def escape(self):
		"""
		returns         periapsis dv to escape
		"""
		return self.chra(inf)

	def circ(self):
		"""
		returns		periapsis dv to make orbit circular
		"""
		return self.chrp(self.ra)

	def chir(self, r, inclnew):
		"""
		r               height over center of orbit (m) at which the inclination change is performed
		inclnew         new inclination
		"""
		if r < self.rp or (self.ra > 0 and r > self.ra):
			raise Exception("Orbit does not reach this height")

		Orbit(self.body, self.ra, self.rp, inclnew)
		#TODO not absolutely sure whether this formula holds for e != 0, but it should
		return 2 * self.v(r) * sin(self.incl - inclnew)

	def chih(self, h, inclnew):
		"""
		h               height over surface (km) where the inclination change is performed
		inclnew         new inclination
		"""
		r = h * 1000 + self.body.radius
		return self.chir(r, inclnew)

	def thetafromr(self, r):
		"""
		r               height over center of mass (m)
		returns         angle in orbit (rads, 0: periapsis)
		"""
		return acos((self.rp * ( 1 + self.e() ) / r - 1) / self.e())

	def rfromtheta(self, theta):
		"""
		theta           angle in orbit (rads, 0: periapsis)
		returns         height over center of mass at that point (m)
		"""
		return self.rp * (1 + self.e()) / (1 + self.e() * cos(radians(theta)))

	def rvector(self, r, omega = 0):
		"""
		r               height above center of mass (m)
		theta           angle in orbit (rads; 0 means periapsis)
		omega           argument of periapsis (rads; 0 means ascending node)
		returns         velocity vector in IRF
				z points north
				y points towards ascending node
				x spans the equatorial plane with y
		"""
		theta = self.thetafromr(r)
		#first, calculate without inclination
		rx = cos(radians(theta + omega)) * r
		ry = sin(radians(theta + omega)) * r
		#the inclination decides how ry is distributed among ry and rz
		ry, rz = cos(radians(self.incl)) * ry, sin(radians(self.incl)) * ry
		#vector is already scaled to correct length; done.
		return rx, ry, rz

	def vvector(self, r, omega = 0):
		"""
		r               height above center of mass (m)
		theta           angle in orbit (rads; 0 means periapsis)
		omega           argument of periapsis (rads; 0 means ascending node)
		returns         velocity vector in IRF
				z points north
				y points towards ascending node
				x spans the equatorial plane with y
		"""
		theta = self.thetafromr(r)
		#first, ignore the inclination; thus z = 0
		vx = cos(theta + omega) + self.e() * sin(omega)
		vy = sin(theta + omega) + self.e() * cos(omega)
		#the inclination decides how vy is distributed among vy and vz
		vy, vz = -cos(self.incl) * vy, sin(self.incl) * vz
		#scale to correct length
		scalefactor = self.v(r) / sqrt(vx * vx + vy * vy + vz * vz)
		vz *= scalefactor
		vy *= scalefactor
		vx *= scalefactor
		#done
		return vx, vy, vz
	
	def aerobrake(self, d = 0.2, omega = 0, timesteps = 0.001):
		"""
		numerically simulates aerobrake/aerocapture
		orbit must partially lie within the atmosphere for this to work

		d               drag coefficient
		omega           argument of periapsis (rads; 0 means ascending node)
		timesteps       time per physics frame (s)
		"""
		entryr = self.body.atm.cutoff + self.body.radius
		collisionr = self.body.maxelev + self.body.radius

		if self.rp > entryr:
			raise Exception("Orbit outside atmosphere")
		if self.ra > 0 and self.ra < entryr:
			raise Exception("Orbit completely within atmosphere")

		#we start our numerical simulation when the vessel enters the atmosphere (r = entryr)
		#all calculations are done in IRF: origin is the center of mass,
		# z points north
		# y points towards ascending node (of the old orbit)
		# x spans the equatorial plane with y

		ventry = self.vvector(entryr, omega)
		rentry = self.rvector(entryr, omega)

		print("Entry velocity: " + str(ventry) + ", entry radius: " + str(rentry))
