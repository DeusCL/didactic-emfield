# Plan de implementación - mejoras, refactors y reorganización

> Documento de trabajo. Se aplica de a poco, un ítem (o un grupo chico) por commit.
> Nada de esto incluye optimizaciones de rendimiento: solo corrección, claridad,
> eliminación de código innecesario y consistencia.

## Cómo usar este plan

**Convención de commits:** un ítem = un commit (o un grupo de ítems mecánicos del mismo archivo).
Mensajes en imperativo: `refactor(text_field): extraer helpers de portapapeles`.

**Verificación obligatoria en cada commit** (los cuatro deben pasar):

```bash
.venv/bin/pytest -q                                       # 30 passed, 4 xfailed
.venv/bin/pyrefly check --min-severity warn               # 0 diagnósticos
.venv/bin/ruff check && .venv/bin/ruff format --check     # 13 hallazgos pendientes (Fase 1)
SDL_VIDEODRIVER=dummy timeout 5 .venv/bin/python main.py  # arranca y carga escena
```

**Orden:** las fases están pensadas para que cada una sea verificable por separado.
No saltar de la Fase 0 a la 3 (los refactors grandes necesitan la red de seguridad).

**Invariantes del proyecto** (mantener mientras se refactoriza):

- Imports: los ordena `ruff` (`select = [..., "I"]`, isort) y son
  stdlib → terceros → proyecto absoluto (`settings`, `lib`) → relativos (`.`), un salto de
  línea entre grupos y alfabéticos dentro de cada grupo; **2 líneas en blanco** (PEP 8)
  antes del primer bloque de código, aplicadas por `ruff format` (decisión D10 = A).
  Sin `import *`.
- Indentación con tabuladores (`indent-style = "tab"`).
- `pyrefly.toml` mantiene el `[[sub-config]]` de `scenes/**` (son scripts de DSL).
- Identificadores en inglés / textos de UI en español (ver Decisión D5).

**Etiquetas de los ítems:**

- 🔴 **decide** - requiere una decisión de diseño antes de tocar código.
- 🧪 **test primero** - escribir el test que falla antes de arreglar.
- 🟢 **mecánico** - sin riesgo, se puede aplicar directo.

---

## Estado de partida

| Archivo | Líneas | Peso |
|---|---:|---|
| `lib/text_field.py` | 644 | editor de texto completo |
| `lib/gui.py` | 342 | mini-framework de widgets |
| `lib/gui_manager.py` | 318 | armado de UI |
| `lib/scene.py` | 261 | lógica + input + render |
| `main.py` | 174 | app loop |
| `lib/particle.py` | 129 | física |
| `lib/maths.py` | 102 | cálculo |
| `lib/camera.py` | 79 | cámara |
| `settings.py` | 68 | config mezclada |
| `lib/grid.py` / `lib/field.py` / `lib/custom_draw.py` | 114 | render |
| `scenes/*.py` | 27 | duplicados entre sí |
| **Total** | **≈2258** | 58% es GUI |

Recorte estimado al terminar: **≈450–550 líneas (~20–25%)** y 3 archivos nuevos de test.

> **Tras la Fase 0:** el código de la app pasó de 2258 a **2066 líneas** (-192, casi todo por
> el formateo: líneas en blanco y espacios), y la suite de tests son 323 líneas en `tests/`.

---

## Fase 0 - Red de seguridad y tooling (base de todo)

Objetivo: poder cambiar código sin miedo. **Nada de la Fase 2/3 debería empezar antes de esto.**

