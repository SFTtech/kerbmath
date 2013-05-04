from math import *
import itertools
inf = float("+inf")
nan = float("NaN")

class Container:
	"""
	provides convenient access to a dict
	"""
	def __init__(self, d, delonget = False, dbg = True):
		"""
		d
			value dict
		delonget
			auto-delete values when they are queried
		dbg
			display debug messages for each access
		"""
		self._dbg = dbg
		self._vals = d
		self._delonget = delonget

	def __getattr__(self, name):
		"""
		return a val, or raise AttributeError if it does not exist
		if delonget is True, delete the val

		name
			value name
		returns
			value
		"""
		if name in self._vals:
			result = self._vals[name]
			if self._delonget:
				del self._vals[name]
			if self._dbg:
				print("getattr(" + name + "): " + str(result))
			return result
		else:
			if self._dbg:
				print("getattr(" + name + "): FAIL")
			raise AttributeError("No such value: " + name)

	def __delattr__(self, name):
		"""
		delete a val

		name
			value name
		"""
		self._vals.remove(name)

	def __setattr__(self, name, val):
		"""
		set a new/overwrite an existing val

		name
			value name
		val
			value
		"""
		if name[0] == '_':
			self.__dict__[name] = val
		else:
			self._vals[name] = val
		if self._dbg:
			print("setattr(" + name + ", " + str(val) + ")")

	def __len__(self):
		"""
		get the number of vals
		"""
		return len(self._vals)

	def vallist(self, *names):
		"""
		get the names of values

		*names
			if any are passed, they are filtered
			if none are passed, all val names are returned

		returns
			list of val names
		"""
		if len(names) == 0:
			return [name for name in self._vals]
		else:
			return [name for name in names if name in self._vals]

def colprint(msg, col):
	"""
	print colored text

	msg
		any string (or even non-string)
	col
		the ANSI color code
		in the simplest case, an integer such as 32 for green
	"""
	print("\x1b[" + str(col) + "m" + str(msg) + "\x1b[m")

def liststr(l):
	"""
	convert a list to a string
	"""
	if len(l) == 0:
		return ""

	result = ""
	for e in l:
		result += str(e) + ", "

	return result[-2:]

def diststr(dist):
	"""
	convert a distance to a string

	dist
		distance (m)
	returns
		the string
	"""
	if dist < 0:
		return "-" + diststr(-dist)
	elif dist == nan:
		return "NaN"
	elif dist == inf:
		return "inf"
	if dist < 1:
		return "%.4fm"  % (dist / 1)
	elif dist < 100:
		return "%.2fm"  % (dist / 1)
	elif dist < 100e3:
		return "%.2fkm" % (dist / 1e3)
	elif dist < 10000e3:
		return "%.1fkm" % (dist / 1e3)
	elif dist < 1000000e3:
		return "%.0fkm" % (dist / 1e3)
	elif dist < 100e9:
		return "%.2fGM" % (dist / 1e9)
	elif dist < 10000e9:
		return "%.1fGM" % (dist / 1e9)
	else:
		return "%.0fGM" % (dist / 1e9)

def velstr(vel):
	"""
	convert a velocity to a string

	vel
		velocity (m/s)
	returns
		the string
	"""
	if vel < 0:
		return "-" + velstr(-vel)
	elif vel == nan:
		return "NaN"
	elif vel == inf:
		return "inf"
	elif vel < 1:
		return "%.0fmm/s" % (vel / 1e-3)
	elif vel < 100:
		return "%.3fm/s"  % (vel / 1)
	elif vel < 10000:
		return "%.1fm/s"  % (vel / 1)
	elif vel < 1000e3:
		return "%.1fkm/s" % (vel / 1e3)
	else:
		return "%.0fkm/s" % (vel / 1e3)

def interact(globs, banner = None):
	"""
	launch an interactive python console

	globs
		the global variable dict
	banner
		the banner string that is printed
	"""

	#try to read the user's .pyrc file
	try:
		import os
		exec(open(os.environ["PYTHONSTARTUP"]).read(), globs)
	except:
		pass

	def printdocstrings(obj):
		import inspect
		doc = inspect.getdoc(obj)
		if doc == None:
			print("No documentation available")
		else:
			print(doc)

	globs["printdocstrings"] = printdocstrings

	#activate tab completion
	import rlcompleter, readline, code
	readline.parse_and_bind("tab: complete")
	readline.set_completer(rlcompleter.Completer(globs).complete)

	class HelpfulInteractiveConsole(code.InteractiveConsole):
		""""
		Wrapper that will detect trailing '?' characters and try to print docstrings
		"""
		def runsource(self, source, filename="<input>", symbol="single"):
			if len(source) > 1 and source[-1:] == '?':
				#try to display help stuff
				super().runsource("printdocstrings(" + source[:-1] + ")", filename, symbol)
				return False
			else:
				#simply call the super method
				return super().runsource(source, filename, symbol)

	#launch session
	HelpfulInteractiveConsole(globs).interact(banner)
