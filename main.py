import pygame
from pygame.locals import *
from random import randint
import math as m

# Inicializar Pygame y la fuente para el texto
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Consolas', 18)

# --- CONFIGURACIÓN DE LA SIMULACIÓN ---
winSize = (800, 800)
display = pygame.display.set_mode(winSize)
pygame.display.set_caption("Proyecto calculo vectorial")
fps = 60
clock = pygame.time.Clock()
simSpeed = 1

# Estado de la simulación
paused = True # Inicia pausado para analizar desde el principio

# -- CUERPOS CELESTES Y CONSTANTES FÍSICAS --
# Usamos pygame.Vector2 para facilitar las operaciones vectoriales
bodies = {
    "sun": {
        "col": (255, 255, 0),
        "rad": 30,
        "mass": 20000, # Aumentamos la masa del sol para mayor atracción
        "pos": pygame.Vector2(400, 400),
        "vel": pygame.Vector2(0, 0)
    },
    "earth": {
        "col": (100, 100, 255),
        "rad": 8,
        "mass": 1,
        "pos": pygame.Vector2(600, 400),
        "vel": pygame.Vector2(0, -2.5) # Reducimos significativamente la velocidad
    }
}
G = 0.1 # La constante G se mantiene igual
# --- ELEMENTOS VISUALES ---
stars = [((randint(150, 200), randint(150, 200), randint(150, 200)), 
          (randint(1, winSize[0]), randint(1, winSize[1])), 
          randint(1, 2)) for _ in range(250)]

def draw_background():
    for star in stars:
        pygame.draw.circle(display, star[0], star[1], star[2])

def draw_bodies():
    for body in bodies.values():
        pygame.draw.circle(display, body['col'], body['pos'], body['rad'])

# --- NUEVA FUNCIÓN PARA DIBUJAR VECTORES ---
def draw_vector(start_pos, vector, color, scale=1.0, width=2):
    """Dibuja una flecha representando un vector."""
    if vector.length() == 0: return
    end_pos = start_pos + vector * scale
    pygame.draw.line(display, color, start_pos, end_pos, width)
    # Dibuja la punta de la flecha
    angle = m.atan2(vector.y, vector.x)
    p1 = (end_pos.x - 10 * m.cos(angle - m.pi / 6), end_pos.y - 10 * m.sin(angle - m.pi / 6))
    p2 = (end_pos.x - 10 * m.cos(angle + m.pi / 6), end_pos.y - 10 * m.sin(angle + m.pi / 6))
    pygame.draw.polygon(display, color, [end_pos, p1, p2])

# --- LÓGICA DE LA FÍSICA Y CÁLCULOS VECTORIALES ---
def update_physics():
    sun = bodies['sun']
    earth = bodies['earth']

    # Vector de Posición (r): Va del Sol a la Tierra
    r_vec = earth['pos'] - sun['pos']
    distance = r_vec.length()
    if distance == 0: return

    # Vector de Fuerza Gravitacional (Fg): Apunta desde la Tierra hacia el Sol
    # F = G * (m1*m2) / r^2
    force_magnitude = G * (sun['mass'] * earth['mass']) / (distance * distance)
    # La dirección es opuesta al vector de posición (hacia el Sol)
    force_vec = -r_vec.normalize() * force_magnitude

    # Vector de Aceleración (a = F/m)
    accel_vec = force_vec / earth['mass']

    # Solo actualizamos si la simulación no está pausada
    if not paused:
        # Actualizar el Vector Velocidad (v_nuevo = v_viejo + a*dt)
        earth['vel'] += accel_vec * simSpeed
        # Actualizar el Vector Posición (p_nuevo = p_viejo + v*dt)
        earth['pos'] += earth['vel'] * simSpeed

    # Devolvemos los vectores para poder visualizarlos
    return r_vec, earth['vel'], force_vec

# --- BUCLE PRINCIPAL DE LA SIMULACIÓN ---
run = True
while run:
    # Dibujar elementos estáticos
    display.fill((0, 0, 0))
    draw_background()
    draw_bodies()

    # Actualizar física y obtener vectores
    r_vec, v_vec, f_vec = update_physics()
    
    # --- VISUALIZACIÓN DE VECTORES Y DATOS (SOLO EN PAUSA) ---
    if paused:
        sun_pos = bodies['sun']['pos']
        earth_pos = bodies['earth']['pos']
        
        # 1. Visualizar Vector Posición (r) - en blanco
        draw_vector(sun_pos, r_vec, (255, 255, 255), scale=1.0, width=2)
        
        # 2. Visualizar Vector Velocidad (v) - en verde
        draw_vector(earth_pos, v_vec, (0, 255, 0), scale=20.0, width=3) # Escala para mejor visibilidad
        
        # 3. Visualizar Vector Fuerza/Aceleración (F/a) - en rojo
        draw_vector(earth_pos, f_vec, (255, 0, 0), scale=500.0, width=3) # Escala para mejor visibilidad

        # Mostrar texto con los valores
        text_r = font.render(f"Posición r: ({r_vec.x:.1f}, {r_vec.y:.1f}) | Dist: {r_vec.length():.1f}", True, (255, 255, 255))
        text_v = font.render(f"Velocidad v: ({v_vec.x:.2f}, {v_vec.y:.2f}) | Rapidez: {v_vec.length():.2f}", True, (0, 255, 0))
        text_f = font.render(f"Fuerza Fg: ({f_vec.x:.3f}, {f_vec.y:.3f}) | Mag: {f_vec.length():.3f}", True, (255, 0, 0))
        text_paused = font.render("PAUSADO", True, (200, 200, 0))

        display.blit(text_r, (10, 10))
        display.blit(text_v, (10, 35))
        display.blit(text_f, (10, 60))
        display.blit(text_paused, (winSize[0] // 2 - 50, 10))

    # Control de FPS y actualización de pantalla
    clock.tick(fps)
    pygame.display.update()

    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == K_SPACE: # Activar/desactivar pausa
                paused = not paused
                pygame.display.set_caption(f"Laboratorio Orbital | {'PAUSADO' if paused else 'EN CURSO'}")

pygame.quit()