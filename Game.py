import numpy as np
import pygame
import random
import json
import sys
import os


# Inicializar pygame y el módulo de sonido
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)


# Configuración de la ventana
display_width = 750
display_height = 250
SCREEN = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Dino PyGame")


# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)


# Variables para control de día/noche
is_night = False
current_colors = {
    'background': WHITE,
    'foreground': BLACK,
    'cloud': LIGHT_GRAY
}


# Reloj para controlar FPS
clock = pygame.time.Clock()
FPS = 60


# Cargar fuente
font = pygame.font.Font(None, 30)


# Archivo para guardar la puntuación más alta
HIGHSCORE_FILE = "Highscore.json"


# Función para actualizar colores según el estado día/noche
def update_colors(score):

    global is_night, current_colors

    # Cambiar cada 100 puntos
    is_night = (score // 100) % 2 == 1
    if is_night:
        current_colors['background'] = BLACK
        current_colors['foreground'] = WHITE
        current_colors['cloud'] = DARK_GRAY
    else:
        current_colors['background'] = WHITE
        current_colors['foreground'] = BLACK
        current_colors['cloud'] = LIGHT_GRAY


# Función para generar sonidos procedurales
def generate_sounds():

    sounds = {}

    # Sonido de salto (tono ascendente)
    jump_sound = generate_tone(frequency=440, duration=0.1, volume=0.3, fade=True)
    sounds["jump"] = jump_sound

    # Sonido de colisión (ruido blanco)
    collision_sound = generate_noise(duration=0.3, volume=0.4)
    sounds["collision"] = collision_sound

    # Sonido de punto (ping corto)
    point_sound = generate_tone(frequency=880, duration=0.05, volume=0.2)
    sounds["point"] = point_sound

    return sounds


# Genera un tono simple usando numpy y lo convierte en un objeto Sound de Pygame
def generate_tone(frequency=440, duration=0.1, volume=0.5, fade=False):
    
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * 2 * np.pi * t) * volume

    if fade:
        # Aplicar un fade-out al sonido
        fade_samples = int(sample_rate * duration * 0.5)
        fade_out = np.linspace(1.0, 0.0, fade_samples)
        tone[-fade_samples:] *= fade_out

    # Asegurarse de que los valores estén entre -1 y 1
    tone = np.clip(tone, -1, 1)

    # Convertir a formato de audio de pygame
    tone = (tone * 32767).astype(np.int16)

    # Crear objeto Sound de pygame
    sound_obj = pygame.mixer.Sound(tone)

    return sound_obj


# Genera ruido blanco usando numpy y lo convierte en un objeto Sound de Pygame
def generate_noise(duration=0.2, volume=0.5):

    sample_rate = 44100
    samples = int(sample_rate * duration)

    # Generar ruido blanco
    noise = np.random.uniform(-1, 1, samples) * volume

    # Aplicar un fade-out al ruido
    fade_samples = int(sample_rate * duration * 0.5)
    fade_out = np.linspace(1.0, 0.0, fade_samples)
    noise[-fade_samples:] *= fade_out

    # Convertir a formato de audio de pygame
    noise = (noise * 32767).astype(np.int16)

    # Crear objeto Sound de pygame
    sound_obj = pygame.mixer.Sound(noise)

    return sound_obj


