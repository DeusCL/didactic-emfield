"""Humo: imports, arranque y frame completo.

Esta es la red que detecta roturas al hacer los refactors mecánicos (Fase 1) y de
estructura (Fase 4): si un import se rompe o un frame deja de ejecutarse, falla acá.
"""

import importlib

import pytest

MODULES = [
	"main",
	"settings",
	"lib",
	"lib.camera",
	"lib.custom_draw",
	"lib.field",
	"lib.grid",
	"lib.gui",
	"lib.gui_manager",
	"lib.maths",
	"lib.particle",
	"lib.scene",
	"lib.text_field",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_module_imports(module_name):
	assert importlib.import_module(module_name) is not None


def test_app_boots_and_runs_frames(qapp, app_frame):
	app_frame(qapp)


@pytest.mark.xfail(strict=True, reason="main.py usa una ruta con backslash (item 2.4)")
def test_app_renders_the_default_scene(qapp, app_frame):
	"""main.py carga esta misma ruta antes de entrar en el bucle."""

	# Si se cambia el literal de main.py (ítem 2.4), actualizar este test.
	qapp.scene.load("scenes\\scene1.py")

	app_frame(qapp)

	assert qapp.scene.charges, "la escena por defecto quedó vacía (ítem 2.4 del plan)"