- [x] **0.1 🟢** Añadir a `requirements-dev.txt`: `pytest` + `ruff`. Crear `pyproject.toml` con
  `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `pythonpath = ["."]`) y `[tool.ruff]`
  (`line-length = 100`, `exclude = [".venv"]`, `indent-style = "tab"`).
- [x] **0.2 🧪** `tests/conftest.py`: driver dummy de SDL, `pygame_session` (pg.init/pg.quit
  por sesión), `in_repo_root` (chdir a la raíz, porque settings usa rutas relativas),
  `qapp` (construye `App()`) y `app_frame` (3 frames como `App.run()` sin bucle).
- [x] **0.3 🧪** `tests/test_maths.py`: 14 tests de `calc_E` (Coulomb, inversa del cuadrado,
  saturación de `alpha`, cancelación, signo, arrow points, `Q_norm`, `get_dist`,
  `smooth_step`). Valores anclados a la física, no a la implementación.
- [x] **0.4 🧪** `tests/test_scene_io.py`: roundtrip `save` → `load` de cargas (pasa),
  más 3 tests `xfail(strict=True)` para los bugs de 2.2 (sensores, partículas, nombre).
- [x] **0.5 🧪** `tests/test_smoke.py`: imports de los 13 módulos + 3 frames completos,
  más 1 `xfail(strict=True)` de la ruta Windows (2.4).
- [x] **0.6 🟢** `ruff check --fix` + `ruff format` aplicados en un commit **aislado y solo**
  (18 archivos: isort reordenó los imports, el formateador normalizó espacios y colapsó
  líneas en blanco; **ninguna línea de lógica**). Decisión D10 resuelta como **A**.

**Criterio de aceptación:** `pytest` corre, `pyrefly` en 0, `ruff format` estable y
`ruff check` sin más pendientes que los ítems ya planificados de la Fase 1.

**Resultado:** 30 passed + 4 xfailed (0.7 s) · `pyrefly` 0 diagnósticos ·
`ruff format` aplicado y estable (21 archivos, **-167 líneas netas** solo por colapsar
líneas en blanco y normalizar espacios) · `ruff check` con **13 hallazgos, todos de la
Fase 1** (E722 ×2 → 1.18, E712 ×6 → 1.19, F841 ×5 → 1.22). Nota: los E701 (7) los resolvió
el propio formateador al expandir los `if ...: return` de una línea → ítem 1.21 cerrado de paso.

---

## Fase 1 - Mecánico, sin decisiones de diseño

### 1.A Código muerto

- [ ] **1.1 🟢** `lib/gui.py`: borrar los setters `Widget.x` / `Widget.y` (0 asignaciones
  externas verificadas) y `Widget.handle_event/update/render` (los que sean `pass`).
- [ ] **1.2 🟢** `lib/gui.py`: borrar las propiedades `Label.color`, `Label.antialiasing`,
  `Label.font` y `Label.render_text` (solo se usa el setter de `text`).
- [ ] **1.3 🟢** `lib/gui.py` + `lib/gui_manager.py`: eliminar `Widget.clone` y
  `Button.clone`; reemplazar el único uso por un `Button(...)` construido con
  `on_pressed=self.add_sensor` (y `autopress_key=pg.K_RETURN` explícito).
- [ ] **1.4 🟢** `lib/text_field.py`: borrar la rama `dtype == int`, `on_type`,
  `get_selection_text()`, `render_textsurf()` / `render_surf()` (inline) y el memo de
  `render_caption` + la línea `self.caption_surf = self.render_caption(self.caption)` en `render()`.
- [ ] **1.5 🟢** `lib/scene.py`: borrar `self.pause` (2 asignaciones, 0 lecturas) y
  `reload()` (nunca llamado) - o dejarlo si se decide reactivarlo (Decisión D3).
- [ ] **1.6 🟢** `lib/camera.py`: borrar `self.target` y la rama `if self.target is not None`.
- [ ] **1.7 🟢** `lib/particle.py`: borrar `Sensor.magnitude`, `px, py = self.pos` de
  `CargaLibre.render` y el `if E is not None:` de `Sensor.render` (siempre verdadero).
- [ ] **1.8 🟢** `lib/field.py`: borrar `self.vectors_head_size`.
- [ ] **1.9 🟢** `lib/grid.py`: borrar `self.grid_thickness` y el parámetro
  `line_thickness` de `draw_grid` (nunca se usa).
- [ ] **1.10 🟢** `main.py`: borrar `self.font` + `FONT_1` de `settings.py`
  (y evaluar borrar `assets/fonts/cmunbi.ttf`).
- [ ] **1.11 🟢** `lib/scene.py` / `lib/gui_manager.py`: borrar `Scene.guim` y
  `self.scene.guim = self` (escritura sin ninguna lectura).
- [ ] **1.12 🟢** `main.py`: borrar el parámetro `hotspot` de `new_cursor`
  (nadie lo pasa; el ternario es muerto).
- [ ] **1.13 🟢** `settings.py`: borrar `TARGET_FPS`, `SHOW_FPS`, `ARROW_CENTERED`,
  `BLUE`, `BACKGROUND`, `ITEM1`, `ITEM2` y las 4 variables intermedias de paths
  (`ASSETS_DIR`, `FONTS_DIR`, `CURSORS_DIR`, `IMAGES_DIR`) usándolas solo para construir las rutas finales.
- [ ] **1.14 🟢** `scenes/rosa.py`: eliminar (es idéntico a `scene1.py`; `diff` confirma
  que solo difiere en una línea en blanco final).

### 1.B Ruido

- [ ] **1.15 🟢** Borrar código comentado: `#q2 = CargaLibre(...)`, `#self.particles.append(q2)`,
  `#if self.camera.zoom < 70000:`, `#self.app = app`, `#self.padding = 0, 0`,
  `#self.pos = pos`, `#style`.
