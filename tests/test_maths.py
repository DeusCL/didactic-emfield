"""Tests de ``lib/maths.py``: la única capa pura del proyecto.

No importan pygame a propósito: ``calc_E`` solo necesita objetos con ``.pos`` y
``.charge`` (duck typing, ver ítem 3.2 del plan), así que se usa un namedtuple.
Estos tests fijan la física para que los refactors de render/GUI no la alteren.
"""

from collections import namedtuple

import pytest

from lib import maths
from settings import K

# La referencia de saturación de Q_alpha: campo de 1 μC a 1 m.
REFERENCE_FIELD = K * 1e-6

Charge = namedtuple("Charge", "pos charge")


def test_field_of_a_single_charge_follows_coulomb_law():
	charges = [Charge((0.0, 0.0), 1.0)]

	field, alpha = maths.calc_E(charges, 1.0, 0.0)

	assert field[0] == pytest.approx(REFERENCE_FIELD)
	assert field[1] == pytest.approx(0.0)
	# 1 μC a 1 m es justo la referencia: alpha queda saturado al máximo.
	assert alpha == pytest.approx(255.0)


def test_field_decays_with_the_inverse_square_of_the_distance():
	charges = [Charge((0.0, 0.0), 1.0)]

	near = maths.calc_E(charges, 1.0, 0.0)[0][0]
	far = maths.calc_E(charges, 2.0, 0.0)[0][0]

	assert far == pytest.approx(near / 4)


def test_alpha_scales_with_the_field_magnitude():
	charges = [Charge((0.0, 0.0), 1.0)]

	field, alpha = maths.calc_E(charges, 2.0, 0.0)

	assert alpha == pytest.approx(255 * abs(field[0]) / REFERENCE_FIELD)
	assert alpha == pytest.approx(255 / 4)


def test_alpha_saturates_at_255():
	charges = [Charge((0.0, 0.0), 100.0)]

	_, alpha = maths.calc_E(charges, 0.1, 0.0)

	assert alpha == 255.0


def test_equal_charges_cancel_in_the_middle():
	charges = [Charge((-1.0, 0.0), 1.0), Charge((1.0, 0.0), 1.0)]

	field, alpha = maths.calc_E(charges, 0.0, 0.0)

	assert field == pytest.approx((0.0, 0.0))
	assert alpha == pytest.approx(0.0)


def test_opposite_charges_double_in_the_middle():
	charges = [Charge((-1.0, 0.0), 1.0), Charge((1.0, 0.0), -1.0)]

	field, _ = maths.calc_E(charges, 0.0, 0.0)

	# Ambos apuntan hacia la carga negativa: se suman.
	assert field[0] == pytest.approx(2 * REFERENCE_FIELD)
	assert field[1] == pytest.approx(0.0)


def test_negative_charge_inverts_the_field():
	positive = maths.calc_E([Charge((0.0, 0.0), 1.0)], 1.0, 0.0)[0]
	negative = maths.calc_E([Charge((0.0, 0.0), -1.0)], 1.0, 0.0)[0]

	assert negative[0] == pytest.approx(-positive[0])
	assert negative[1] == pytest.approx(-positive[1])


def test_query_about_a_charge_position_cancels_the_whole_field():
	"""Comportamiento actual: si la consulta coincide con una carga, ``calc_sum``
	devuelve (0, 0) y ``calc_E`` corta el cálculo completo (no solo esa carga)."""
	charges = [Charge((0.0, 0.0), 1.0), Charge((5.0, 0.0), 1.0)]

	field, alpha = maths.calc_E(charges, 0.0, 0.0)

	assert field == (0, 0)
	assert alpha == 0


def test_q_norm_returns_a_unit_vector():
	assert maths.Q_norm((3.0, 4.0)) == pytest.approx((0.6, 0.8))


def test_q_norm_of_a_zero_vector_is_zero():
	# El guard de Q_rsqrt evita la división por cero.
	assert maths.Q_norm((0.0, 0.0)) == (0.0, 0.0)


def test_get_dist():
	assert maths.get_dist((0.0, 0.0), (3.0, 4.0)) == pytest.approx(5.0)
	assert maths.get_dist((1.0, 1.0), (1.0, 1.0)) == pytest.approx(0.0)


def test_arrow_head_points_sit_behind_the_tip():
	tip = (10.0, 0.0)

	p1, p2 = maths.calc_arrow_points((0.0, 0.0), tip, 2.0)

	assert maths.get_dist(tip, p1) == pytest.approx(2.0)
	assert maths.get_dist(tip, p2) == pytest.approx(2.0)
	# Simétricas respecto del eje del vector.
	assert p1[0] == pytest.approx(p2[0])
	assert p1[1] == pytest.approx(-p2[1])


def test_smooth_step_advances_a_fraction_towards_the_target():
	# Con los valores por defecto (smoothness=10, dt=1/60) avanza 1/60 del camino.
	assert maths.smooth_step(0.0, 10.0, smoothness=10, dt=1 / 60) == pytest.approx(10 / 60)


def test_smooth_step_converges_without_overshooting():
	value = 0.0

	for _ in range(1000):
		value = maths.smooth_step(value, 10.0)
		assert value <= 10.0

	assert value == pytest.approx(10.0, abs=1e-3)
