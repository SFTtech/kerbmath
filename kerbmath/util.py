inf = float("+inf")

def colprint(msg, col):
	"""
	msg:          any string (or even non-string)
	col:          the ANSI color code, excluding the starting \\e[ and the finalizing m
		      in the simplest case, an integer such as 32 for green.
	"""
	print("\x1b[" + str(col) + "m" + str(msg) + "\x1b[m")

def diststr(dist):
	"""
	dist:         distance (m)
	returns:      an appropriate string. in a wide range, km will be used as unit 
	"""
	if dist < 0:
		return "-" + diststr(-dist)
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

def interact(globs, banner = None):
	"""
	launch a interactive python console

	globs      the global variable dict
	
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