- [ ] **1.16 🟢** Borrar comentarios que repiten el nombre de la variable de al lado
  (~25 en `GuiManager.on_init`: `# Button to create a new particle` sobre `btn_new_particle`)
  y los `# Draw the ...` / `# Render the ...` (~40 en total).
- [ ] **1.17 🟢** Arreglar docstrings falsos: `TextField.__init__` documenta `app` (no
  existe), omite `caption`/`dtype`/`verificator`, y el bloque "This class requires:
  import ..." no aplica.
- [ ] **1.18 🟢** `except:` desnudo → excepción concreta en `Scene.save` y en el
  `verificator` de `GuiManager.on_init`.
- [ ] **1.19 🟢** `== True` / `== False` → `if x:` / `if not x:` en `main.py`,
  `Scene.handle_event`, `Scene.move_charges`.
- [ ] **1.20 🟢** `if` → `elif` en `App.check_events`, `Scene.handle_event` y
  `Button.handle_event` (donde mezcla `elif` con `if`).
- [x] **1.21 🟢** `E701` (7): separar los `if ...: return` de una línea en
  `grid.py:30`, `maths.py:65`, `scene.py:151,152`, `text_field.py:85,86,398`.
  ✔ **Resuelto por el formateador** en 0.6, no hace falta tocarlo a mano.
- [x] **1.23 🟢** `F541` / `E713` ×2 / `except ValueError as e` sin uso: los arregló
  `ruff check --fix` en 0.6.
- [ ] **1.22 🟢** `F841` (5, todos en `Scene.load`): `cam`, `app`, `field` y `grid`
  nunca se usan (ni el DSL los usa hoy) y desaparecen al resolver D7/3.29. `add` **sí** se
  usa: lo consume el código que ejecuta `exec()`, que ningún linter ve → con 3.29
  (namespace explícito) se vuelve visible; si no, queda `# noqa: F841` con motivo.

**Criterio de aceptación por commit:** pyrefly 0, pytest verde, app arranca.

---

## Fase 2 - Bugs latentes (cada uno 🧪 test primero, varios 🔴 decide)

> Estos cambian comportamiento. Conviene resolver las Decisiones D1–D3 antes.

- [ ] **2.1 🔴🧪** **`TextField.verificator` nunca se guarda** (`self.verificator = None`
  ignora el parámetro) → el campo "Posición (m)" **jamás valida**. Test: pasar un
  verificador que rechaza `"1,2,3"` y assert `invalid_value is True` (hoy falla).
  Decisión D1.
- [ ] **2.2 🔴🧪** **`Scene.save()` pierde sensores y partículas** y **no sanitiza el
  nombre** (`SCENES_DIR / f"{text}"` permite `../`): guardar solo `charges`, cargar
  la escena y comparar. Decisión D2 + validar el nombre contra `[A-Za-z0-9_-]+`.
- [ ] **2.3 🧪** `Scene.save` con `open()` sin `with` / `close()` sin `finally` → `with open(...)`.
- [ ] **2.4 🟢** **`main.py` carga la escena con ruta Windows** (`"scenes\\scene1.py"`):
  en Linux `os.path.exists` es `False` → arranca con la escena vacía **sin avisar**.
  Usar `SCENES_DIR / "scene1.py"`. Cubierto por el test 0.5.
