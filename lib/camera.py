import pygame as pg

from . import maths



class Camera:
	def __init__(self, app, pos=(0, 0)):
		self.app = app
		self.pos = pos
		self.smoothness = 1.5
		self.target = None
		self.target_pos = (0, 0)
		self.zoom = 30.0
		self.target_zoom = 30.0

		self.speed = 1

		self.min_zoom = 50


	def handle_event(self, event):
		if event.type == pg.MOUSEWHEEL:
			self.handle_zoom(event.y)


	def handle_zoom(self, wheel_movement):
		win_w, win_h = pg.display.get_window_size()
		cam_x, cam_y = self.pos

		x_off, y_off = cam_x + win_w//2, cam_y + win_h//2
		scale = self.zoom

		focus_x, focus_y = pg.mouse.get_pos()
		tx, ty = self.target_pos

		if wheel_movement > 0:
			self.target_zoom *= 1.3

			dx = ((focus_x-x_off) / scale) - ((focus_x-x_off) / (scale*1.3))
			dy = ((focus_y-y_off) / scale) - ((focus_y-y_off) / (scale*1.3))

			self.target_pos = tx - dx*self.target_zoom, ty - dy*self.target_zoom

		else:
			if self.target_zoom <= self.min_zoom:
				return

			self.target_zoom = max(self.target_zoom/1.3, self.min_zoom)

			dx = ((focus_x-x_off) / scale) - ((focus_x-x_off) / max(scale/1.3, self.min_zoom))
			dy = ((focus_y-y_off) / scale) - ((focus_y-y_off) / max(scale/1.3, self.min_zoom))

			self.target_pos = tx - dx*self.target_zoom, ty - dy*self.target_zoom


	def update(self, dt=1/60.0):
		# Camera position
		cx, cy = self.pos

		# Target position
		if self.target is not None:
			tx, ty = self.target.pos
			tx, ty = -tx*self.zoom, -ty*self.zoom
		else:
			tx, ty = self.target_pos

		# Camera movement
		cx = maths.smooth_step(cx, tx, self.smoothness, dt)
		cy = maths.smooth_step(cy, ty, self.smoothness, dt)

		# Update camera position
		self.pos = (cx, cy)

		# Update camera zoom
		self.target_zoom = max(self.min_zoom, self.target_zoom)
		self.zoom = maths.smooth_step(self.zoom, self.target_zoom, self.smoothness)


