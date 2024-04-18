import math
import maths

import pygame as pg

from settings import ARROW_CENTERED

# Made with Chat-GPT
def arrow(surface, color, start_pos, end_pos, arrow_size=10, line_width=3):
	pg.draw.line(surface, color, start_pos, end_pos, line_width)

	# Calcula el ángulo entre la línea y el eje x
	angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])

	# Calcula las coordenadas de los puntos de la cabeza de la flecha
	arrow_points = [
		end_pos,
		(
			end_pos[0] - arrow_size * math.cos(angle - math.pi / 6),
			end_pos[1] - arrow_size * math.sin(angle - math.pi / 6)
		),
		(
			end_pos[0] - arrow_size * 0.7 * math.cos(angle),
			end_pos[1] - arrow_size * 0.7 * math.sin(angle)
		),
		(
			end_pos[0] - arrow_size * math.cos(angle + math.pi / 6),
			end_pos[1] - arrow_size * math.sin(angle + math.pi / 6)
		)
	]

	pg.draw.polygon(surface, color, arrow_points)






def arrow2(surface, color, start_pos, end_pos, arrow_size=10, line_width=3):
	pg.draw.line(surface, color, start_pos, end_pos, line_width)

	# Calcula las coordenadas de los puntos de la cabeza de la flecha
	p1, p2 = maths.calc_arrow_points(start_pos, end_pos, arrow_size)

	pg.draw.lines(surface, color, False, [p1, end_pos, p2], line_width)
	#pg.draw.line(surface, color, p2, end_pos, 1)





def arrow_line(renderer, start_pos, end_pos, arrow_size=10):
	renderer.draw_line(start_pos, end_pos)

	# Calcula el ángulo entre la línea y el eje x
	angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])

	# Calcula las coordenadas de los puntos de la cabeza de la flecha
	arrow_points = (
			end_pos[0] - arrow_size * math.cos(angle - math.pi / 6),
			end_pos[1] - arrow_size * math.sin(angle - math.pi / 6)
	)

	arrow_point2 = (
			end_pos[0] - arrow_size * math.cos(angle + math.pi / 6),
			end_pos[1] - arrow_size * math.sin(angle + math.pi / 6)

	)

	renderer.draw_line(end_pos, arrow_points)
	renderer.draw_line(arrow_point2, end_pos)



def draw_regular_polygon(renderer, center, n_vertices, radius):
	if n_vertices < 3:
		print("El polígono debe tener al menos 3 vértices")
		return
	
	angle_between_vertices = 2 * math.pi / n_vertices
	vertices = []
	
	for i in range(n_vertices):
		x = center[0] + radius * math.cos(i * angle_between_vertices)
		y = center[1] + radius * math.sin(i * angle_between_vertices)
		vertices.append((x, y))

	for i in range(n_vertices):
		renderer.fill_triangle(center, vertices[i], vertices[(i + 1) % n_vertices])