- [ ] **2.5 🧪** `Scene.load()` debe fallar ruidosamente si el archivo no existe
  (hoy imprime "load finished" igual) → `FileNotFoundError` o `logging.error` + `return False`.
- [ ] **2.6 🟢** `App.exit()`: el `pg.quit()` está después de `sys.exit()` (inalcanzable)
  → `pg.quit(); sys.exit()`.
- [ ] **2.7 🧪** **`App.__init__` ignora `FULLSCREEN`** (`set_mode(WIN_RES, vsync=...)`):
  con `FULLSCREEN = True` la ventana se crea en modo ventana pero `_fullscreen` dice
  `True`. Aplicar `FULLSCREEN` en el arranque (o eliminarlo de `settings` si nunca se usa).
- [ ] **2.8 🔴🧪** **`Field.render` muta `camera.speed`** (efecto colateral en el render
  que altera la física del frame siguiente). Mover el cálculo a `update()` o pasarlo
  como parámetro. Test de caracterización: tras `render()`, `camera.speed` no cambia.
- [ ] **2.9 🔴** **`Camera.update(dt=1/60)` nunca recibe el `dt` real** mientras las
  partículas sí → decidir: pasar `app.dt` a la cámara o fijar 1/60 en todos.
- [ ] **2.10 🟢** `TextField.hovering` no se inicializa en el constructor (AttributeError
  si llega un clic en el primer frame) → inicializar en `Widget.__init__`.
- [ ] **2.11 🟢** `Dialog.organize()` con 0 elementos deja `self.surface` sin crear →
  `AttributeError` en `render()`. Crear siempre el surface.
- [ ] **2.12 🔴** `Label.render(surface, offset)` interpreta `offset` como desplazamiento
  **adicional** a `self.pos` (que ya incluye `self.offset`), pero `Button.render` lo
  ignora. Unificar la semántica (propuesta: que el origen lo calcule un único sitio).
- [ ] **2.13 🔴** Estado de diálogos no se resetea: `tf_pos` y `btn_cancel` son la **misma
  instancia** en los diálogos "nueva carga" y "nuevo sensor", y `close_dialog()` no
  limpia el texto. Decidir si compartir (documentarlo) o limpiar al abrir (recomendado).
- [ ] **2.14 🟢** `Scene.add` decide carga vs sensor por `prtl.charge != 0`: una carga de
  **0 μC se registra como sensor**. Separar en `add_charge()` / `add_sensor()` o usar `isinstance`.
- [ ] **2.15 🟢** `CargaLibre.update()` asigna `self.vel` dos veces seguidas → una sola expresión.
- [ ] **2.16 🟢** `CargaLibre.update()`: `list(set(particles + charges) - {self})` no
  preserva orden → la suma del campo puede variar entre frames. Usar comprensión con
  identidad (`p is not self`) - es corrección, no optimización.

---

## Fase 3 - Abstracciones y simplificaciones (los «pudo ser más corto»)

### 3.A Cámara y geometría

- [ ] **3.1 🧪** `Camera.world_to_screen(pos)` / `screen_to_world(pos)`: hoy la fórmula
  `cam_pos + ventana//2` se recalcula en `Scene.get_rel_pos`, `Scene.move_charges`,
  `Scene.render`, `Camera.handle_zoom` y se pasa como `offset_pos` a `Grid`/`Field`.
  Un solo helper elimina 4 copias. Test unitario del redondeo/offset.
- [ ] **3.2 🟢** `Camera.handle_zoom`: unificar las 2 ramas (~22 líneas → ~8) con
  `factor = 1.3 if wheel > 0 else 1/1.3` + un solo cálculo y clamp.
- [ ] **3.3 🟢** Sacar los números mágicos a constantes: `1.3` (zoom), `10**-6` (μC→C,
  usado en `maths.calc_sum` y `CargaLibre.update`), `0.001` (`main.get_time`), `8990`
  (`Q_alpha`), `1000`/`rscale` (en `CargaLibre` **multiplica** y en `Sensor` **divide**,
  con el mismo nombre y significado opuesto: renombrar al menos uno).
- [ ] **3.4 🔴** `Camera.zoom = 30.0` con `min_zoom = 50`: el inicial se sobrescribe en
  el primer `update`. Unificar y mover `min_zoom`/`smoothness` a `settings` (Decisión D4).
