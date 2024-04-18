import pygame as pg
import sys

import pyautogui
import datetime
import os

from lib.scene import Scene
from lib.gui_manager import GuiManager

from settings import *



class App:
	def __init__(self):
		pg.init()

		self.window = pg.display.set_mode(WIN_RES, vsync=VSYNC)
		self.surface = pg.Surface(WIN_RES).convert_alpha()

		self._fullscreen = FULLSCREEN

		self.clock = pg.time.Clock()
		self.font = pg.font.Font(FONT_1, 30)

		self.time = 0
		self.dt = 1/60.0

		self.scene = Scene(self)
		self.guim = GuiManager(self)

		self.load_cursors()


	@property
	def fullscreen(self):
		"""Get the fullscreen status of the window."""
		return self._fullscreen


	@fullscreen.setter
	def fullscreen(self, is_fullscreen):
		"""Set the fullscreen status of the window.

		Args:
			is_fullscreen (bool): True to set fullscreen, False to set windowed.
		"""
		self._fullscreen = is_fullscreen

		if is_fullscreen == True:
			max_win_res = pyautogui.size()
			self.surface = pg.Surface(max_win_res).convert_alpha()
			self.window = pg.display.set_mode(
				max_win_res, pg.FULLSCREEN, vsync=VSYNC
			)

		if is_fullscreen == False:
			self.surface = pg.Surface(WIN_RES).convert_alpha()
			self.window = pg.display.set_mode(
				WIN_RES, vsync=VSYNC
			)

		self.guim.generate_dialog_bg()


	def new_cursor(self, cursor_filepath, hotspot=None):
		hotspot = (8, 8) if hotspot is None else hotspot

		new_cursor_img = pg.image.load(cursor_filepath)
		return pg.cursors.Cursor(hotspot, new_cursor_img)


	def load_cursors(self):
		self.cursors = {
			CURSOR_NORMAL: pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW),
			CURSOR_HAND_FINGER: pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND),
			CURSOR_HAND_OPEN: self.new_cursor(CURSOR_HAND_OPEN_FILEPATH),
			CURSOR_HAND_CLOSED: self.new_cursor(CURSOR_HAND_CLOSED_FILEPATH),
			CURSOR_TEXT_MARKER: self.new_cursor(CURSOR_TEXT_MARKER_FILEPATH)
		}

		self.current_cursor = CURSOR_NORMAL


	def save_screenshot(self):
		now = datetime.datetime.now()
		imgname = now.strftime("%m%d%Y%H%M%S.png")
		imgfilepath = SCREENSHOTS_DIR / imgname
		os.makedirs(SCREENSHOTS_DIR, exist_ok = True)

		pg.image.save(self.window, imgfilepath)



	def check_events(self):
		for event in pg.event.get():
			if event.type == pg.QUIT:
				self.exit()

			if event.type == pg.KEYDOWN:
				if event.key == pg.K_F11:
					self.fullscreen = not self.fullscreen

				if event.key == pg.K_F10:
					self.save_screenshot()

			self.guim.handle_event(event)
			self.scene.handle_event(event)


	def render(self):
		self.window.fill(BG_COLOR)
		self.surface.fill((0, 0, 0, 0))

		self.scene.render(self.window, self.surface)
		self.window.blit(self.surface, (0, 0))

		self.guim.render(self.window)

		pg.display.flip()


	def exit(self):
		sys.exit()
		pg.quit()


	def get_time(self):
		self.time = pg.time.get_ticks()*0.001


	def update(self):
		self.scene.controls_active = True
		self.guim.update()
		self.scene.update()


	def run(self):
		while True:
			self.current_cursor = CURSOR_NORMAL
			self.get_time()
			self.check_events()
			self.update()
			self.render()
			self.dt = self.clock.tick()*0.001

			pg.mouse.set_cursor(self.cursors[self.current_cursor])
			pg.display.set_caption(f"{self.clock.get_fps():.2f}")


if __name__ == '__main__':
	app = App()
	app.scene.load("scenes\\scene1.py")
	app.run()





