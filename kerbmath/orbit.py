from math import *
from kerbmath.util import *
import kerbmath.vector as vec

#TODO some formulae fail for circular orbits (e == 0); for example stuff related to theta

class Orbit:
	def __init__(self, body, **kw):
		"""
		body
			central body of the orbit
		name
			defaults to a free name such as 'orb0'

		> arguments that describe the orientation of the orbit
		> these may always be specified and are independent of the others
		> if not specified, they default to 0

		incl
			inclination (deg)
			angle between orbital plane and equatorial plane of body
		omega
			argument of periapsis (deg)
			angle between perigee and ascending node

		> arguments that describe the dimensions of the orbit
		> there are several groups of parameters
		> (such as: parameters that directly describe periapsis height)
		> from each group, only one may be specified
		> paraeters from exactly two groups must be specified to allow calculation
		> for some combinations, calcuation may be not implemented

		> periapsis height

		rp
			height of periapsis above center of mass (m)
		hp
			height of periapsis above surface (km)

		> apoapsis height

		ra
			height of apoapsis above center of mass (m)
		ha
			height of apoapsis above surface (km)

		> semi-major axis
		a
			semi-major axis (m)
		vr
			velocity at a certain height above center of mass (tuple of m/s, m)
		vh
			velocity at a certain height above surface (tuple of m/s, km)
		vinf
			velocity at infinity (m/s, may be negative for elliptical orbits)
		T
			orbital period (s)
		espec
			specific energy (J/kg)

		> eccentricity
		e
			eccentricity

		> periapsis velocity
		vp
			periapsis velocity (m/s)

		> apoapsis velocity
		va
			apoapsis velocity (m/s)
		"""

		#set body
		self.body = body

		#store kw in a container
		args = Container(kw, delonget = True)

		#set name, incl, omega
		try:
			self.name = args.name
		except AttributeError:
			self.name = None

		try:
			self.incl = args.incl
		except AttributeError:
			self.incl = 0

		try:
			self.omega = args.omega
		except AttributeError:
			self.omega = 0

		def onlyoneof(*vals):
			givenvals = args.vallist(*vals)
			if len(givenvals) > 1:
				raise Exception("Only one of " + liststr(vals) + " may be specified, but " + liststr(givenvals) + " were")

		#for each group, convert to the first element
		#stores the successfully converted params
		params = {}

		#rp group
		onlyoneof("rp", "hp")

		try:
			args.rp = args.hp * 1000 + body.radius
		except AttributeError:
			pass

		try:
			rp = args.rp
			if not rp > 0:
				raise Exception("rp must be > 0, but is " + diststr(rp))
			params["rp"] = diststr(rp)
		except AttributeError:
			rp = None

		#ra group
		onlyoneof("ra", "ha")

		try:
			args.ra = args.ha * 1000 + body.radius
		except AttributeError:
			pass

		try:
			ra = args.ra
			if ra == +inf:
				ra = -inf
			params["ra"] = diststr(ra)
		except AttributeError:
			ra = None

		#a group
		onlyoneof("a", "vr", "vh", "vinf", "T", "espec")

		try:
			v, h = args.vh
			args.vr = v, h * 1000 + body.radius
		except AttributeError:
			pass

		try:
			args.vr = args.vinf, inf
		except AttributeError:
			pass

		try:
			v, r = args.vr
			args.espec = v * v / 2 - body.mu() / r
		except AttributeError:
			pass

		try:
			args.espec = ((args.T/(2 * pi))**2 * body.mu()) ** (1/3)
		except AttributeError:
			pass

		try:
			args.a = -body.mu() / (2 * args.espec)
		except AttributeError:
			pass

		try:
			a = args.a
			if a == +inf:
				a = -inf
			if a == 0:
				raise Exception("a must be != 0, but is 0")
			params["a"] = diststr(a)
		except AttributeError:
			a = None

		#e group
		try:
			e = args.e
			if e < 0:
				raise Exception("e must be >= 0, but is " + str(e))
			params["e"] = str(e)
		except AttributeError:
			e = None

		#vp group
		try:
			vp = args.vp
			if vp < 0:
				raise Exception("vp must be >= 0, but is " + velstr(vp))
			params["vp"] = velstr(vp)
			params.append("vp")
		except AttributeError:
			vp = None

		#va group
		try:
			va = args.va
			if va < 0:
				raise Exception("va must be >= 0, but is " + velstr(va))
			params["va"] = velstr(va)
		except AttributeError:
			va = None

		#check whether exactly two are defined
		if len(params) != 2:
			raise Exception("Exactly 2 orbit dimension parameters must be given, but the following are: " + str(params))

		#check whether there are any unused args
		if len(args) != 0:
			raise Exception("Unknown arguments: " + liststr(args.vallist()))

		def orbitdims(rp = None, ra = None, a = None, e = None, vp = None, va = None):
			"""
			calculate rp, ra from the parameters rp, ra, a, e, vp, va,
			and return them as a tuple (rp, ra)
			"""
			if rp != None and ra != None:
				#if the user confused ra and rp, correct that
				if ra > 0 and rp > ra:
					ra, rp = rp, ra
				return rp, ra

			if rp != None and a != None:
				ra = 2 * a - rp
				if ra == +inf:
					ra = -inf
				return rp, ra

			if rp != None and e != None:
				if e == 1:
					ra = -inf
				else:
					ra = rp * (1 + e) / (1 - e)
				return rp, ra

			if rp != None and vp != None:
				espec = vp * vp / 2 - body.mu() / rp
				a = -body.mu() / (2 * args.espec)
				return orbitdims(rp = rp, a = a)

			if rp != None and va != None:
				#TODO
				raise Exception("Not implemented: orbitdims(rp, va)")

			if ra != None and a != None:
				if ra > 0 and a < 0:
					raise Exception("if ra > 0, a can not be < 0")
				if ra < 0 and a > 0:
					raise Exception("if ra < 0, a can not be > 0")
				if ra == -inf:
					raise Exception("rp must be known for parabolic orbits")
				rp = 2 * a - ra
				return rp, ra

			if ra != None and e != None:
				if ra == -inf or e == 1:
					raise Exception("rp must be known for parabolic orbits")
				rp = ra * (1 - e) / (1 + e)
				return rp, ra

			if ra != None and vp != None:
				#TODO
				raise Exception("Not implemented: orbitdims(ra, vp)")

			if ra != None and va != None:
				espec = va * va / 2 - body.mu() / ap
				a = -body.mu() / (2 * args.espec)
				return orbitdims(ra = ra, a = a)

			if a != None and e != None:
				if a == -inf or e == 1:
					raise Exception("rp must be known for parabolic orbits")

				rp = (1 - e) * a
				ra = 2 * a - rp

			if a != None and vp != None:
				#TODO
				raise Exception("Not implemented: orbitdims(a, vp)")

			if a != None and va != None:
				#TODO
				raise Exception("Not implemented: orbitdims(a, va)")

			if vp != None and va != None:
				#TODO
				raise Exception("Not implemented: orbitdims(vp, va)")

		self.rp, self.ra = orbitdims(rp, ra, a, e, vp, va)
		body.system.addorb(self)

	def __repr__(self):
		#orbit name
		rep = self.name + ": "

		#body name
		rep += self.body.name

		#trajectory dimensions
		if self.ra < 0:
			#escape trajectory
			rep += " escape trajectory, " + diststr(self.rp - self.body.radius) + "/vinf=" + velstr(self.v(inf))
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
		returns
			eccentricity
		"""
		return (1 - self.rp/self.ra) / (1 + self.rp/self.ra)

	def a(self):
		"""
		returns
			semi-major axis (m)
		"""
		return (self.ra + self.rp)/2

	def specenergy(self):
		"""
		returns
			specific energy (J/kg)
		"""
		return -0.5 * self.body.mu() / self.a()

	def period(self):
		"""
		returns
			orbital period (s)
		"""
		return 2 * pi * sqrt((self.a() ** 3) / self.body.mu())

	def v(self, r):
		"""
		r
			height over center of mass (m)
		returns
			v (m/s)
		"""
		return sqrt(self.body.mu() * (2/r - 1/self.a()))

	def vp(self):
		"""
		returns
			periapsis velocity (m/s)
		"""
		return self.v(self.rp)

	def va(self):
		"""
		returns
			apoapsis velocity or velocity at infinity (m/s)
		"""
		if self.ra < 0:
			#escape orbit
			return self.v(inf)
		else:
			return self.v(self.ra)

	def chrp(self, rpnew):
		"""
		rpnew
			target periapsis height over center of mass (m)
		returns
			apoapsis burn dv
		"""
		if self.ra < 0:
			raise Exception("Can not optimally lower periapsis while on escape trajectory")
		if rpnew > self.ra:
			raise Exception("Can not raise periapsis over apoapsis")

		return Orbit(self.body, ra = self.ra, rp = rpnew, incl = self.incl, omega = self.omega).va() - self.va()

	def chra(self, ranew):
		"""
		ranew
			target apoapsis height over center of mass (m)
		returns
			periapsis burn dv
		"""
		if ranew > 0 and ranew < self.rp:
			raise Exception("Can not lower apoapsis below periapsis")

		return Orbit(self.body, ra = ranew, rp = self.rp, incl = self.incl, omega = self.omega).vp() - self.vp()

	def chhp(self, hpnew):
		"""
		hpnew
			target periapsis height over surface (km)
		returns
			apoapsis burn dv (m/s)
		"""
		rpnew = 1000 * hpnew + self.body.radius
		return self.chrp(rpnew)

	def chha(self, hanew):
		"""
		hanew
			target apoapsis height over surface (km)
		returns
			periapsis burn dv
		"""
		ranew = 1000 * hanew + self.body.radius
		return self.chra(ranew)

	def deorbit(self):
		"""
		returns
			apoapsis dv to de-orbit
		"""
		return self.chrp(self.body.atm.cutoff)

	def escape(self):
		"""
		returns
			periapsis dv to escape
		"""
		return self.chra(inf)

	def circ(self):
		"""
		returns
			apoapsis dv to make orbit circular
		"""
		return self.chrp(self.ra)

	def chir(self, r, inclnew):
		"""
		r
			height over center of orbit (m) at which the inclination change is performed
		inclnew
			new inclination (deg)
		"""
		if r < self.rp or (self.ra > 0 and r > self.ra):
			raise Exception("Orbit does not reach this height")

		Orbit(self.body, ra = self.ra, rp = self.rp, incl = inclnew, omega = self.omega)
		#TODO not absolutely sure whether this formula holds for e != 0, but it should
		return 2 * self.v(r) * sin(radians((self.incl - inclnew) / 2))

	def chih(self, h, inclnew):
		"""
		h
			height over surface (km) where the inclination change is performed
		inclnew
			new inclination (deg)
		"""
		r = h * 1000 + self.body.radius
		return self.chir(r, inclnew)

	def thetafromr(self, r):
		"""
		r
			height over center of mass (m)
		returns
			angle in orbit (degrees, 0: periapsis)
		"""
		e = self.e()
		if e == 0:
			#for circular orbits, theta does not matter
			theta = 0
		else:
			theta = degrees(acos((self.rp * ( 1 + e ) / r - 1) / e))

		return theta

	def rfromtheta(self, theta):
		"""
		theta
			angle in orbit (degrees, 0: periapsis)
		returns
			height over center of mass at that point (m)
		"""
		e = self.e()
		r = self.rp * (1 + e) / (1 + e * cos(radians(theta)))
		return r

	def rvector(self, r):
		"""
		r
			height above center of mass (m)
		theta
			angle in orbit (degrees; 0 means periapsis)
		returns
			velocity vector in IRF
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
		r
			height above center of mass (m)
		returns
			velocity vector in IRF
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

		return vec.scalarprod(vec.unity((vx, vy, vz)), self.v(r))

	def aerobrake(self, d = 0.2, timestep = 0.001):
		"""
		numerically simulates aerobrake/aerocapture
		orbit must partially lie within the atmosphere for this to work

		d
			drag coefficient
		timestep
			time per physics frame (s)
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

		vr = self.rvector(entryr)
		vv = self.vvector(entryr)

		print("Entry position: " + vec.tostr(vr, diststr))
		print("Entry velocity: " + vec.tostr(vv, velstr))

		#run simulation
		while True:
			r = vec.abs(vr)
			if r < collisionr:
				print("Within ground collision range")
			if r < self.body.radius:
				break
			if r > entryr * 1.01:
				print("Atmosphere left")
				#break

			vvatm = self.body.rotvvector(vr)
			vvdelta = vec.diff(vv, vvatm)
			aatm = self.body.atm.accel(r - self.body.radius, vec.abs(vvdelta), d)
			vaatm = vec.scalarprod(vec.unity(vvdelta), -aatm)
			agrav = self.body.accel(r)
			vagrav = vec.scalarprod(vec.unity(vr), -agrav)
			vatot = vec.sum(vaatm, vagrav)
			vdv = vec.scalarprod(vatot, timestep)
			vdr = vec.scalarprod(vv, timestep)
			vv = vec.sum(vdv, vv)
			vr = vec.sum(vdr, vr)

			print("h: " + diststr(r - self.body.radius) + ", agrav: " + str(agrav) + ", aatm: " + str(aatm) + ", v: " + str(vec.abs(vvdelta)) + ", espec: " + str(vec.abs(vv)**2 - self.body.mu()/r))

		print("Exit position: " + vec.tostr(vr, diststr))
		print("Exit velocity: " + vec.tostr(vv, velstr))

		#TODO calculate orbital elements fro vv, vr
		#TODO orbit does not even sink to its periapsis
		#even worse, it _rises above its apoapsis_
		#must be an error with the rvvector() and vvector() equations...