- [ ] **3.5 🟢** El módulo repetido `((i*scale + off) % (n*scale)) - scale` está copiado
  en `Grid.draw_grid` y `Field.render` → helper compartido.

### 3.B Partículas y matemática

- [ ] **3.6 🟢** `CargaLibre`/`Carga`/`Sensor` comparten `get_size` y `render` (con
  variantes de color distintas) → base común `Particle` con `world_to_screen` y color
  como método; `Sensor(Carga)` conserva su especificidad.
- [ ] **3.7 🟢** `Carga.render` usa tuplas RGBA de 4 elementos y `CargaLibre.render`
  aritmética con tuplas de 3 + ternarios numéricos
  (`(255,166,255)*(charge>0) + ...`) → un `_color()` por clase o un dict de colores.
- [ ] **3.8 🟢** `maths`: `Q_rsqrt` y `Q_rsqrt_c` son idénticas salvo `**3` → una con
  parámetro. `smooth_step(..., smoothness=10)` usa `10/smoothness`: pasar el factor directo.
  Documentar `K` y el prefijo `Q_`.

### 3.C Widgets y GUI

- [ ] **3.9 🔴** `Widget`/`Dialog` (`gui.py`): decidir contrato (Decisión D6). Opciones:
  (a) `abc.ABC` con `render`/`update`/`handle_event` abstractos y `Dialog` heredando;
  (b) sin base, duck typing puro. Elimina los no-ops y la asimetría `Dialog`.
- [ ] **3.10 🟢** `Button.check_hovering`: `cnd1/cnd2/cnd3` → una sola expresión booleana.
- [ ] **3.11 🟢** `Button.__init__`: `if on_pressed_args is None` (4 líneas) → `or ()`.
  Evaluar `on_pressed=lambda: None` como default para borrar el guard `is not None`.
- [ ] **3.12 🟢** `Dialog.organize`: 4 acumuladores manuales → `max(... for e in elements)`.
- [ ] **3.13 🔴** `Dialog.render` muta a sus hijos cada frame (`padding`, `offset`,
  `in_dialog`) → pasar un origen a `render(surface, origin)` y sacar el estado de layout
  de los hijos (se relaciona con 2.12).
- [ ] **3.14 🟢** `GuiManager.gui_elements` (dict con claves string) +
  `add_gui_element()` → atributos con nombre (`self.btn_new_particle`, `self.lb_position`).
  `Dialog` ya usa lista: unificar. Además sacar los 4 lookups del `update()`.
- [ ] **3.15 🟢** `GuiManager`: `on_init` (150 líneas) → `_build_ui()` con nombres reales;
  `add_particle`/`add_sensor` comparten `_parse_position(field) -> tuple | None`;
  el `verificator` closure (12 líneas con `try/except/else` y variable sin usar) → 3 líneas;
  `update()` con helper `_set_info(...)`; el `(bool, str)` de `Scene.save` → excepción/log
  (la capa lógica no debe devolver textos de UI).
- [ ] **3.16 🟢** `App`: `check_events` con tabla `{pg.K_F11: ..., pg.K_F10: ...}`;
  `get_time()` inline (o `self.time += self.dt`); `self.dt` calculado **al inicio** del
  loop (hoy se calcula al final y el primer frame usa el default);
  `save_screenshot` con `SCREENSHOTS_DIR.mkdir(exist_ok=True)` una vez y
  `strftime("%Y%m%d_%H%M%S")` (hoy es "mes-día-año", no ordenable).
- [ ] **3.17 🟢** `App`: `scene` + `guim` como lista de capas (`for layer in self.layers`)
  para `update`/`render`/`handle_event` → agregar una capa nueva no toca `App`.
- [ ] **3.18 🔴** `controls_active`: lo escriben `App.update`, `GuiManager.update` y
  `GuiManager.render`; lo leen `Scene` y `Button`. Convertirlo en propiedad derivada.
- [ ] **3.19 🔴** `App.current_cursor` + dict de cursores + reset por frame +
  `pg.mouse.set_cursor` por frame → `app.set_cursor(...)` que solo actúa si cambió, con
  un `enum.IntEnum` de cursores (hoy son 5 constantes enteras en `settings.py`).
  Añadir `def main()` y dejar el guard `if __name__ == "__main__":` en 2 líneas.
