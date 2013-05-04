from math import *
from kerbmath.util import *

class Orbit:
	def __init__(self, body, hp = None, ha = None, incl = 0, omega = 0, ra = None, rp = None, a = None, e = None, vr = None, vh = None, vinf = None, name = None):
		"""
		body            central body of the orbit
		hp              height of periapsis above surface (km)
		ha              height of apoapsis above surface (km)
		incl            inclination: angle between orbital plane and equatorial plane of body (deg)
		omega           argument of perigee: angle between perigee and ascending node (deg)
		ra              radius of apoapsis (m)
		rp              radius of periapsis (m)
		a               semi-major axis (m)
		e               eccentricity
		vr              velocity (m/s) at height above center of mass (m): tuple
		vh		velocity (m/s) at height above surface (km): tuple
		vinf            velocity at infinity (m/s, for escape orbits)
		name		an orbit name

		incl and omega may always be specified 
		almost any two of rp/hp, ra/ha, a, e, vinf may be specified (unimplemented combinations will raise exceptions)
		alternatively to vinf, vr or vh may be specified
		"""
		#set body and
		self.body = body
		self.name = name
		#take over incl and omega
		self.incl = incl
		self.omega = omega

		#normalize and check the hp/ha/rp/ra parameters
		if hp != None and rp != None:
			raise Exception("hp and rp are mutually exclusive")
		if ha != None and ra != None:
			raise Exception("ha and ra are mutually exclusive")
		if ha != None:
			ra = ha * 1000 + body.radius
		if hp != None:
			rp = hp * 1000 + body.radius
		del ha
		del hp

		if ra != None:
			#by convention, parabolic orbits have an ra of -inf
			if ra == +inf:
				ra = -inf

		if ra != None and rp != None and a != None:
			raise Exception("rp, ra, a can not be stated together")

		if ra != None and rp != None:
			if ra > 0 and rp > ra:
				#swap ra and rp
				ra, rp = rp, ra

		#ra and rp have been processed; combine with a
		if ra != None and a != None:
			rp = 2 * a - ra
			a = None
			if ra == -inf:
				raise Exception("rp must be specified for parabolic orbits")

		if rp != None and a != None:
			ra = 2 * a - rp
			a = None
			if ra == +inf:
				ra = -inf

		if rp != None and rp < 0:
			raise Exception("rp must be >= 0, but is " + diststr(rp))

		#ra, rp and a have been processed; combine with e
		if ra != None and rp != None and e != None:
			raise Exception("rp, ra, e can not be stated together")

		if rp != None and e != None:
			if e < 0:
				raise Exception("e must be >= 0")
			if e == 1:
				ra = -inf
			else:
				ra = rp * (1 + e) / (1 - e)
			e = None
		
		if ra != None and e != None:
			if e < 0:
				raise Exception("e must be >= 0")
			rp = ra * (1 - e) / (1 + e)
			if ra == -inf or e == 1:
				raise Exception("rp must be specified for parabolic orbits")
			e = None

		if a != None and e != None:
			if e < 0:
				raise Exception("e must be >= 0")
			if ra != None or rp != None:
				raise Exception("only two of a, e, ra, rp can be specified")
			if e == 1 or abs(a) == inf:
				raise Exception("rp must be specified for parabolic orbits")

			rp = (1 - e) * a
			ra = 2 * a - rp
			e = None
			a = None
		
		#ra, rp, e, a have been processed; combine with vinf/vr/vh
		if vr != None and vh != None:
			raise Exception("only one of vh/vr may be specified")

		if vh != None:
			v, h = vh
			vr = (v, 1000 * h + body.radius)
			del v, h
			vh = None

		if vr != None and vinf != None:
			raise Exception("only one of vh/vr/vinf may be specified")
		
		if vr != None:
			v, r = vr
			vinf = sqrt(v * v - 2 * body.mu()/r)
			del v, r
			vr = None

		if rp != None and vinf != None:
			if ra != None:
				raise Exception("only two of vinf, a, e, ra, rp can be specified")
			if vinf < 0:
				raise Exception("vinf must be >= 0")
			elif vinf == 0:
				ra = -inf
			else:
				a = -body.mu() / (vinf * vinf)
				ra = 2 * a - rp
				a = None
			vinf = None

		if ra != None and vinf != None:
			#TODO
			raise Exception("Not implemented: calculation of orbital elements from (ra, vinf)")

		if a != None and vinf != None:
			#TODO
			raise Exception("Not implemented: calculation of orbital elements from (a, vinf)")

		if e != None and vinf != None:
			#TODO
			raise Exception("Not implemented: calculation of orbital elements from (e, vinf)")

		#all parameters have been processed; check whether we were successful
		if ra == None or rp == None:
			raise Exception("Not enough data to calculate orbital elements")

		self.ra = ra
		self.rp = rp
		body.system.addorb(self)

	def __repr__(self):
		#orbit name
		rep = self.name + ": "

		#body name
		rep += self.body.name

		#trajectory dimensions
		if self.ra < 0:
			#escape trajectory
			rep += " escape trajectory, " + diststr(self.rp - self.body.radius) + "/vinf=" + str(self.v(inf)) + "m/s"
		else:
			#orbit
			rep += " orbit, " + diststr(self.rp - self.body.radius) + "/" + diststr(self.ra - self.body.radius)

		#inclination
		if self.incl != 0:
			rep += ", incl = %.2f deg" % self.incl

		if self.omega != 0:
			rep += ", omega = %.2f deg" % self.omega

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
		return 2 * pi * sqrt((self.a() ** 3) / self.body.mu())

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
		if rpnew > self.ra:
			raise Exception("Can not raise periapsis over apoapsis")

		return Orbit(self.body, ra = self.ra, rp = rpnew, incl = self.incl, omega = self.omega).va() - self.va()

	def chra(self, ranew):
		"""
		ranew           target apoapsis height over center of mass (m)
		returns         apoapsis burn dv
		"""
		if ranew > 0 and ranew < self.rp:
			raise Exception("Can not lower apoapsis below periapsis")

		return Orbit(self.body, ra = ranew, rp = self.rp, incl = self.incl, omega = self.omega).vp() - self.vp()

	def chhp(self, hpnew):
		"""
		hpnew 	        target periapsis height over surface (km)
		returns         apoapsis burn dv (m/s)
		"""
		rpnew = 1000 * hpnew + self.body.radius
		return self.chrp(rpnew)

	def chha(self, hanew):
		"""
		hanew           target apoapsis height over surface (km)
		returns         periapsis burn dv
		"""
		ranew = 1000 * hanew + self.body.radius
		return self.chra(ranew)

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
		inclnew         new inclination (deg)
		"""
		inclnew
		if r < self.rp or (self.ra > 0 and r > self.ra):
			raise Exception("Orbit does not reach this height")

		Orbit(self.body, ra = self.ra, rp = self.rp, incl = inclnew, omega = self.omega)
		#TODO not absolutely sure whether this formula holds for e != 0, but it should
		return 2 * self.v(r) * sin(radians((self.incl - inclnew) / 2))

	def chih(self, h, inclnew):
		"""
		h               height over surface (km) where the inclination change is performed
		inclnew         new inclination (deg)
		"""
		r = h * 1000 + self.body.radius
		return self.chir(r, inclnew)

	def thetafromr(self, r):
		"""
		r               height over center of mass (m)
		returns         angle in orbit (degrees, 0: periapsis)
		"""
		return degrees(acos((self.rp * ( 1 + self.e() ) / r - 1) / self.e()))

	def rfromtheta(self, theta):
		"""
		theta           angle in orbit (degrees, 0: periapsis)
		returns         height over center of mass at that point (m)
		"""
		return self.rp * (1 + self.e()) / (1 + self.e() * cos(radians(theta)))

	def rvector(self, r):
		"""
		r               height above center of mass (m)
		theta           angle in orbit (degrees; 0 means periapsis)
		returns         velocity vector in IRF
				z points north
				y points towards ascending node
				x spans the equatorial plane with y
		"""
		theta = self.thetafromr(r)
		#first, calculate without inclination
		rx = cos(radians(theta + self.omega)) * r
		ry = sin(radians(theta + self.omega)) * r
		#the inclination decides how ry is distributed among ry and rz
		ry, rz = cos(radians(self.incl)) * ry, sin(radians(self.incl)) * ry
		#vector is already scaled to correct length; done.
		return rx, ry, rz

	def vvector(self, r):
		"""
		r               height above center of mass (m)
		returns         velocity vector in IRF
				z points north
				y points towards ascending node
				x spans the equatorial plane with y
		"""
		theta = self.thetafromr(r)
		#first, ignore the inclination; thus z = 0
		vx = cos(radians(theta + self.omega)) + self.e() * sin(radians(self.omega))
		vy = sin(radians(theta + self.omega)) + self.e() * cos(radians(self.omega))
		#the inclination decides how vy is distributed among vy and vz
		vy, vz = -cos(radians(self.incl)) * vy, sin(radians(self.incl)) * vy
		#scale to correct length
		scalefactor = self.v(r) / sqrt(vx * vx + vy * vy + vz * vz)
		vz *= scalefactor
		vy *= scalefactor
		vx *= scalefactor
		#done
		return vx, vy, vz
	
	def aerobrake(self, d = 0.2, timesteps = 0.001):
		"""
		numerically simulates aerobrake/aerocapture
		orbit must partially lie within the atmosphere for this to work

		d               drag coefficient
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

		ventry = self.vvector(entryr)
		rentry = self.rvector(entryr)

		print("Entry velocity: " + str(ventry) + ", entry radius: " + str(rentry))
