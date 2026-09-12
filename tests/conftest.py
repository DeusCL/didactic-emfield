"""Fixtures compartidas por la suite.

La app asume que se ejecuta desde la raíz del repo (settings usa rutas relativas
como ``Path("assets/")``) y necesita un display, así que aquí se fija el driver
headless de SDL y cada test se ejecuta desde la raíz.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from pathlib import Path

import pygame as pg
import pytest

from main import App

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def pygame_session():
	"""Inicializa pygame una vez para toda la sesión (sin ventana real)."""
	pg.init()
	yield
	pg.quit()


@pytest.fixture(autouse=True)
def in_repo_root(monkeypatch):
	monkeypatch.chdir(REPO_ROOT)


@pytest.fixture
def qapp():
	"""App recién construida; arranca con la escena vacía (nada llama a Scene.load)."""
	return App()


@pytest.fixture
def app_frame():
	"""Ejecuta N frames como App.run(), sin el bucle infinito.

	Omitimos la línea ``pg.mouse.set_cursor(...)`` de ``App.run()``: el driver
	dummy de SDL no la implementa (y no es parte de lo que se quiere cubrir).
	"""

	def _run(app, frames=3):
		for _ in range(frames):
			app.get_time()
			app.check_events()
			app.update()
			app.render()
			app.dt = app.clock.tick() * 0.001

	return _run