- [ ] **3.20 🟢** Colores hardcodeados fuera de `settings`: `(170,255,170)` (`particle`),
  `(100,255,255,alpha)` (`field`), `(150,150,150)`/`(50,50,50)`/`(80,80,80)` (`grid`),
  `(0,0,0,0)` ×3, y `pg.font.SysFont("Consolas", 16)` duplicado en `Label` y `TextField`
  (que además convive con `FONT_2 = consolab.ttf`) → un único origen por recurso.

### 3.D TextField (el refactor más grande - 🧪 test de caracterización ANTES)

- [ ] **3.21 🧪** Tests de caracterización del editor **antes de tocar nada**: mover
  cursor (izq/der/up/down), borrar hacia atrás/adelante, insertar en el medio, selección
  con shift, doble clic (seleccionar todo), copiar/pegar/recortar con `pyperclip`
  monkeypatcheado, límites del `dtype=float`. Estos tests son el contrato del refactor.
- [ ] **3.22 🟢** Extraer `_copy_selection()`, `_replace_selection(text)`,
  `_insert_at_cursor(text)`: hoy los bloques de Ctrl+C/X/V y de tipeo están repetidos
  casi literalmente dentro de un `handle_event` de **~250 líneas con 5 niveles de anidación**.
- [ ] **3.23 🟢** `handle_event` → `_on_mouse_down` / `_on_mouse_up` / `_on_key_down` /
  `_on_key_up`.
- [ ] **3.24 🟢** **`cursor_bwpos` → índice normal `cursor`**: hoy la posición se mide
  desde el final y obliga a `len(self.text) - x` en **8 sitios** más el
  `self.text[:-self.cursor_bwpos]` para rebanar. `cursor == len(text)` (4 comparaciones)
  merece un nombre (`at_end`).
- [ ] **3.25 🟢** Los 4 timers de auto-repeat (`left_time`, `right_time`, `backspace_time`,
  `delete_time`) + 4 bloques idénticos en `update()` → un dict `{key: time}` + loop (~20 → ~8).
- [ ] **3.26 🟢** `*((self.border_radius,)*4)` repetido 4 veces → `_rounded_rect(surface, color, width)`.
- [ ] **3.27 🟢** Validación en `update_text_surf`: `try/except ValueError` +
  `if verificator` + 3 asignaciones → `invalid_value` como propiedad derivada
  (se apoya en 2.1).
- [ ] **3.28 🟢** `__init__` de `TextField`: ~25 asignaciones, revisar cuáles son estado
  real y cuáles configuración de estilo.

### 3.E Escenas (DSL)

- [ ] **3.29 🔴🧪** `Scene.load`: `exec(file.read())` escribe en los `locals/globals` del
  frame del método (por eso `from .particle import ...` "funciona" por accidente usando
  el `__package__` de `lib.scene`). Pasar un namespace explícito
  (`exec(code, {"add": self.add, "__name__": ...})`), documentar el contrato del DSL
  (`add`, `cam`, `app`, `field`, `grid` - de los que hoy **solo `add` se usa**) y decidir
  si se recortan los alias no usados (Decisión D7).
- [ ] **3.30 🟢** `Scene.move_charges` (25 líneas de indentación con `for ... break`) →
  extraer `_particle_at(pos)`; `remove_the_selected` (2 `try/except ValueError`) →
  una sola pasada sobre las colecciones.
- [ ] **3.31 🔴** `Scene` hace input + física + render (y `Scene.handle_event` con 3 `if`
  que deberían ser `elif`, ya en 1.20). Evaluar separar `SceneControls` de `Scene`.

### 3.F Logging

- [ ] **3.32 🟢** `print()` → `logging` (`Scene.load/add/save`, `Scene.move_charges`
  "Dropped with clamps", `TextField` "Text: ...", `GuiManager.save_scene`). Hoy cargar una
  escena imprime ~11 líneas sin nivel ni categoría.

---

## Fase 4 - Reorganización estructural

