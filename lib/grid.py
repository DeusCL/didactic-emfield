import pygame as pg


class Grid:
	def __init__(self, app):
		self.app = app

		#style
		self.minor_grid_color = (50, 50, 50)
		self.major_grid_color = (80, 80, 80)
		self.grid_thickness = 1

		self.show = True

	def draw_grid(self, surface, color, scale, x_off, y_off, w, h, line_thickness):
		v_lines = int(w/scale) + 1
		h_lines = int(h/scale) + 1

		for i in range(v_lines):
			x = (i*scale + x_off) % (v_lines*scale)
			pg.draw.line(surface, color, (x, 0), (x, h))

		for j in range(h_lines):
			y = (j*scale + y_off) % (h_lines*scale)
			pg.draw.line(surface, color, (0, y), (w, y))


	def render(self, surface, scale=30, offset_pos=(0, 0)):
		if not self.show: return

		w, h = pg.display.get_window_size()
		x_off, y_off = int(offset_pos[0]), int(offset_pos[1])

		# draw minor grid
		self.draw_grid(
			surface, self.minor_grid_color, scale, x_off, y_off, w, h, 1
		)

		# draw major grid
		self.draw_grid(
			surface, self.major_grid_color, scale*10, x_off, y_off, w, h, 1
		)

		# Main Axis lines
		if 0 <= x_off <= w: 
			pg.draw.line(surface, (150, 150, 150), (x_off, 0), (x_off, h))

		if 0 <= y_off <= h:
			pg.draw.line(surface, (150, 150, 150), (0, y_off), (w, y_off))



