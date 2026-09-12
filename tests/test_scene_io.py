"""Guarda y recarga escenas (``Scene.save`` / ``Scene.load``).

Los tests marcados ``xfail(strict=True)`` documentan bugs conocidos del plan
(``docs/implementation-plan.md``, ítem 2.2): cuando se arreglen, el test pasará y
el marcador estricto fallará a propósito para forzar a actualizarlo.
"""

import pytest

from lib.particle import Carga, CargaLibre, Sensor

SCENE_NAME = "escena_prueba"


class FakeTextField:
	"""``Scene.save`` recibe un widget pero solo usa ``.text`` (ítem 3.15 del plan)."""

	def __init__(self, text):
		self.text = text


@pytest.fixture
def scenes_dir(tmp_path, monkeypatch):
	# lib/scene.py importó SCENES_DIR por valor: hay que parchear el módulo, no settings.
	monkeypatch.setattr("lib.scene.SCENES_DIR", tmp_path)
	return tmp_path


@pytest.fixture
def scene(qapp):
	return qapp.scene


def test_save_writes_a_file_in_the_scenes_directory(scene, scenes_dir):
	scene.add(Carga((1.0, 2.0), 3.0))

	success, _ = scene.save(FakeTextField(SCENE_NAME))

	assert success
	assert (scenes_dir / f"{SCENE_NAME}.py").exists()


def test_save_and_load_keeps_the_charges(scene, scenes_dir):
	scene.add(Carga((1.5, -2.5), 4.4))
	scene.add(Carga((-3.0, 2.0), -1.1))
	scene.save(FakeTextField(SCENE_NAME))
	scene.charges.clear()

	scene.load(scenes_dir / f"{SCENE_NAME}.py")

	assert [(c.pos, c.charge) for c in scene.charges] == [
		((1.5, -2.5), 4.4),
		((-3.0, 2.0), -1.1),
	]


@pytest.mark.xfail(strict=True, reason="Scene.save solo escribe charges (item 2.2)")
def test_save_and_load_keeps_the_sensors(scene, scenes_dir):
	scene.add(Sensor((2.0, 1.0)))
	scene.save(FakeTextField(SCENE_NAME))
	scene.sensors.clear()

	scene.load(scenes_dir / f"{SCENE_NAME}.py")

	assert len(scene.sensors) == 1


@pytest.mark.xfail(strict=True, reason="Scene.save no escribe particulas libres (items 2.2 / D2)")
def test_save_and_load_keeps_the_free_particles(scene, scenes_dir):
	scene.add(CargaLibre(scene, (0.5, 0.5), 1.0))
	scene.save(FakeTextField(SCENE_NAME))
	scene.particles.clear()

	scene.load(scenes_dir / f"{SCENE_NAME}.py")

	assert len(scene.particles) == 1


@pytest.mark.xfail(strict=True, reason="el nombre de la escena no se valida (item 2.2)")
def test_save_does_not_write_outside_the_scenes_directory(scene, scenes_dir):
	scene.add(Carga((0.0, 0.0), 1.0))

	scene.save(FakeTextField("../fuera_de_scenes"))

	assert not (scenes_dir.parent / "fuera_de_scenes.py").exists()
