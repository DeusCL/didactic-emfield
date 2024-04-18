import pygame as pg

from . import maths
from . import custom_draw as cdraw

from settings import *



class CargaLibre:
	def __init__(self, scene, pos, charge):
		self.pos = pos
		self.scene = scene
		self.size = 0.000001
		self.vel = 0, 0
		self.charge = charge
		self.F = 0, 0


	def get_size(self, scale):
		return max(6, scale*self.size)


	def update(self, dt):
		x, y = self.pos
		vx, vy = self.vel

		speed = self.scene.camera.speed

		self.pos = x + dt*vx*speed, y + dt*vy*speed

		prtls = list(set(self.scene.particles + self.scene.charges) - {self})

		E, alpha = maths.calc_E(prtls, x, y)
		self.F = E[0]*self.charge * 10**-6, E[1]*self.charge * 10**-6

		mag = alpha/255
		nx, ny = maths.Q_norm(self.F)

		self.vel = vx + nx*mag*speed*dt, vy + ny*mag*speed*dt

		self.vel = self.vel[0] - self.vel[0]*0.001*speed*dt, self.vel[1] - self.vel[1]*0.001*speed*dt



	def render(self, surface, scale, offset_pos):
		x, y = self.pos[0]*scale + offset_pos[0], self.pos[1]*scale + offset_pos[1]

		px, py = self.pos

		rscale = 1000

		if self.F != (0, 0):
			w, h = min(1000, self.F[0]*scale*rscale), min(1000, self.F[1]*scale*rscale)

			s_pos = x, y
			e_pos = x + w, y + h

			cdraw.arrow(surface, (170, 255, 170), s_pos, e_pos, 15)


		draw_color = (255,166,255)*(self.charge>0) + (166, 255, 255)*(self.charge<0) + (255,)*3*(self.charge==0)
		size = self.get_size(scale)
		pg.draw.circle(surface, draw_color, (x, y), size)




class Carga:
	def __init__(self, pos, charge=-10):
		self.pos = pos
		self.charge = charge
		self.size = 0.000001
		self.electric_field = 0, 0


	def get_size(self, scale):
		return max(6, scale*self.size)


	def render(self, surface, scale, offset_pos):
		x, y = self.pos[0]*scale + offset_pos[0], self.pos[1]*scale + offset_pos[1]

		if self.charge > 0:
			draw_color = (255, 0, 0, 255)
		elif self.charge < 0:
			draw_color = (0, 0, 255, 255)
		else:
			draw_color = (255, 255, 255, 255)

		size = self.get_size(scale)

		pg.draw.circle(surface, draw_color, (x, y), size)



class Sensor(Carga):
	def __init__(self, pos):
		super().__init__(pos, 0)

		self.size = 0.1
		self.scene = None
		self.magnitude = 0


	def render(self, surface, scale, offset_pos):
		x, y = self.pos[0]*scale + offset_pos[0], self.pos[1]*scale + offset_pos[1]
		px, py = self.pos

		self.electric_field, alpha = maths.calc_E(self.scene.charges, px, py)

		E = self.electric_field
		rscale = 1000

		if E is not None:
			w, h = min(1000, E[0]*scale/rscale), min(1000, E[1]*scale/rscale)

			s_pos = x, y
			e_pos = x + w, y + h

			cdraw.arrow(surface, (170, 255, 170), s_pos, e_pos, 15)

		pg.draw.circle(surface, (170, 255, 170), (x, y), 9)


