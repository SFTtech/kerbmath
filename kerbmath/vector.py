from math import *

def tostr(vec, fun = str):
	"""
	vec          3-dimensional vector (x, y, z)
	fun          string conversion function for the elements
	returns      appropriate string, including the absolute value
	"""
	return "(x=" + fun(vec[0]) + ", y=" + fun(vec[1]) + ", z=" + fun(vec[2]) + ", abs=" + fun(abs(vec)) + ")"

def sum(vec0, vec1):
	"""
	vec0         3-dimensional vector
	vec1         3-dimensional vector
	returns      vec0 + vec1
	"""
	return (vec0[0] + vec1[0], vec0[1] + vec1[1], vec0[2] + vec1[2])

def diff(vec0, vec1):
	"""
	vec0         3-dimensional vector
	vec1         3-dimensional vector
	returns      vec0 - vec1
	"""
	return (vec0[0] - vec1[0], vec0[1] - vec1[1], vec0[2] - vec1[2])

def scalarprod(vec, scalar):
	"""
	vec          3-dimensional vector
	scalar       scalar
        returns      vec * scalar
	"""
	return (vec[0] * scalar, vec[1] * scalar, vec[2] * scalar)

def abs(vec):
	"""
	vec          3-dimensional vector
	returns      |vec|
	"""
	return sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])

def unity(vec):
	"""
	vec          3-dimensional vector
	returns      vec/|vec|
	"""
	return scalarprod(vec, 1/abs(vec))