- [ ] **4.1 🔴** Partir `settings.py` (mezcla display + rutas + física + tema + enum de
  cursores) en `config/display.py`, `config/paths.py`, `config/physics.py`, `config/theme.py`
  y un `Cursor(enum.IntEnum)` en `config/cursors.py` (re-exportar desde `settings.py` para
  no romper imports de golpe, o migrar todo en el mismo commit).
- [ ] **4.2 🟢** Rutas ancladas al archivo: `Path(__file__).resolve().parent / "assets"`
  en vez de `Path("assets/")` → hoy ejecutar desde otra carpeta rompe fuentes/imágenes.
- [ ] **4.3 🔴** `lib/` → `emfield/` (nombre genérico, colisiona conceptualmente con
  cualquier cosa) + `pyproject.toml` con el paquete y un entry point. Decisión D8.
- [ ] **4.4 🔴** Renombrar identificadores del dominio a un solo idioma (Decisión D5):
  `Carga`/`CargaLibre` → `Charge`/`FreeCharge`, `verificator` → `validator`,
  `prtl`/`guim`/`cdraw`/`bwpos`/`cnd1..3`/`tf_*`/`lb_*`.
  ⚠️ Ojo: `Carga` es parte del DSL de `scenes/*.py` y de lo que escribe `Scene.save()`
  → si se renombra, hay que migrar las escenas existentes y el texto que genera `save`.
- [ ] **4.5 🟢** README: pasos de ejecución (`.venv`, `python main.py`), tabla de controles
  (F10 captura, F11 fullscreen, O centrar, K partícula libre, Supr borrar, Ctrl+C/X/V,
  Shift selección, Espacio arrastrar cámara), y sección del DSL de escenas.
- [ ] **4.6 🟢** `requirements.txt` con rangos de versión + `pyproject.toml` como fuente
  única; `.gitignore`: ignorar las capturas generadas por F10 y conservar la del README.
- [ ] **4.7 🟢** `docs/`: mover este plan y el análisis de la revisión.

---

## Fase 5 - Calidad continua

- [ ] **5.1 🟢** CI (GitHub Actions): `ruff check`, `ruff format --check`, `pyrefly check`
  y `pytest` en Python 3.13 con `SDL_VIDEODRIVER=dummy`.
- [ ] **5.2 🟢** Tipado gradual de firmas públicas: `maths.py`, `particle.py`, `scene.py`,
  `camera.py` primero (hoy pyrefly da 0 diagnósticos en parte porque muchos parámetros no
  están anotados y se infieren `Unknown`).
- [ ] **5.3 🔴** Evaluar subir `preset` de pyrefly de `default` a `strict` una vez que el
  código esté tipado (y decidir el destino de los `unknown-name` de `scenes/**`).

---

## Momento de los tests (resumen)

| Cuándo | Test | Para qué |
|---|---|---|
| **Fase 0, antes de todo** | `test_maths.py` (valores de referencia de `calc_E`) | protege la física durante todos los refactors |
| **Fase 0** | `test_smoke.py` (imports + 3 frames + escena no vacía) | detecta roturas de imports/arranque en cada commit |
| **Fase 0** | `test_scene_io.py` (roundtrip save→load) | guía 2.2 (pierde sensores/partículas) |
| **Antes de 2.1** | test del `verificator` (falla hoy) | red-green del bug de validación |
| **Antes de 2.8** | test de caracterización: `render()` no muta `camera.speed` | fija el comportamiento correcto antes de mover el efecto a `update()` |
| **Antes de 3.21–3.27** | suite de caracterización del editor de texto | es el refactor más riesgoso del proyecto (644 líneas, máquina de estados) |
| **Antes de 3.29** | test que carga una escena y verifica `charges`/`sensors`/`particles` | el namespace del `exec` se rompe fácil |
| **Después de 3.1** | test unitario de `world_to_screen` (ida y vuelta) | es la fórmula que hoy está copiada 5 veces |
| **Antes de 4.1–4.3** | nada nuevo: la suite existente cubre imports y arranque | mover archivos solo lo rompe si un import queda mal |
| **Fase 5** | los anteriores + CI | que no se degrade con el tiempo |

**Regla general:** cada ítem 🔴/🧪 entra con test que falla primero; los 🟢 se cubren con
los tests de humo de la Fase 0. No se escribe test de lo que se va a borrar (ítems 1.x).

---

## Decisiones abiertas (necesarias antes de la fase indicada)

