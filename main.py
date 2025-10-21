import pygame
from pygame.locals import *
from random import randint
import math as m

# Inicializar Pygame y la fuente para el texto
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Consolas', 18)
angle_font = pygame.font.SysFont('Consolas', 16, bold=True)

# --- CONFIGURACIÓN DE LA SIMULACIÓN ---
winSize = (800, 800)
display = pygame.display.set_mode(winSize)
pygame.display.set_caption("Laboratorio Orbital | ESPACIO para pausar")
fps = 60
clock = pygame.time.Clock()
simSpeed = 1

# Estado de la simulación
paused = True # Inicia pausado

# --- CUERPOS CELESTES Y CONSTANTES FÍSICAS ---
bodies = {
    "sun": {
        "col": (255, 255, 0),
        "rad": 30,
        "mass": 20000, # Masa aumentada para una órbita estable
        "pos": pygame.Vector2(400, 400),
        "vel": pygame.Vector2(0, 0)
    },
    "earth": {
        "col": (100, 100, 255),
        "rad": 8,
        "mass": 1,
        "pos": pygame.Vector2(600, 400),
        "vel": pygame.Vector2(0, -3.5) # Velocidad reducida
    }
}
G = 0.1 # Constante de gravitación

# --- ELEMENTOS VISUALES ---
# stars = [((randint(150, 200), randint(150, 200), randint(150, 200)), 
#           (randint(1, winSize[0]), randint(1, winSize[1])), 
#           randint(1, 2)) for _ in range(250)]

# def draw_background():
#     for star in stars:
#         pygame.draw.circle(display, star[0], star[1], star[2])

def draw_bodies():
    for body in bodies.values():
        pygame.draw.circle(display, body['col'], body['pos'], body['rad'])

def draw_vector(start_pos, vector, color, scale=1.0, width=2):
    if vector.length() == 0: return
    end_pos = start_pos + vector * scale
    pygame.draw.line(display, color, start_pos, end_pos, width)
    angle = m.atan2(vector.y, vector.x)
    p1 = (end_pos.x - 10 * m.cos(angle - m.pi / 6), end_pos.y - 10 * m.sin(angle - m.pi / 6))
    p2 = (end_pos.x - 10 * m.cos(angle + m.pi / 6), end_pos.y - 10 * m.sin(angle + m.pi / 6))
    pygame.draw.polygon(display, color, [end_pos, p1, p2])

# --- NUEVA FUNCIÓN PARA DIBUJAR EL ÁNGULO ---
def draw_angle(origin, v_vec, f_vec, color=(255, 165, 0)):
    """Dibuja el ángulo entre el vector de velocidad y el de fuerza."""
    if v_vec.length() == 0 or f_vec.length() == 0: return
    
    # Calcular los ángulos de cada vector respecto al eje X
    angle_v = m.atan2(-v_vec.y, v_vec.x) # Invertimos 'y' porque Pygame crece hacia abajo
    angle_f = m.atan2(-f_vec.y, f_vec.x)
    
    # Dibujar el arco
    arc_rect = pygame.Rect(origin.x - 40, origin.y - 40, 80, 80)
    pygame.draw.arc(display, color, arc_rect, angle_f, angle_v, 2)

    # Calcular y mostrar el valor del ángulo
    angle_degrees = abs(v_vec.angle_to(f_vec))
    angle_text = angle_font.render(f"{angle_degrees:.1f}°", True, color)
    
    # Posicionar el texto en el punto medio del arco
    mid_angle = (angle_v + angle_f) / 2
    text_pos = origin + pygame.Vector2(m.cos(mid_angle), -m.sin(mid_angle)) * 55
    display.blit(angle_text, angle_text.get_rect(center=text_pos))


# --- LÓGICA DE LA FÍSICA ---
def update_physics():
    sun = bodies['sun']
    earth = bodies['earth']
    r_vec = earth['pos'] - sun['pos']
    distance = r_vec.length()
    if distance == 0: return
    force_magnitude = G * (sun['mass'] * earth['mass']) / (distance * distance)
    force_vec = -r_vec.normalize() * force_magnitude
    accel_vec = force_vec / earth['mass']

    if not paused:
        earth['vel'] += accel_vec * simSpeed
        earth['pos'] += earth['vel'] * simSpeed

    return r_vec, earth['vel'], force_vec

# --- BUCLE PRINCIPAL ---
run = True
while run:
    display.fill((0, 0, 0))
 #   draw_background()
    draw_bodies()

    r_vec, v_vec, f_vec = update_physics()
    
    if paused:
        sun_pos = bodies['sun']['pos']
        earth_pos = bodies['earth']['pos']
        
        # Visualizar Vectores
        draw_vector(sun_pos, r_vec, (255, 255, 255), scale=1.0)
        draw_vector(earth_pos, v_vec, (0, 255, 0), scale=20.0)
        draw_vector(earth_pos, f_vec, (255, 0, 0), scale=500.0)
        
        # --- Visualizar el Ángulo (NUEVO) ---
        draw_angle(earth_pos, v_vec, f_vec, color=(255, 165, 0))

        # Mostrar texto con datos
        text_r = font.render(f"Posición r: ({r_vec.x:.1f}, {r_vec.y:.1f}) | Dist: {r_vec.length():.1f}", True, (255, 255, 255))
        text_v = font.render(f"Velocidad v: ({v_vec.x:.2f}, {v_vec.y:.2f}) | Rapidez: {v_vec.length():.2f}", True, (0, 255, 0))
        text_f = font.render(f"Fuerza Fg: ({f_vec.x:.3f}, {f_vec.y:.3f}) | Mag: {f_vec.length():.3f}", True, (255, 0, 0))
        text_paused = font.render("PAUSADO", True, (255, 255, 0))

        display.blit(text_r, (10, 10))
        display.blit(text_v, (10, 35))
        display.blit(text_f, (10, 60))
        display.blit(text_paused, (winSize[0] // 2 - 50, 10))

    clock.tick(fps)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                paused = not paused
                pygame.display.set_caption(f"Laboratorio Orbital | {'PAUSADO' if paused else 'EN CURSO'}")

pygame.quit()