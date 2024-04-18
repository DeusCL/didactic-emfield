import math
import struct

from settings import *
from numba import njit

def normalize_vector(vector, magnitude):
	if vector is None:
		return None

	#magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2)

	if magnitude < 10e-23:
		return None  # El vector nulo no puede normalizarse

	return vector[0] / magnitude, vector[1] / magnitude



def scale_vector(vector, factor):
	return [vector[0]*factor, vector[1]*factor]


def smooth_step(start_value, target_value, smoothness=10, dt=1/60.0):
	return start_value + (target_value-start_value)*(10/smoothness)*dt

def dist(p1, p2):
	return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)



def calc_electric_field(charges, px, py):
	sum_E = [0, 0]

	for charge in charges:
		vr = px-charge.pos[0], py-charge.pos[1]
		r = math.sqrt(vr[0]**2 + vr[1]**2)
		if r < 0.1: return None
		vr = vr[0]/r, vr[1]/r
		pre_E = (9e-9*charge.charge*(10**-6))/(r**3)
		sum_E = sum_E[0] + pre_E*vr[0], sum_E[1] + pre_E*vr[1]

	return sum_E


def Q_sqrt_c_bad(x):
	"""
	Fast inverse square root algorithm cubed.
	"""
	# Convert the input to 32-bit floating point representation
	x = float(x)
	# Convert the bits of the floating-point number into an integer
	i = 0x5f3759df - (x >> 1)
	# Convert the integer back to floating-point
	y = float(i)
	# Perform one iteration of Newton's method to refine the estimate
	y = y * (1.5 - 0.5 * x * y * y)
	return y*y*y


@njit
def Q_rsqrt_c(number):
	if number == 0:
		return 0
	return 1/math.sqrt(number)**3

@njit
def Q_rsqrt(number):
	if number == 0:
		return 0
	return 1/math.sqrt(number)

@njit
def calc_sum(c, cx, cy, px, py):
	qi = c * (10**-6)
	drx, dry = px-cx, py-cy
	if -0.0000001 < px-cx < 0.0000001 and -0.0000001 < py-cy < 0.0000001:
		return 0, 0
	qsqrt = Q_rsqrt_c(drx**2 + dry**2)
	return qi*drx*qsqrt, qi*dry*qsqrt


@njit
def Q_norm(vect):
	x, y = vect
	rsqrt = Q_rsqrt(x * x + y * y)
	return x*rsqrt, y*rsqrt




"""

E = maths.Q_norm(efield)

w, h = E[0]*scale*ARROW_LENGTH, E[1]*scale*ARROW_LENGTH

cdraw.arrow2(surface, (100, 255, 255, alpha),
	(x-(w/2)*ARROW_CENTERED, y-(h/2)*ARROW_CENTERED),
	(x+w - (w/2)*ARROW_CENTERED, y+h - (h/2)*ARROW_CENTERED)
)

"""


@njit
def Q_arrow(pos, vect, scale):
	x, y = pos
	vx, vy = vect
	rsqrt = Q_rsqrt(vx * vx + vy * vy)
	w, h = vx*rsqrt*scale*ARROW_LENGTH, vy*rsqrt*scale*ARROW_LENGTH
	return (x - w/2, y - h/2), (x + w/2, y + h/2)


@njit
def Q_alpha(vect):
	x, y = vect
	return min(255, 255*math.sqrt(x*x + y*y)/8990)


def calc_E(charges, px, py):
	sum_E = 0, 0

	for c in charges:
		sx, sy = calc_sum(c.charge, c.pos[0], c.pos[1], px, py)
		if (sx, sy) == (0, 0): return (0, 0), 0
		sum_E = sum_E[0] + sx, sum_E[1] + sy

	sum_E = K*sum_E[0], K*sum_E[1]

	return sum_E, Q_alpha(sum_E)


@njit
def get_dist(start_pos, end_pos):
	x, y = start_pos
	px, py = end_pos

	dx, dy = px-x, py-y

	return math.sqrt(dx**2 + dy**2)



@njit(fastmath=True)
def calc_arrow_points(spos, epos, arrow_size):
	angle = math.atan2(epos[1] - spos[1], epos[0] - spos[0])

	p1 = (
		epos[0] - arrow_size * math.cos(angle - math.pi / 6),
		epos[1] - arrow_size * math.sin(angle - math.pi / 6)
	)

	p2 = (
		epos[0] - arrow_size * math.cos(angle + math.pi / 6),
		epos[1] - arrow_size * math.sin(angle + math.pi / 6)
	)

	return p1, p2





