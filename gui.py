import pygame as pg

from settings import *


class Widget:
	def __init__(self, guim, pos):
		self.guim = guim
		self.app = guim.app
		self.scene = guim.app.scene

		self.padding = (0, 0)
		self.offset = (0, 0)

		self.in_dialog = False

		self._pos = pos


	def handle_event(self, event):
		pass

	def update(self):
		pass

	def render(self, surface, offset=None):
		pass


	@property
	def pos(self):
		ox, oy = self.offset
		px, py = self.padding
		x, y = self._pos
		return x + px + ox, y + py + oy

	@property
	def x(self):
		return self.pos[0]

	@x.setter
	def x(self, new_x):
		self._pos = new_x, self._pos[1]

	@property
	def y(self):
		return self.pos[1]

	@y.setter
	def y(self, new_y):
		self._pos = self._pos[0], new_y



class Dialog:
	def __init__(self, app, title, elements):
		self.app = app

		self.padding = 15, 15

		self.title_label = Label(
			app, (0, 0), title, True, ORANGE,
			pg.font.Font(FONT_2, 18)
		)

		self.elements = elements

		self.organize()


	def organize(self):
		if len(self.elements) == 0:
			return

		most_right = 0
		most_bottom = 0

		for element in self.elements:
			element.in_dialog = True

			w, h = element.size

			if element.x + w > most_right:
				most_right = element.x + w

			if element.y + h > most_bottom:
				most_bottom = element.y + h

		title_width = self.title_label.size[0] + 2*self.padding[0]
		title_height = self.title_label.size[1] + self.padding[1]

		total_width = max(title_width, most_right + 2*self.padding[0])
		total_height = max(1, most_bottom + 2*self.padding[1]) + title_height

		self.surface = pg.Surface(
			(total_width, total_height)
		).convert_alpha()

		self.surface.fill((0, 0, 0, 0))


	def handle_event(self, event):
		for element in self.elements:
			element.handle_event(event)


	def update(self):
		for element in self.elements:
			element.update()


	def render(self, surface):
		size = self.surface.get_size()

		title_height = self.title_label.size[1] + self.padding[1]

		# Draw the background
		pg.draw.rect(self.surface, DARK_GRAY_2, (0, 0, *size), 0, 10)

		# Draw the title
		self.title_label.render(self.surface, self.padding)

		# Blit the surface to the destination surface
		w, h = pg.display.get_window_size()
		pos = w//2 - size[0]//2, h//2 - size[1]//2
		surface.blit(self.surface, pos)

		# Draw elements
		padding = self.padding[0], self.padding[1] + title_height
		for element in self.elements:
			element.padding = padding
			element.offset = pos
			element.render(surface)



class Label(Widget):
	def __init__(self, guim, pos, text, antialiasing, color, font=None):
		super().__init__(guim, pos)
		self._text = text
		self._color = color
		self._antialiasing = antialiasing
		self._font = pg.font.SysFont("Consolas", 16) if font is None else font

		self.render_text(text, antialiasing, color)


	@property
	def size(self):
		return self.text_surf.get_size()


	@property
	def text(self):
		return self._text

	@text.setter
	def text(self, new_text):
		if self._text == new_text:
			return

		self._text = new_text
		self.render_text(new_text, self.antialiasing, self.color)


	@property
	def color(self):
		return self._color

	@color.setter
	def color(self, color):
		self._color = color
		self.render_text(self.text, self.antialiasing, color)


	@property
	def antialiasing(self):
		return self._antialiasing

	@antialiasing.setter
	def antialiasing(self, value):
		self._antialiasing = value
		self.render_text(self.text, value, self.color)


	@property
	def font(self):
		return self._font

	@font.setter
	def font(self, font_obj):
		self._font = font_obj
		self.render_text(self.text, self.antialiasing, self.color)


	def render_text(self, text, aa, color):
		self.text_surf = self.font.render(text, aa, color)


	def render(self, surface, offset=None):
		pos = self.pos

		if offset is not None:
			pos = pos[0] + offset[0], pos[1] + offset[1]

		surface.blit(self.text_surf, pos)



class Button(Widget):
	def __init__(self, app, pos, size, text):
		super().__init__(app, pos)

		self.size = size
		self.label = Label(app, (0, 0), text, True, COLOR_TEXT)

		self.text = self.label.text

		self.hovering = False
		self.pressing = False

		self.img = None

		self.on_pressed = None
		self.on_pressed_args = ()


	def check_hovering(self):
		cnd1 = self.scene.grabbed
		cnd2 = self.scene.particle_grabbed is not None
		cnd3 = self.guim.dialog_to_show is not None

		if self.in_dialog:
			cnd3 = False

		if cnd1 or cnd2 or cnd3:
			self.hovering = False
			return

		mx, my = pg.mouse.get_pos()
		w, h = self.size

		h_hovering = mx >= self.x and mx <= self.x + w
		v_hovering = my >= self.y and my <= self.y + h

		self.hovering = h_hovering and v_hovering

		if self.hovering:
			self.app.current_cursor = CURSOR_HAND_FINGER
			self.scene.controls_active = False


	def handle_event(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1 and self.hovering:
				self.pressing = True

		elif event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				if self.pressing and self.hovering:
					# This button really got pressed and released
					if self.on_pressed is not None:
						self.on_pressed(*self.on_pressed_args)

				self.pressing = False


	def update(self):
		self.check_hovering()


	def render(self, surface):
		# Adjust the color
		color = COLOR_BG_2
		outline_color = COLOR_OUTLINE_1
		if self.hovering:
			outline_color = COLOR_OUTLINE_2
			if self.pressing:
				color = COLOR_BG_1

		# Render the button
		w, h = self.size
		pg.draw.rect(surface, color, (*self.pos, w, h), 0, 5)
		pg.draw.rect(surface, outline_color, (*self.pos, w, h), 1, 5)

		# Render the label
		lw, lh = self.label.size
		lpos = self.pos[0] + w//2 - lw//2, self.pos[1] + h//2 - lh//2 + 2
		self.label.render(surface, lpos)

		# Blit the img if any
		if self.img is not None:
			iw, ih = self.img.get_size()
			ipos = self.pos[0] + w//2 - iw//2, self.pos[1] + h//2 - ih//2
			surface.blit(self.img, ipos)




