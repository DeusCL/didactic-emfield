import pygame as pg

from .gui import *
from .text_field import TextField
from .particle import Carga, Sensor

from settings import *



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


		###### >>> TEXTFIELDS <<< #######
		# Textfield to type the Particle Position
		tf_pos = TextField(self, (0, 20),
			size = (125, 30),
			caption = "Posición (m)",
			verificator = verificator
		)

		# Textfield to type the Particle Charge
		tf_particle_charge = TextField(self, (140, 20),
			size = (100, 30),
			caption = "Carga",
			dtype = float
		)

		# Textfield to type the name of the saving scene
		tf_scene_name = TextField(self, (0, 20),
			size = (240, 30),
			caption = "Nombre de la escena:"
		)


		###### >>> BUTTONS <<< #######
		# Button to confirm and place the particle
		btn_place_particle = Button(self, (180, 65), (60, 25),
			text = "Ok",
			on_pressed = self.add_particle,
			on_pressed_args = (tf_pos, tf_particle_charge,),
			autopress_key = pg.K_RETURN
		)

		# Button to confirm and place a sensor
		btn_place_sensor = btn_place_particle.clone(
			on_pressed=self.add_sensor,
			on_pressed_args = (tf_pos,),
		)

		# Button to cancel any operation and close the current dialog
		btn_cancel = Button(self, (0, 65), (100, 25),
			text = "Cancelar",
			on_pressed = self.close_dialog,
			autopress_key = pg.K_ESCAPE
		)

		# Make a button to confirm the saving of the scene
		btn_confirm_save = Button(self, (140, 65), (100, 25),
			text = "Guardar",
			on_pressed = self.save_scene,
			on_pressed_args = (tf_scene_name,),
			autopress_key = pg.K_RETURN
		)


		###### >>> DIALOGS <<< #######
		# Dialog to create a new particle
		dialog_new_particle = Dialog(self,
			title="Nueva carga eléctrica",
			elements=[
				tf_pos,
				tf_particle_charge,
				btn_place_particle,
				btn_cancel
			]
		)

		# Dialog to create a new sensor
		dialog_new_sensor = Dialog(self,
			title="Nuevo sensor",
			elements=[
				tf_pos,
				btn_place_sensor,
				btn_cancel
			]
		)

		# Dialog to type the name of the saving scene
		dialog_save_scene = Dialog(self,
			title="Guardar escena",
			elements=[
				tf_scene_name,
				btn_confirm_save,
				btn_cancel
			]
		)


		###### >>> MAIN BUTTONS <<< #######
		# Button to create a new particle
		self.add_gui_element("btn_new_particle",
			Button(self, (10, 10), (60, 60), "",
				on_pressed = self.open_dialog,
				on_pressed_args = (dialog_new_particle,),
				img = pg.image.load(IMG_CHARGE)
			)
		)

		# Button to place a sensor
		self.add_gui_element("btn_new_sensor",
			Button(self, (80, 10), (60, 60), "",
				on_pressed = self.open_dialog,
				on_pressed_args = (dialog_new_sensor,),
				img = pg.image.load(IMG_SENSOR)
			)
		)

		# Button to remove a particle
		self.add_gui_element("btn_remove_particle",
			Button(self, (150, 10), (60, 60), "",
				on_pressed = self.scene.remove_the_selected,
				img = pg.image.load(IMG_TRASH)
			)
		)

		# Button to save the current scene
		self.add_gui_element("btn_save_scene",
			Button(self, (220, 10), (60, 60), "",
				on_pressed = self.open_dialog,
				on_pressed_args = (dialog_save_scene,),
				img = pg.image.load(IMG_SAVE)
			)
		)


		###### >>> INFO LABELS <<< #######
		font2 = pg.font.Font(FONT_2, 18)

		self.add_gui_element("lb_info_title",
			Label(self, (10, 100), "", True, WHITE, font2)
		)

		self.add_gui_element("lb_info_position",
			Label(self, (17, 120), "", True, WHITE, font2)
		)

		self.add_gui_element("lb_info_charge",
			Label(self, (17, 140), "", True, WHITE, font2)
		)

		self.add_gui_element("lb_info_force",
			Label(self, (17, 160), "", True, WHITE, font2)
		)


	def save_scene(self, scene_name_textfield):
		success, msg = self.scene.save(scene_name_textfield)
		print(msg)
		if success:
			self.close_dialog()


	def add_sensor(self, field_pos):
		if field_pos.invalid_value or field_pos.text == "":
			return

		pos = tuple(map(float, pos_str.split(',')))
		sensor = Sensor((pos[0], -pos[1]))
		self.scene.add(sensor)
		self.scene.last_grabbed_particle = sensor
		self.close_dialog()


	def add_particle(self, field_pos, field_charge):
		if field_pos.invalid_value or field_charge.invalid_value:
			return

		pos_str = field_pos.text
		charge_str = field_charge.text

		if pos_str == "":
			return

		if charge_str == "":
			charge_str = 1

		pos = tuple(map(float, pos_str.split(',')))
		prtl = Carga((pos[0], -pos[1]), float(charge_str))

		self.scene.add(prtl)
		self.scene.last_grabbed_particle = prtl

		self.close_dialog()


	def open_dialog(self, dialog):
		self.dialog_to_show = dialog


	def close_dialog(self):
		self.dialog_to_show = None


	def add_gui_element(self, element_name, element):
		self.gui_elements[element_name] = element


	def handle_event(self, event):
		for element in self.gui_elements.values():
			element.handle_event(event)

		if self.dialog_to_show is not None:
			self.dialog_to_show.handle_event(event)


	def update(self):
		prtl = self.scene.last_grabbed_particle

		lb_title = self.gui_elements["lb_info_title"]
		lb_position = self.gui_elements["lb_info_position"]
		lb_charge = self.gui_elements["lb_info_charge"]
		lb_force = self.gui_elements["lb_info_force"]


		if prtl is not None:
			lb_title.text = "Información:"
			x, y = prtl.pos
			lb_position.text = f"- Posición: {x}î + {-y}ĵ"
			lb_charge.text = f"- Carga: {prtl.charge}μC"

			if prtl.charge == 0:
				cx, cy = prtl.electric_field
				lb_force.text = f"- Fuerza: {cx}î + {-cy}ĵ"
			else:
				lb_force.text = ""

		else:
			lb_title.text = ""
			lb_position.text = ""
			lb_charge.text = ""
			lb_force.text = ""


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
			surface.blit(self.dialog_bg, (0, 0))

			self.dialog_to_show.render(surface)


