# Cargar o crear el archivo de puntuación más alta
def load_highscore():

    try:
        with open(HIGHSCORE_FILE, 'r') as file:
            data = json.load(file)
            return data.get('highscore', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si el archivo no existe o está corrupto, devolver 0
        return 0


# Guardar la puntuación más alta
def save_highscore(score):

    data = {'highscore': score}
    with open(HIGHSCORE_FILE, 'w') as file:
        json.dump(data, file)


# Generar sonidos
game_sounds = generate_sounds()




# Clase para el Dinosaurio
class Dinosaur(pygame.sprite.Sprite):


    # Inicialización
    def __init__(self):

        super().__init__()

        # Inicializar variables de estado
        self.jump_speed = 0
        self.ducking = False
        self.step_index = 0
        self.gravity = 1
        self.jumping = False
        self.alive = True
        self.pixel_render_size = 3

        # Datos de los sprites
        self.run_data_1 = [
            "     XXXXXX    ",
            "   XX      X   ",
            "  XX        X  ",
            "XXX       XXX  ",
            "X X         x  ",
            "X X          X ",
            "XXX          X ",
            "  X    XX    X ",
            "  XX  X  X   X ",
            "   XXXX   XXX "
        ]

        self.run_data_2 = [
            "     XXXXXX    ",
            "   XX      X   ",
            "  XX        X  ",
            "XXX       XXX  ",
            "X X          X ",
            "XXX          X ",
            "  X    XX    X ",
            "  XX  X  X   X ",
            "   XXXX   XXX "
        ]

        self.duck_data_1 = [
            "     XXXXX    ",
            "   XX     X   ",
            "  XX       X  ",
            "XXX      XXX  ",
            "XXX         X ",
            "  X    XX    X ",
            "  XX  X  X   X ",
            "   XXXX   XXX "
        ]

        self.duck_data_2 = [
            "     XXXXX    ",
            "   XX     X   ",
            "  XX       X  ",
            "XXX      XXX  ",
            "XXX         X ",
            "  X    XX    X ",
            "  XX  X  X   X ",
            "   XXXX   XXX "
        ]

        self.dead_data = [
            "  X  XXXXXX   X ",
            "   XX    * X X  ",
            "  XX        X  ",
            "XXX  *    XXX  ",
            "X X         x  ",
            "X X    *     X ",
            "XXX  X     * X ",
            "  X    XX    X ",
            "  XX  X  X   X ",
            "X  XXXX   XXX "
        ]

        # Generar sprites iniciales
        self.regenerate_sprites()

        # Configurar posición inicial
        self.rect = self.image.get_rect()
        self.rect.x = 80
        self.run_base_y = display_height - 80 - self.rect.height
        self.duck_base_y = display_height - 80 - self.duck_sprites[0].get_rect().height + 5
        self.rect.y = self.run_base_y


    # Actualizar
    def update(self):

        if self.alive:
            if self.ducking:
                self.duck()
            elif self.jumping:
                self.jump()
            else:
                self.run()

            if self.step_index >= 20:
                self.step_index = 0


    # Agacharse
    def duck(self):

        self.image = self.duck_sprites[self.step_index // 10]
        current_x = self.rect.x
        current_bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = current_x
        self.rect.bottom = current_bottom
        self.step_index += 1


    # Correr
    def run(self):

        self.image = self.run_sprites[self.step_index // 10]
        current_x = self.rect.x
        current_bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = current_x
        self.rect.bottom = current_bottom
        self.step_index += 1


    # Saltar
    def jump(self):

        self.image = self.run_sprites[0]

        if self.jumping:
            self.rect.y -= self.jump_speed
            self.jump_speed -= self.gravity
            if self.rect.y >= self.run_base_y:
                self.rect.y = self.run_base_y
                self.jumping = False
                self.jump_speed = 0


    # Manejar entrada
    def handle_input(self, keys):

        if self.alive:
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not self.jumping:
                self.ducking = True
                self.play_jump_sound()
            elif (keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]) and not self.jumping and not self.ducking:
                self.jumping = True
                self.jump_speed = 20
                self.ducking = False
                self.play_jump_sound()
            elif not (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not self.jumping:
                self.ducking = False


    # Reproducir sonido de salto
    def play_jump_sound(self):
        
        game_sounds["jump"].play()


    # Morir
    def die(self):

        self.alive = False
        self.image = self.dead_image
        game_sounds["collision"].play()


    # Regenerar todos los sprites con los colores actuales
    def regenerate_sprites(self):

        self.run_sprites = []
        self.duck_sprites = []

        self.run_image1 = self.create_surface_from_pixel_art(self.run_data_1, self.pixel_render_size)
        self.draw_eye(self.run_image1, self.run_data_1)
        self.run_sprites.append(self.run_image1)

        self.run_image2 = self.create_surface_from_pixel_art(self.run_data_2, self.pixel_render_size)
        self.draw_eye(self.run_image2, self.run_data_2)
        self.run_sprites.append(self.run_image2)

        self.duck_image1 = self.create_surface_from_pixel_art(self.duck_data_1, self.pixel_render_size)
        self.draw_eye(self.duck_image1, self.duck_data_1)
        self.duck_sprites.append(self.duck_image1)

        self.duck_image2 = self.create_surface_from_pixel_art(self.duck_data_2, self.pixel_render_size)
        self.draw_eye(self.duck_image2, self.duck_data_2)
        self.duck_sprites.append(self.duck_image2)

        self.dead_image = self.create_surface_from_pixel_art(self.dead_data, self.pixel_render_size)
        self.draw_dead_eyes(self.dead_image, self.dead_data)

        # Actualizar la imagen actual
        if self.alive:
            if self.ducking:
                self.image = self.duck_sprites[self.step_index // 10]
            else:
                self.image = self.run_sprites[self.step_index // 10]
        else:
            self.image = self.dead_image

    # Crear superficie de pixel de un archivo de texto
    def create_surface_from_pixel_art(self, pixel_data, pixel_size=2):

        height = len(pixel_data) * pixel_size
        width = len(pixel_data[0]) * pixel_size if height > 0 else 0

        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

        for r, row in enumerate(pixel_data):
            for c, char in enumerate(row):
                if char == 'X':
                    pygame.draw.rect(surface, current_colors['foreground'], (c * pixel_size, r * pixel_size, pixel_size, pixel_size))
        return surface


    # Dibujar los ojos
    def draw_eye(self, surface, data, eye_char='.', pixel_size=None):

        if pixel_size is None:
            pixel_size = self.pixel_render_size
        for r, row in enumerate(data):
            for c, char in enumerate(row):
                if char == eye_char:
                    pygame.draw.rect(surface, current_colors['foreground'], (c * pixel_size, r * pixel_size, pixel_size, pixel_size))


    # Dibujar los ojos al morir
    def draw_dead_eyes(self, surface, data, eye_char='o', pixel_size=None):

        if pixel_size is None:
            pixel_size = self.pixel_render_size
        for r, row in enumerate(data):
            for c, char in enumerate(row):
                if char == eye_char:
                    pygame.draw.line(surface, current_colors['foreground'], (c * pixel_size, r * pixel_size),
                                     ((c + 1) * pixel_size - 1, (r + 1) * pixel_size - 1), 1)
                    pygame.draw.line(surface, current_colors['foreground'], ((c + 1) * pixel_size - 1, r * pixel_size),
                                     (c * pixel_size, (r + 1) * pixel_size - 1), 1)




# Clase para los obstáculos
class Obstacle(pygame.sprite.Sprite):


    # Inicialización
    def __init__(self, image, obstacle_type):

        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.type = obstacle_type

        if self.type == "cactus":
            self.rect.y = display_height - 120
        else:  # Es un pájaro
            self.rect.y = display_height - 180 if random.randint(0, 1) == 0 else display_height - 140
        self.rect.x = display_width


    # Actualización
    def update(self, game_speed):

        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            self.kill()


    # Crear cactus
    @staticmethod
    def create_cactus_surface():

        height = random.randint(40, 60)
        width = 20
        cactus_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        color = current_colors['foreground']

        # Tronco principal
        pygame.draw.rect(cactus_surface, color, (8, 0, 4, height))

        # Brazos
        arm_height = random.randint(15, 25)
        pygame.draw.rect(cactus_surface, color, (0, height // 3, 8, 4))  # Brazo izquierdo
        pygame.draw.rect(cactus_surface, color, (0, height // 3, 4, arm_height))

        pygame.draw.rect(cactus_surface, color, (12, height // 2, 8, 4))  # Brazo derecho
        pygame.draw.rect(cactus_surface, color, (16, height // 2, 4, arm_height))

        return cactus_surface


    # Crear pájaro con alas en diferentes posiciones
    @staticmethod
    def create_bird_surface(step):

        bird_surface = pygame.Surface((40, 20), pygame.SRCALPHA)
        color = current_colors['foreground']

        # Cuerpo
        pygame.draw.rect(bird_surface, color, (15, 10, 10, 10))

        # Cabeza
        pygame.draw.rect(bird_surface, color, (30, 5, 10, 10))

        # Pico
        pygame.draw.rect(bird_surface, color, (40, 8, 3, 4))

        # Alas (diferentes según el paso de animación)
        if step == 1:
            pygame.draw.rect(bird_surface, color, (15, 5, 15, 3))  # Alas arriba
        else:
            pygame.draw.rect(bird_surface, color, (15, 15, 15, 3))  # Alas abajo

        return bird_surface




# Clase para el suelo
class Ground(pygame.sprite.Sprite):


    # Inicialización
    def __init__(self, x_pos):

        super().__init__()

        self.image = self.create_ground_surface()
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = display_height - 80


    # Crear superficie del suelo
    def create_ground_surface(self):

        ground_surface = pygame.Surface((display_width, 80))
        ground_surface.fill(current_colors['background'])

        # Línea superior
        pygame.draw.line(ground_surface, current_colors['foreground'], (0, 0), (display_width, 0), 2)

        # Dibujar algunas piedras pequeñas aleatorias
        for _ in range(20):
            x = random.randint(0, display_width)
            y = random.randint(10, 70)
            size = random.randint(1, 3)
            pygame.draw.rect(ground_surface, current_colors['foreground'], (x, y, size, size))

        return ground_surface


    # Actualizar
    def update(self, game_speed):

        self.rect.x -= game_speed

        if self.rect.x <= -display_width:
            self.kill()




# Clase para la nube
class Cloud(pygame.sprite.Sprite):


    # Inicialización
    def __init__(self):

        super().__init__()

        self.image = self.create_cloud_surface()
        self.rect = self.image.get_rect()
        self.rect.x = display_width + random.randint(800, 1000)
        self.rect.y = random.randint(50, 100)


    # Crear nube
    def create_cloud_surface(self):

        cloud_surface = pygame.Surface((60, 20), pygame.SRCALPHA)
        color = current_colors['cloud']

        # Forma básica de nube
        pygame.draw.rect(cloud_surface, color, (10, 10, 40, 10))
        pygame.draw.rect(cloud_surface, color, (5, 5, 10, 10))
        pygame.draw.rect(cloud_surface, color, (20, 5, 15, 5))
        pygame.draw.rect(cloud_surface, color, (45, 5, 10, 10))

        return cloud_surface


    # Actualizar
    def update(self, game_speed):

        self.rect.x -= game_speed // 2

        if self.rect.x < -self.rect.width:
            self.kill()




# Clase principal del juego
class Game:


    # Inicialización
    def __init__(self):

        self.game_speed = 10
        self.score = 0
        self.highscore = load_highscore()  # Cargar puntuación más alta
        self.start_time = pygame.time.get_ticks()
        self.last_milestone = 0  # Para rastrear cuando reproducir el sonido de punto

        # Crear grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.cloud_group = pygame.sprite.Group()

        # Crear el dinosaurio
        self.dinosaur = Dinosaur()
        self.all_sprites.add(self.dinosaur)

        # Crear el suelo inicial
        self.create_ground()

        # Control de tiempo para la generación de obstáculos
        self.obstacle_timer = 0
        self.cloud_timer = 0

        # Estado del juego
        self.game_over = False
        self.game_started = False


    # Crear el suelo para que cubra toda la pantalla
    def create_ground(self):

        for i in range(2):
            ground = Ground(display_width * i)
            self.ground_group.add(ground)
            self.all_sprites.add(ground)


    # Crear Obstáculo
    def create_obstacle(self):

        # Probabilidad de crear un cactus o un pájaro
        if random.randint(0, 4) == 0 and self.score > 100:  # Pájaros solo después de cierta puntuación
            bird_image1 = Obstacle.create_bird_surface(1)
            bird_image2 = Obstacle.create_bird_surface(2)
            bird = Obstacle(bird_image1, "bird")
            bird.images = [bird_image1, bird_image2]
            bird.current_image = 0
        else:
            cactus_image = Obstacle.create_cactus_surface()
            bird = Obstacle(cactus_image, "cactus")

        self.obstacle_group.add(bird)
        self.all_sprites.add(bird)


    # Crear Nube
    def create_cloud(self):

        cloud = Cloud()
        self.cloud_group.add(cloud)
        self.all_sprites.add(cloud)


    # Actualizar Puntuación
    def update_score(self):

        current_time = pygame.time.get_ticks()
        self.score = int((current_time - self.start_time) / 100)

        # Verificar si se ha alcanzado un nuevo hito de puntuación (cada 100 puntos)
        current_milestone = self.score // 100

        if current_milestone > self.last_milestone:
            # Reproducir sonido de punto
            game_sounds["point"].play()
            self.last_milestone = current_milestone

        # Actualizar la puntuación más alta si es necesario
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)  # Guardar la nueva puntuación más alta

        # Aumentar la velocidad del juego con el tiempo
        if self.score > 0 and self.score % 100 == 0:
            self.game_speed += 0.5


    # Mostrar Puntuación
    def show_score(self):

        # Mostrar puntuación actual
        score_text = font.render(f"Score: {self.score}", True, current_colors['foreground'])
        SCREEN.blit(score_text, (display_width - 150, 10))

        # Mostrar récord
        highscore_text = font.render(f"Highscore: {self.highscore}", True, current_colors['foreground'])
        SCREEN.blit(highscore_text, (display_width - 150, 40))


    # Mostrar Game Over
    def show_game_over(self):

        game_over_text = font.render("GAME OVER", True, current_colors['foreground'])
        restart_text = font.render("Press SPACE to restart", True, current_colors['foreground'])

        SCREEN.blit(game_over_text, (display_width // 2 - 100, display_height // 2 - 20))
        SCREEN.blit(restart_text, (display_width // 2 - 150, display_height // 2 + 20))


    # Mostrar Pantalla de Inicio
    def show_start_screen(self):

        title_text = font.render("Dino PyGame", True, BLACK)
        start_text = font.render("Press SPACE to start", True, BLACK)
        instructions_text = font.render("SPACE/UP: Jump, DOWN: Duck", True, BLACK)

        SCREEN.blit(title_text, (display_width // 2 - 70, display_height // 2 - 50))
        SCREEN.blit(start_text, (display_width // 2 - 110, display_height // 2))
        SCREEN.blit(instructions_text, (display_width // 2 - 150, display_height // 2 + 50))

        # Mostrar récord actual en la pantalla de inicio
        if self.highscore > 0:
            highscore_text = font.render(f"Highscore: {self.highscore}", True, current_colors['foreground'])
            SCREEN.blit(highscore_text, (display_width // 2 - 80, display_height // 2 + 80))


    # Verificar Colisiones con Obstáculos
    def check_collision(self):

        # Verificar colisiones con obstáculos
        if pygame.sprite.spritecollide(self.dinosaur, self.obstacle_group, False, pygame.sprite.collide_mask):
            self.dinosaur.die()
            self.game_over = True


    # Animación pájaros
    def animate_birds(self):

        # Animar los pájaros
        for obstacle in self.obstacle_group:
            if hasattr(obstacle, 'type') and obstacle.type == "bird" and hasattr(obstacle, 'images'):
                # Cambiar imagen cada cierto tiempo para animar
                if pygame.time.get_ticks() % 200 < 100:
                    obstacle.image = obstacle.images[0]
                else:
                    obstacle.image = obstacle.images[1]


    # Reiniciar Juego
    def reset_game(self):

        # Guardar puntuación máxima antes de reiniciar
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

        # Reiniciar juego manteniendo la puntuación más alta
        previous_highscore = self.highscore
        self.__init__()
        self.highscore = previous_highscore


    # Ejecutar
    def run(self):
        
        # Bucle principal del juego
        running = True
        last_score = -1  # Para detectar cambios en la puntuación
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Guardar puntuación antes de salir
                    if self.score > self.highscore:
                        save_highscore(self.score)
                    running = False
                    pygame.quit()
                    sys.exit()
                
                # Iniciar o reiniciar el juego con la barra espaciadora
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        if not self.game_started:
                            self.game_started = True
                            self.start_time = pygame.time.get_ticks()
                        elif self.game_over:
                            self.reset_game()
            
            # Obtener teclas presionadas
            keys = pygame.key.get_pressed()
            
            # Pantalla de inicio
            if not self.game_started:
                SCREEN.fill(current_colors['background'])
                self.show_start_screen()
                pygame.display.update()
                clock.tick(FPS)
                continue
            
            # Fondo según el estado día/noche
            SCREEN.fill(current_colors['background'])
            
            # Actualizar colores según la puntuación
            update_colors(self.score)
            
            # Regenerar sprites del dinosaurio si cambió el modo día/noche
            if self.score // 100 != last_score // 100:
                self.dinosaur.regenerate_sprites()
                last_score = self.score
            
            # Manejar entrada del dinosaurio
            self.dinosaur.handle_input(keys)
            
            # Actualizar sprites solo si el juego no ha terminado
            if not self.game_over:
                # Generar nubes
                self.cloud_timer += 1
                if self.cloud_timer >= 100:
                    self.create_cloud()
                    self.cloud_timer = 0
                
                # Generar obstáculos
                self.obstacle_timer += 1
                if self.obstacle_timer >= 50 + random.randint(0, 50):
                    self.create_obstacle()
                    self.obstacle_timer = 0
                
                # Verificar si se necesita crear más suelo
                if len(self.ground_group) < 2:
                    ground = Ground(display_width - 5)
                    self.ground_group.add(ground)
                    self.all_sprites.add(ground)
                
                # Actualizar puntuación
                self.update_score()
                
                # Animar pájaros
                self.animate_birds()
                
                # Actualizar todos los sprites
                for sprite in self.all_sprites:
                    if isinstance(sprite, (Ground, Obstacle, Cloud)):
                        sprite.update(self.game_speed)
                    else:
                        sprite.update()
                
                # Comprobar colisiones
                self.check_collision()
            
            # Dibujar todos los sprites
            self.all_sprites.draw(SCREEN)
            
            # Mostrar puntuación
            self.show_score()
            
            # Mostrar pantalla de game over si es necesario
            if self.game_over:
                self.show_game_over()
            
            # Actualizar pantalla
            pygame.display.update()
            
            # Controlar FPS
            clock.tick(FPS)


# Iniciar el juego
if __name__ == "__main__":
    game = Game()
    game.run()