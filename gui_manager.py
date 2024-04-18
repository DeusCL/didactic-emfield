import pygame as pg

from gui import *
from text_field import TextField
from settings import *

from particle import Carga, Sensor


class GuiManager:
	def __init__(self, app):
		self.app = app
		self.scene = app.scene
		self.scene.guim = self

		self.gui_elements = dict()

		self.dialog_to_show = None
		self.dialog_bg = None

		self.on_init()


	def on_init(self):
		self.generate_dialog_bg()

		def verificator(text):
			good = False

			try:
				a = tuple(map(float, text.split(',')))
			except:
				pass
			else:
				if len(a) == 2:
					good = True

			return good


		# Make a textfield test
		textfield1 = TextField(self, (0, 20),
			size = (125, 30),
			caption = "Posición (m)"
		)

		textfield1.verificator = verificator

		textfield2 = TextField(self, (140, 20),
			size = (100, 30),
			caption = "Carga",
			dtype = float
		)

		# Make a button that says Ok
		btn_ok = Button(self, (180, 65), (60, 25), "Ok")
		btn_ok.on_pressed = self.add_prtl
		btn_ok.on_pressed_args = (textfield1, textfield2,)

		# Make a button that says Cancelar
		btn_cancel = Button(self, (0, 65), (100, 25), "Cancelar")
		btn_cancel.on_pressed = self.close_dialog

		# Make a dialog test
		dialog_add_prtl = Dialog(self, "Colocar carga eléctrica",
			[textfield1, textfield2, btn_ok, btn_cancel]
		)


		# Make a button to place a particle
		btn_add_prtl = Button(self, (10, 10), (60, 60), "")
		btn_add_prtl.on_pressed = self.open_dialog
		btn_add_prtl.on_pressed_args = (dialog_add_prtl,)
		btn_add_prtl.img = pg.image.load(IMG_CHARGE)


		# Make a button to remove a particle
		btn_del_prtl = Button(self, (80, 10), (60, 60), "")
		btn_del_prtl.on_pressed = self.scene.remove_the_selected
		btn_del_prtl.img = pg.image.load(IMG_TRASH)






		# Make a textfield test
		snsr_pos = TextField(self, (0, 20),
			size = (125, 30),
			caption = "Posición (m)"
		)

		snsr_pos.verificator = verificator

		# Make a button that says Ok
		btn_ok = Button(self, (180, 65), (60, 25), "Ok")
		btn_ok.on_pressed = self.add_snsr
		btn_ok.on_pressed_args = (snsr_pos,)

		# Make a dialog to place a sensor
		dialog_add_snsr = Dialog(self, "Colocar sensor",
			[snsr_pos, btn_ok, btn_cancel]
		)



		# Make a button to place a sensor
		btn_add_snsr = Button(self, (150, 10), (60, 60), "")
		btn_add_snsr.on_pressed = self.open_dialog
		btn_add_snsr.on_pressed_args = (dialog_add_snsr,)
		btn_add_snsr.img = pg.image.load(IMG_SENSOR)

		font2 = pg.font.Font(FONT_2, 18)


		# Make a label that shows info
		self.info_label = Label(self, (10, 100),
			"", True, WHITE, font2
		)

		# Make a label that shows info
		self.info_label_charge = Label(self, (17, 120),
			"", True, WHITE, font2
		)

		# Make a label that shows info
		self.info_label_position = Label(self, (17, 140),
			"", True, WHITE, font2
		)

		# Make a label that shows info
		self.info_label_E = Label(self, (17, 160),
			"", True, WHITE, font2
		)


		# Make a textfield to type the name of the saving scene
		scene_name_textfield = TextField(self, (0, 20),
			size = (240, 30),
			caption = "Nombre de la escena:"
		)


		# Make a button to confirm the saving of the scene
		btn_confirm_save = Button(self, (140, 65), (100, 25), "Guardar")
		btn_confirm_save.on_pressed = self.save_scene
		btn_confirm_save.on_pressed_args = (scene_name_textfield,)


		# Make a dialog to type the name of the saving scene
		dialog_save_scene = Dialog(self,
			title="Guardar escena",
			elements=[
				scene_name_textfield,
				btn_confirm_save,
				btn_cancel
			]
		)



		# Make a button to save the current scene
		btn_save = Button(self, (220, 10), (60, 60), "")
		btn_save.on_pressed = self.open_dialog
		btn_save.on_pressed_args = (dialog_save_scene,)
		btn_save.img = pg.image.load(IMG_SAVE)



		self.add_gui_element(btn_add_prtl, "button_1")
		self.add_gui_element(btn_del_prtl, "button_2")
		self.add_gui_element(btn_add_snsr, "button_3")
		self.add_gui_element(btn_save, "save")

		self.add_gui_element(self.info_label, "label_1")
		self.add_gui_element(self.info_label_charge, "label_2")
		self.add_gui_element(self.info_label_position, "label_3")
		self.add_gui_element(self.info_label_E, "label_4")



	def save_scene(self, scene_name_textfield):
		success, msg = self.scene.save(scene_name_textfield)
		print(msg)
		if success:
			self.close_dialog()


	def add_snsr(self, field_pos):
		if field_pos.invalid_value:
			return

		pos_str = field_pos.text

		if pos_str == "":
			return

		pos = tuple(map(float, pos_str.split(',')))

		x, y = pos

		snsr = Sensor((x, -y))
		self.scene.add(snsr)

		self.scene.last_grabbed_particle = snsr

		self.close_dialog()


	def add_prtl(self, field_pos, field_charge):
		if field_pos.invalid_value or field_charge.invalid_value:
			return

		pos_str = field_pos.text
		charge_str = field_charge.text

		if pos_str == "":
			return

		if charge_str == "":
			charge_str = 1

		pos = tuple(map(float, pos_str.split(',')))
		charge = float(charge_str)

		x, y = pos

		prtl = Carga((x, -y), charge)

		self.scene.add(prtl)

		self.scene.last_grabbed_particle = prtl

		self.close_dialog()


	def open_dialog(self, dialog):
		self.dialog_to_show = dialog


	def close_dialog(self):
		self.dialog_to_show = None


	def add_gui_element(self, element, element_name):
		self.gui_elements[element_name] = element


	def handle_event(self, event):
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE and self.dialog_to_show is not None:
				self.close_dialog()

		for element in self.gui_elements.values():
			element.handle_event(event)

		if self.dialog_to_show is not None:
			self.dialog_to_show.handle_event(event)


	def update(self):
		prtl = self.scene.last_grabbed_particle

		if prtl is not None:
			self.info_label.text = "Información:"
			x, y = prtl.pos
			self.info_label_position.text = f"- Posición: {x}î + {-y}ĵ"
			self.info_label_charge.text = f"- Carga: {prtl.charge}μC"

			if prtl.charge == 0:
				cx, cy = prtl.electric_field
				self.info_label_E.text = f"- Campo: {cx}î + {-cy}ĵ"
			else:
				self.info_label_E.text = ""

		else:
			self.info_label.text = ""
			self.info_label_position.text = ""
			self.info_label_charge.text = ""
			self.info_label_E.text = ""


		for element in self.gui_elements.values():
			element.update()

		if self.dialog_to_show is not None:
			self.scene.controls_active = False
			self.dialog_to_show.update()


	def generate_dialog_bg(self):
		""" Generate a semi transparent surface that will be shown when
		a dialog is opened """

		self.dialog_bg = pg.Surface(
			pg.display.get_window_size()
		).convert_alpha()

		self.dialog_bg.fill((0, 0, 0, 120))


	def render(self, surface):
		for element in self.gui_elements.values():
			element.render(surface)

		self.scene.controls_active = self.dialog_to_show is None

		if self.dialog_to_show is not None:

			#pg.transform.gaussian_blur(
			#	self.app.window.copy(), 10,
			#	dest_surface = self.app.window
			#)

			surface.blit(self.dialog_bg, (0, 0))

			self.dialog_to_show.render(surface)


















