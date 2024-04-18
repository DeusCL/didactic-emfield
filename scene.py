import os
import pygame as pg

from grid import Grid
from camera import Camera
from field import Field

import random
import math
import maths

from settings import *
from particle import *


class Scene:
	def __init__(self, app):
		self.app = app

		self.charges = list()
		self.sensors = list()
		self.particles = list()

		self.camera = Camera(app)
		self.guim = None

		self.grid = Grid(app)
		self.field = Field(app, self)

		self.current_scene = None
		self.pause = 1

		self.offset = 0, 0
		self.grabbed = False
		self.grabbed_pos = (0, 0)

		self.shifting = False

		self.particle_grabbed = None
		self.particle_grabbed_offset = (0, 0)

		self.last_grabbed_particle = None

		self.controls_active = True


	def save(self, textfield):
		filename = f"{textfield.text}.py"
		filepath = SCENES_DIR / filename

		try:
			f = open(filepath, 'w')
		except:
			return False, "Error guardando la escena, nombre inválido."

		f.write("from particle import Carga, Sensor\n\n")
		for c in self.charges:
			x, y = c.pos
			f.write(f"add(Carga(({x}, {y}), {c.charge}))\n")
		f.close()

		return True, "Escena guardada correctamente."


	def add(self, prtl):
		if prtl.charge != 0:
			self.charges.append(prtl)
			print(f"\tCarga de {prtl.charge}μC añadida a la escena.")
		else:
			prtl.scene = self
			self.sensors.append(prtl)
			print(f"\tPunto añadido a la escena.")


	def reload(self):
		self.charges = list()
		self.sensors = list()

		self.load(self.current_scene)
		self.pause = 1


	def handle_event(self, event):
		if self.controls_active == False:
			return

		if event.type == pg.KEYDOWN:
			if event.key == pg.K_o:
				self.camera.target_pos = 0, 0
				self.camera.target_zoom = 70

			if event.key == pg.K_DELETE:
				self.remove_the_selected()

			if event.key == pg.K_k:
				q1 = CargaLibre(self, (random.uniform(-5, 5), random.uniform(-5, 5)), random.uniform(-2, 2))
				q1.vel = 0, 0
				#q2 = CargaLibre(self, (5, 0), 1)
				#q2.vel = 0, -1

				self.particles.append(q1)
				#self.particles.append(q2)



		self.camera.handle_event(event)


	def remove_the_selected(self):
		if self.last_grabbed_particle is None:
			return

		try:
			self.sensors.remove(self.last_grabbed_particle)
		except ValueError:
			pass

		try:
			self.charges.remove(self.last_grabbed_particle)
		except ValueError:
			pass

		self.last_grabbed_particle = None


	def load(self, scene_file):
		print(f"Loading \"{scene_file}\"...\n")
		add = self.add
		cam = self.camera
		app = self.app
		field = self.field
		grid = self.grid

		if os.path.exists(scene_file):
			with open(scene_file, 'r') as file:
				exec(file.read())
		print(f"\n\"{scene_file}\" load finished.")

		self.current_scene = scene_file


	def get_rel_pos(self, pos):
		w, h = pg.display.get_window_size()
		cam_pos = self.camera.pos

		x_off, y_off = cam_pos[0] + w//2, cam_pos[1] + h//2

		return (pos[0]*self.camera.zoom + x_off, pos[1]*self.camera.zoom + y_off)


	def move_charges(self):
		if self.controls_active == False: return
		if self.grabbed == True: return

		w, h = pg.display.get_window_size()
		cam_pos = self.camera.pos
		scale = self.camera.zoom

		x_off, y_off = cam_pos[0] + w//2, cam_pos[1] + h//2

		mx, my = pg.mouse.get_pos()

		left_clicking = pg.mouse.get_pressed()[0]
		keys = pg.key.get_pressed()


		if self.particle_grabbed is not None:
			if left_clicking:
				self.app.current_cursor = CURSOR_HAND_CLOSED

				ox, oy = self.particle_grabbed_offset
				grabbed_pos = (mx - x_off)/scale + ox, (my - y_off)/scale + oy

				if self.shifting:
					grabbed_pos = round(grabbed_pos[0]), round(grabbed_pos[1])

				self.particle_grabbed.pos = grabbed_pos

			else:
				if keys[pg.K_LCTRL]:
					print("Dropped with clamps")
					x, y = self.particle_grabbed.pos
					clamp_pos = round(x), round(y)
					self.particle_grabbed.pos = clamp_pos

				self.last_grabbed_particle = self.particle_grabbed
				self.particle_grabbed = None


		if self.particle_grabbed is None:
			for charge in self.charges + self.sensors:
				x, y = self.get_rel_pos(charge.pos)
				if maths.get_dist((x, y), (mx, my)) <= charge.get_size(self.camera.zoom) + 5:
					self.app.current_cursor = CURSOR_HAND_OPEN
					if left_clicking:
						mx, my = (mx - x_off)/scale , (my - y_off)/scale
						x, y = charge.pos
						self.particle_grabbed = charge
						self.particle_grabbed_offset = x - mx, y - my
						break




	def check_controls(self):
		if self.controls_active == False:
			return

		keys = pg.key.get_pressed()

		mx, my = pg.mouse.get_pos()

		self.shifting = keys[pg.K_LSHIFT]

		if keys[pg.K_SPACE]:
			if pg.mouse.get_pressed()[0]:
				if not self.grabbed:
					self.grabbed = True
					self.grabbed_pos = mx, my
			else:
				self.grabbed = False
		else:
			self.grabbed = False


		if self.grabbed:
			gpx, gpy = self.grabbed_pos
			self.camera.target_pos = self.offset[0] + (mx-gpx), self.offset[1] + (my-gpy)

		else:
			self.offset = self.camera.target_pos

		self.move_charges()


	def update(self):
		self.camera.update()
		self.check_controls()

		for particle in self.particles:
			particle.update(self.app.dt)


	def render(self, window, surface):
		w, h = pg.display.get_window_size()
		cam_pos = self.camera.pos

		offset_pos = cam_pos[0] + w//2, cam_pos[1] + h//2

		self.grid.render(window, self.camera.zoom, offset_pos)

		#if self.camera.zoom < 70000:
		self.field.render(surface, self.camera.zoom, offset_pos)

		for charge in self.charges:
			charge.render(surface, self.camera.zoom, offset_pos)

		for sensor in self.sensors:
			sensor.render(surface, self.camera.zoom, offset_pos)

		for particle in self.particles:
			particle.render(surface, self.camera.zoom, offset_pos)
