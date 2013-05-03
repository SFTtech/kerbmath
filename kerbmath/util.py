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
