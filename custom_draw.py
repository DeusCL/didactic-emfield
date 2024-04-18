import math
import maths

import pygame as pg

from settings import ARROW_CENTERED


def arrow(surface, color, start_pos, end_pos, arrow_size=10, line_width=3):
	pg.draw.line(surface, color, start_pos, end_pos, line_width)
	p1, p2 = maths.calc_arrow_points(start_pos, end_pos, arrow_size)
	pg.draw.lines(surface, color, False, [p1, end_pos, p2], line_width)

