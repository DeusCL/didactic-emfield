import pygame as pg
import custom_draw as cdraw

import maths
import math

import sys

import numpy as np

from settings import *


class Field:
	def __init__(self, app, scene):
		self.app = app
		self.scene = scene

		self.vectors_head_size = 10


	def render(self, surface, scale, offset_pos):
		w, h = pg.display.get_window_size()
		x_off, y_off = int(offset_pos[0]), int(offset_pos[1])



		spread_scale = scale*ARROW_SPREAD
		scale2 = scale

		self.scene.camera.speed = 1

		while spread_scale > 150:
			spread_scale /= 4
			scale2 /= 4
			self.scene.camera.speed /= 4

		#ss2 = scale
		#print(f"{spread_scale=:.2f}  {scale=:.2f} {ss2=:.2f}")

		x_points = int(w/spread_scale) + 3
		y_points = int(h/spread_scale) + 3


		for i in range(x_points):
			x = ((i*spread_scale + x_off) % (x_points*spread_scale)) - spread_scale
			px = (x-x_off)/scale

			for j in range(y_points):
				y = ((j*spread_scale + y_off) % (y_points*spread_scale)) - spread_scale
				py = (y-y_off)/scale

				efield, alpha = maths.calc_E(self.scene.charges + self.scene.particles, px, py)

				if alpha < 5 or efield == (0, 0):
					continue

				s_pos, e_pos = maths.Q_arrow((x, y), efield, scale2)

				cdraw.arrow2(surface, (100, 255, 255, alpha), s_pos, e_pos)

