import pygame as pg
import pyperclip

from .gui import Widget

from settings import *



class TextField(Widget):
	def __init__(self, guim, pos, size, caption="", dtype=str,
		verificator=None):

		"""
		Initialize the TextField object.

		This class requires:
			import pygame as pg
			import pyperclip


		Args:
			app (pygame.Surface): The Pygame application surface.
			pos (tuple): The position of the text field (x, y).
			size (tuple): The size of the text field (width, height).
		"""

		super().__init__(guim, pos)

		#self.app = app
		#self.padding = 0, 0

		self.font = pg.font.SysFont("Consolas", 16)

		#self.pos = pos
		self.size = size

		self.dtype = dtype
		self.invalid_value = False
		self.verificator = None

		self.caption = ""
		self.caption_surf = self.render_caption(caption)

		self.border_radius = 5
		self.cursor_xpos = 0
		self.cursor_time = 0
		self.cursor_bwpos = 0

		self.left_time = 0
		self.right_time = 0

		self.backspace_time = 0
		self.delete_time = 0

		self.focused = False

		self.text = ""
		self.textsurf = self.render_textsurf()


		self.surface = self.render_surf()


		self.mholding = False
		self.shifting = False
		self.selection = [-1, -1]

		self.on_type = None

		#double click check
		self.last_click_time = 0
		self.last_click_pos = (0, 0)


	def render_caption(self, caption):
		if caption.strip() == "": return None
		if caption == self.caption: return self.caption_surf
		self.caption = caption
		return self.font.render(caption, True, WHITE)


	def render_textsurf(self):
		""" Create a surface for rendering text. """

		surface = pg.Surface(self.size).convert_alpha()
		surface.fill((0, 0, 0, 0))
		return surface


	def render_surf(self):
		"""
		Render the text field surface.

		Returns:
			pygame.Surface: The surface representing the text field.
		"""

		surface = pg.Surface(self.size).convert_alpha()
		surface.fill((0, 0, 0, 0))

		# Draw a border rounded filled rectangle
		pg.draw.rect(
			surface, GRAY,
			(0, 0, *self.size),
			0, *((self.border_radius,)*4)
		)

		return surface


	def draw_cursor(self, surface):
		"""
		Draw the text cursor on the surface.

		Args:
			surface (pygame.Surface): The surface to draw the cursor on.
		"""

		# A cool way to make the cursor blink periodically
		time = self.app.time - self.cursor_time
		period = 1.2

		if (time%period) > period*0.5:
			return

		# Cursor positioning
		x, y = self.pos

		cursor_height = int(self.size[1]*0.8)
		cursor_x_offset = 10 + self.cursor_xpos
		cursor_y_offset = (self.size[1] - cursor_height)//2
		start_pos = x+cursor_x_offset, y+cursor_y_offset
		end_pos = x+cursor_x_offset, start_pos[1]+cursor_height

		# Draw the cursor with a line
		pg.draw.line(surface, ORANGE, start_pos, end_pos, 2)


	def move_cursor(self, _dir = "left"):
		tlen = len(self.text)

		if _dir == "left":
			bwpos = min(tlen, self.cursor_bwpos+1)
		elif _dir == "right":
			bwpos = max(0, self.cursor_bwpos-1)
		elif _dir == "up":
			bwpos = len(self.text)
		elif _dir == "down":
			bwpos = 0

		if self.shifting:
			self.selection[1] = tlen - bwpos

		else:
			# If there is something selected
			if self.selection[0] != self.selection[1]:

				if _dir == "left":
					bwpos = tlen - min(self.selection)
				elif _dir == "right":
					bwpos = tlen - max(self.selection)

				self.selection = [-1, -1]



		self.cursor_bwpos = bwpos

		self.update_cursor_pos()


	def delete_text(self, k_delete=False):
		if self.text == "":
			return

		si, sf = self.get_selpos()

		if si != sf:
			text = self.text
			self.text = text[:si] + text[sf:]
			self.selection = [-1, -1]
			self.update_text_surf()
			self.cursor_bwpos = len(self.text) - si
			self.update_cursor_pos()
			return

		if self.cursor_bwpos == 0:
			if k_delete:
				return

			self.text = self.text[:-1]
		else:
			text = self.text
			cpos = len(text) - self.cursor_bwpos

			if not k_delete:
				if cpos == 0:
					return
				self.text = text[:cpos-1] + text[cpos:]

			else:
				self.text = text[:cpos] + text[cpos+1:]
				self.cursor_bwpos -= 1

		self.update_text_surf()


	def get_postext(self, pos):
		unit, _ = self.font.size('u')

		x, _ = pos

		rpos = round(max(0, x - self.pos[0] - 10)/unit)
		return max(0, len(self.text) - rpos)


	def get_selpos(self):
		selx, sely = self.selection
		return min(selx, sely), max(selx, sely)


	def double_clicked(self, event):
		if self.app.time - self.last_click_time < 0.6 and self.last_click_pos == event.pos:
			# Double clicked!
			self.last_click_time = 0
			self.selection = [0, len(self.text)]
			self.cursor_bwpos = 0
			self.update_cursor_pos()

			return True

		self.last_click_pos = event.pos
		self.last_click_time = self.app.time

		return False


	def handle_event(self, event):
		"""
		Handle Pygame events for the text field.

		Args:
			event (pygame.event.Event): The Pygame event to handle.
		"""

		# If the text field is clicked, then, its focused
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				self.focused = self.hovering

				if self.cursor_time == 0 and self.focused:
					self.cursor_time = self.app.time
				else:
					self.cursor_time = 0
					if not self.hovering:
						self.selection = [-1, -1]

				if self.hovering:
					if self.double_clicked(event):
						return

					bwpos = self.get_postext(event.pos)
					self.cursor_bwpos = bwpos

					self.mholding = True
					self.selection[0] = len(self.text) - bwpos

					self.update_cursor_pos()



		if event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				self.mholding = False


		# If the main window lost focus, then, the text field isn't focused
		# anymore
		if event.type == pg.ACTIVEEVENT:
			if not event.gain and event.state == 2:
				self.focused = False

		if event.type == pg.KEYDOWN and self.focused:

			key = pg.key.get_pressed()


			if event.key == pg.K_LEFT:
				self.left_time = self.app.time
				self.move_cursor("left")

			if event.key == pg.K_RIGHT:
				self.right_time = self.app.time
				self.move_cursor("right")

			if event.key == pg.K_UP:
				self.move_cursor("up")


			if event.key == pg.K_DOWN:
				self.move_cursor("down")


			if event.key in [pg.K_LSHIFT, pg.K_RSHIFT]:
				self.shifting = True

				si, sf = self.get_selpos()
				
				if si == sf:
					self.selection[0] = len(self.text) - self.cursor_bwpos
					self.selection[1] = len(self.text) - self.cursor_bwpos

			if event.key == pg.K_BACKSPACE:
				self.backspace_time = self.app.time
				self.delete_text()


			elif event.key == pg.K_c and (key[pg.K_LCTRL] or key[pg.K_RCTRL]):
				si, sf = self.get_selpos()
				
				if si == sf:
					pyperclip.copy("")

				else:
					pyperclip.copy(self.text[si:sf])



			elif event.key == pg.K_x and (key[pg.K_LCTRL] or key[pg.K_RCTRL]):
				si, sf = self.get_selpos()
				
				if si == sf:
					pyperclip.copy("")

				else:
					pyperclip.copy(self.text[si:sf])
					self.delete_text()



			elif event.key == pg.K_v and (key[pg.K_LCTRL] or key[pg.K_RCTRL]):
				si, sf = self.get_selpos()

				cv = pyperclip.paste()

				if cv == "":
					return

				# If the selection isnt empty
				if si != sf:
					# Replace the selected text with the clipboard value
					text = self.text

					self.text = text[:si] + cv + text[sf:]
					self.selection = [-1, -1]

					# Adjust the position of the cursor one unit to the right
					# of the left part of the selection
					self.cursor_bwpos = (len(self.text) - si)-len(cv)

				else:
					# If the cursor position is in the end of the text
					if self.cursor_bwpos == 0:
						# Then do a normal unicode addition
						self.text += cv

					# If the cursor is in another position
					else:
						# Then put the unicode in the position of the cursor
						text = self.text
						cpos = len(text) - self.cursor_bwpos
						self.text = text[:cpos] + cv + text[cpos:]

				self.update_text_surf()


			elif event.key == pg.K_DELETE:
				self.delete_time = self.app.time
				self.delete_text(k_delete=True)


			elif event.key in (pg.K_RETURN, pg.K_KP_ENTER):
				print(f"Text: {self.text}")

			else:
				c = event.unicode

				if c == "": return

				if self.dtype == int:
					if not c in "-0123456789e":
						return

					# Only one e allowed in this type of field
					if c == "e" and "e" in self.text:
						return

				if self.dtype == float:
					if not c in "-0.123456789e":
						return

					# Only one period allowed in this type of field
					if c == "." and "." in self.text:
						return

					# Only one minus sign allowed in this type of field
					# and must be at the begining
					if c == "-" and "-" in self.text:
						if self.text[-1] != "e":
							return

					# Only one e allowed in this type of field
					if c == "e" and "e" in self.text:
						return

				# Get the ordered positions of the current selection
				# si = most left part of the selection
				# sf = most right part of the selection
				si, sf = self.get_selpos()

				# If the selection isnt empty
				if si != sf:
					# Replace the selected text with the typed unicode
					text = self.text
					self.text = text[:si] + event.unicode + text[sf:]
					self.selection = [-1, -1]

					# Adjust the position of the cursor one unit to the right
					# of the left part of the selection
					self.cursor_bwpos = (len(self.text) - si)-1

					self.update_text_surf()

					# Nothing else to do here
					return

				# If the cursor position is in the end of the text
				if self.cursor_bwpos == 0:
					# Then do a normal unicode addition
					self.text += event.unicode

				# If the cursor is in another position
				else:
					# Then put the unicode in the position of the cursor
					text = self.text
					cpos = len(text) - self.cursor_bwpos
					self.text = text[:cpos] + c + text[cpos:]

				self.update_text_surf()


		if event.type == pg.KEYUP:
			if event.key == pg.K_DELETE:
				self.delete_time = 0

			if event.key == pg.K_BACKSPACE:
				self.backspace_time = 0

			if event.key == pg.K_LEFT:
				self.left_time = 0

			if event.key == pg.K_RIGHT:
				self.right_time = 0

			if event.key in [pg.K_LSHIFT, pg.K_RSHIFT]:
				self.shifting = False


	def update_text_surf(self):
		""" Update the text surface with the current text. """

		# Check if this field have a valid value

		try:
			if self.text != "":
				number = self.dtype(self.text)
		except ValueError as e:
			self.invalid_value = True
		else:
			self.invalid_value = False


		if self.verificator is not None:
			self.invalid_value = not self.verificator(self.text)


		self.textsurf.fill((0, 0, 0, 0))
		w, h = self.textsurf.get_size()

		rendered_text_surf = self.font.render(self.text, True, WHITE)
		tw, th = rendered_text_surf.get_size()

		self.textsurf.blit(rendered_text_surf, (10, h/2 - th/2))

		self.update_cursor_pos()

		# Callback function
		if self.on_type is not None:
			self.on_type(self.text)


	def update_cursor_pos(self):
		self.cursor_time = self.app.time

		if self.cursor_bwpos == 0:
			cpos, _ = self.font.size(self.text)
		else:
			cpos, _ = self.font.size(self.text[:-self.cursor_bwpos])

		self.cursor_xpos = cpos


	def check_mouse(self):
		""" Check if the mouse is hovering over the text field. """

		mx, my = pg.mouse.get_pos()
		(x, y), (w, h) = self.pos, self.size

		# Update the state of the hovering attribute
		self.hovering = (x <= mx <= x + w) and (y <= my <= y + h)

		# Change the cursor when hovering the text field
		if self.hovering:
			self.app.current_cursor = CURSOR_TEXT_MARKER


	def update(self):
		""" Update the text field. """
		self.check_mouse()

		if self.mholding:
			bwpos = self.get_postext(pg.mouse.get_pos())
			self.selection[1] = len(self.text) - bwpos

			self.cursor_bwpos = bwpos
			self.update_cursor_pos()

			self.app.current_cursor = CURSOR_TEXT_MARKER


		# A cool way to delete letters when holding backspace
		if self.backspace_time > 0:
			if self.app.time - self.backspace_time > 0.5:
				self.delete_text()

		# A cool way to forward delete letters when holding delete
		if self.delete_time > 0:
			if self.app.time - self.delete_time > 0.5:
				self.delete_text(k_delete=True)

		# A cool way to move the cursor to the left when holding left button
		if self.left_time > 0:
			if self.app.time - self.left_time > 0.5:
				self.move_cursor("left")

		# A cool way to move the cursor to the right when holding right button
		if self.right_time > 0:
			if self.app.time - self.right_time > 0.5:
				self.move_cursor("right")


	def get_selection_text(self):
		if self.text == "":
			return ""

		si, sf = min(selx, sely), max(selx, sely)

		if si == sf:
			return ""

		return self.text[si:sf+1]


	def draw_selection(self, surface):
		selx, sely = self.selection

		if selx != sely:
			si, sf = min(selx, sely), max(selx, sely)

			unit, _ = self.font.size("u")
			x, y = self.pos

			ix, iy = x+10 + unit*si, y+2
			w, h = unit*(sf-si), self.size[1]-4

			pg.draw.rect(
				surface, LIGHT_GRAY, (ix, iy, w, h),
				0, *((self.border_radius,)*4)
			)

			pg.draw.rect(
				surface, LIGHT_GRAY2, (ix, iy, w, h),
				1, *((self.border_radius,)*4)
			)


	def render(self, surface):
		self.update()

		surface.blit(self.surface, self.pos)
		self.draw_selection(surface)
		surface.blit(self.textsurf, (self.pos[0], self.pos[1]+2))

		if self.focused:
			# Draw cursor when focused
			self.draw_cursor(surface)

			# Draw a green border when focused
			pg.draw.rect(
				surface, GREEN, (*self.pos, *self.size),
				1, *((self.border_radius,)*4)
			)

		self.caption_surf = self.render_caption(self.caption)

		if self.caption_surf is not None:
			x, y = self.pos
			h = self.caption_surf.get_height()

			surface.blit(self.caption_surf, (x, y - h*1.1))


		# Draw a red border if this field contains an invalid value
		if self.invalid_value:
			pg.draw.rect(
				surface, RED, (*self.pos, *self.size),
				1, *((self.border_radius,)*4)
			)