| ID | Pregunta | Fase |
|---|---|---|
| **D1** | ¿`verificator` se conserva como API (guardar el parámetro) o se reemplaza por validación declarativa (`dtype`/regex/al `_parse_position`)? | 2.1 |
| **D2** | ¿Las escenas guardadas deben incluir sensores y partículas `CargaLibre` (requiere serializar también su estado dinámico: `vel`, etc.) o solo las cargas fijas? | 2.2 |
| **D3** | ¿Se elimina `Scene.reload()` o se reactiva (tecla/ botón) y se corrige para limpiar `particles`? | 1.5 / 2.x |
| **D4** | ¿`min_zoom`, `smoothness` y el factor `1.3` se exponen en `settings` o quedan privados de `Camera`? | 3.4 |
| **D5** | ¿Se unifican los identificadores a inglés (`Carga` → `Charge`)? Afecta el DSL de escenas y el archivo que escribe `Scene.save()`. | 4.4 |
| **D6** | ¿`Widget` pasa a `abc.ABC` con `Dialog` heredando, o se deja duck typing sin clase base? | 3.9 |
| **D7** | ¿El DSL expone solo `add`(+ `Carga`/`Sensor`) o se mantienen `cam`/`app`/`field`/`grid` documentados aunque hoy no se usen? | 3.29 |
| **D8** | ¿`lib/` se renombra a `emfield/` con `pyproject.toml` (empaquetado real) o se mantiene la estructura plana? | 4.3 |
| **D9** | ¿Se conservan las comodidades del editor (auto-repeat de flechas/backspace, doble clic, selección con arrastre) o se recortan? | 3.25 |
| **D10** | Convención de líneas en blanco tras los imports: ¿3 (estilo de la casa, sin soporte de herramientas) o 2 (PEP 8, compatible con `ruff format` + isort)? | 0.6 |

**D10 — resuelta: opción A.** Se adoptó PEP 8 (2 líneas en blanco) y se habilitaron
`ruff format` + `I` (isort). Contexto del conflicto detectado: `ruff format` (equivalente a
Black) colapsa a 2 las líneas en blanco a nivel de módulo y avisa *«The isort option
`isort.lines-after-imports` with a value other than `-1`, `1` or `2` is incompatible with
the formatter»*; además isort ordena el grupo del proyecto como `from settings import ...`
**antes** de `from . import maths` (first-party antes de local-folder), al revés de lo que se
había fijado a mano. La opción B (mantener 3 líneas, sin formateador ni isort) quedó descartada.

---

## Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| `ruff format` toca todo el repo y ensucia los diffs siguientes | commit aislado en 1.6, antes de cualquier refactor |
| El refactor de `TextField` (3.21–3.28) rompe la edición sin que se note a simple vista | suite de caracterización previa + commits por método |
| `cursor_bwpos` → `cursor` (3.24) es aritmética invertida en 8 sitios | hacerlo en su propio commit, con la suite de 3.21 en verde antes y después |
| Mover `settings.py` a `config/` (4.1) rompe imports en 8 archivos | re-exportar desde `settings.py` durante una fase de transición |
| Renombrar `Carga` (4.4) invalida las escenas guardadas | decidir D5 y, si se hace, migrar `scenes/*.py` y `Scene.save()` en el mismo commit |
| El efecto colateral de `Field.render` (2.8) altera el comportamiento visible | test de caracterización antes, y verificar la app a mano después (campo eléctrico en zoom cercano) |
| Perder los cambios sin red | trabajar en una rama `refactor/fase-N` y no acumular más de 1 fase por PR |

---

## Orden recomendado (ruta corta si se quiere avanzar rápido)

1. **Fase 0** completa (tests + ruff) - habilita todo lo demás.
2. **Fase 1** completa (mecánico, ~-150 líneas, riesgo casi nulo).
3. **Fase 2**: solo 2.1, 2.2, 2.4, 2.6, 2.10, 2.11, 2.14, 2.15 (bugs con arreglo claro).
4. **Fase 3.A + 3.B + 3.F** (helpers y constantes: mucho recorte, poco riesgo).
5. **Fase 3.C** (widgets) y luego **3.D** (TextField) con la suite de 3.21.
6. **Fase 4** y **Fase 5**.
