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
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 250
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")


# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Reloj para controlar FPS
clock = pygame.time.Clock()
FPS = 60


# Cargar fuente
font = pygame.font.Font(None, 30)


# Archivo para guardar la puntuación más alta
HIGHSCORE_FILE = "Highscore.json"




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
    sound_object = pygame.mixer.Sound(tone)

    return sound_object


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
    sound_object = pygame.mixer.Sound(noise)

    return sound_object


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


# Crear Superficie
def create_surface_from_pixel_art(pixel_data, pixel_size=2, color=BLACK):

    height = len(pixel_data) * pixel_size
    width = len(pixel_data[0]) * pixel_size if height > 0 else 0

    surface = pygame.Surface((width, height), pygame.SRCALPHA)  # SRCALPHA para transparencia
    surface.fill((0, 0, 0, 0))  # Llenar con transparente

    for r, row_str in enumerate(pixel_data):
        for c, char_pixel in enumerate(row_str):
            if char_pixel == 'X':  # O cualquier carácter que uses para píxel sólido
                pygame.draw.rect(surface, color, (c * pixel_size, r * pixel_size, pixel_size, pixel_size))
    return surface




# Generar sonidos
game_sounds = generate_sounds()




# Clase para el Dinosaurio
class Animal(pygame.sprite.Sprite):


    # Inicializacion
    def __init__(self):

        super().__init__()

        dog_running_data_1 = [
            "      XXXXX   ",
            "     X     X  ",
            "     X     X  ",
            "     X   XXX  ",
            "  X  XX  X    ",
            "  XXXXX   X   ",
            "    XX    X   ",
            "   X       X  ",
            "  XX        X ",
            " X          X "
        ]

        dog_running_data_2 = [
            "      XXXXX   ",
            "     X     X  ",
            "     X     X  ",
            "     X   XXX  ",
            "     XX  X   X",
            "    XX   XXXXX",
            "    X    X    ",
            "   X      XX  ",
            "  XX        X ",
            " X          X "
        ]

        dog_ducking_data_1 = [
            "      XXXXX   ",
            "     X     X  ",
            "     X     X  ",
            "     X   XXX  ",
            "  X  XX  X    ",
            "  XXXXX   X   ",
            "    XX    X   ",
            "   X       X  ",
            "  XX        X ",
            " X          X "
        ]

        dog_ducking_data_2 = [
            "      XXXXX   ",
            "     X     X  ",
            "     X     X  ",
            "     X   XXX  ",
            "     XX  X   X",
            "    XX   XXXXX",
            "    X    X    ",
            "   X      XX  ",
            "  XX        X ",
            " X          X "
        ]

        dog_dead_data = [
            "      XXXXX   ",
            "     X     X  ",
            "     X     X  ",
            "     X   XXX  ",
            "  X  XX  X    ",
            "  XXXXX   X   ",
            "    XX    X   ",
            "   X       X  ",
            "  XX        X ",
            " X          X "
        ]

        pixel_render_size = 3

        # Crear Ojo
        def draw_eye(surface, data, eye_char='.', color=WHITE, pixel_s=pixel_render_size):
            for r, row_str in enumerate(data):
                for c, char_pixel in enumerate(row_str):
                    if char_pixel == eye_char:
                        pygame.draw.rect(surface, color, (c * pixel_s, r * pixel_s, pixel_s, pixel_s))

        # Crear Ojo Muerto
        def draw_dead_eyes(surface, data, eye_char='o', color=BLACK, pixel_s=pixel_render_size):
            for r, row_str in enumerate(data):
                for c, char_pixel in enumerate(row_str):
                    if char_pixel == eye_char:
                        pygame.draw.line(surface, color, (c * pixel_s, r * pixel_s),
                                         ((c + 1) * pixel_s - 1, (r + 1) * pixel_s - 1), 1)
                        pygame.draw.line(surface, color, ((c + 1) * pixel_s - 1, r * pixel_s),
                                         (c * pixel_s, (r + 1) * pixel_s - 1), 1)

        self.running_sprites = []
        self.ducking_sprites = []

        self.running_img1 = create_surface_from_pixel_art(dog_running_data_1, pixel_render_size, BLACK)
        draw_eye(self.running_img1, dog_running_data_1)
        self.running_sprites.append(self.running_img1)

        self.running_img2 = create_surface_from_pixel_art(dog_running_data_2, pixel_render_size, BLACK)
        draw_eye(self.running_img2, dog_running_data_2)
        self.running_sprites.append(self.running_img2)

        self.ducking_img1 = create_surface_from_pixel_art(dog_ducking_data_1, pixel_render_size, BLACK)
        draw_eye(self.ducking_img1, dog_ducking_data_1)
        self.ducking_sprites.append(self.ducking_img1)

        self.ducking_img2 = create_surface_from_pixel_art(dog_ducking_data_2, pixel_render_size, BLACK)
        draw_eye(self.ducking_img2, dog_ducking_data_2)
        self.ducking_sprites.append(self.ducking_img2)

        self.dead_img = create_surface_from_pixel_art(dog_dead_data, pixel_render_size, BLACK)
        draw_dead_eyes(self.dead_img, dog_dead_data, eye_char='o', color=BLACK, pixel_s=pixel_render_size)

        self.image = self.running_sprites[0]
        self.rect = self.image.get_rect()

        self.rect.x = 80
        self.base_y_running = SCREEN_HEIGHT - 80 - self.rect.height
        self.base_y_ducking = SCREEN_HEIGHT - 80 - self.ducking_sprites[0].get_rect().height + 5
        self.rect.y = self.base_y_running

        self.jump_velocity = 0
        self.ducking = False
        self.step_index = 0
        self.gravity = 1
        self.jumping = False
        self.alive = True


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


    # Pato
    def duck(self):

        self.image = self.ducking_sprites[self.step_index // 10]
        current_x = self.rect.x
        current_bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = current_x
        self.rect.bottom = current_bottom
        self.step_index += 1


    # Correr
    def run(self):

        self.image = self.running_sprites[self.step_index // 10]
        current_x = self.rect.x
        current_bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = current_x
        self.rect.bottom = current_bottom
        self.step_index += 1


    # Saltar
    def jump(self):

        self.image = self.running_sprites[0]

        if self.jumping:
            self.rect.y -= self.jump_velocity
            self.jump_velocity -= self.gravity
            if self.rect.y >= self.base_y_running:
                self.rect.y = self.base_y_running
                self.jumping = False
                self.jump_velocity = 0


    # Handle
    def handle_input(self, keys):

        if self.alive:
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not self.jumping:
                self.ducking = True
                self.play_jump_sound()
            elif (keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]) and not self.jumping and not self.ducking:
                self.jumping = True
                self.jump_velocity = 20
                self.ducking = False
                self.play_jump_sound()
            elif not (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not self.jumping:
                self.ducking = False


    # Reproducir sonido de salto
    def play_jump_sound(self):

        game_sounds["jump"].play()


    # Muerte
    def die(self):
        self.alive = False
        self.image = self.dead_img
        game_sounds["collision"].play()




# Clase para los obstáculos
class Obstacle(pygame.sprite.Sprite):


    # Inicializacion
    def __init__(self, image, type_obstacle):

        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.type = type_obstacle

        if self.type == "cactus":
            self.rect.y = SCREEN_HEIGHT - 120
        else:  # Es un pájaro
            self.rect.y = SCREEN_HEIGHT - 180 if random.randint(0, 1) == 0 else SCREEN_HEIGHT - 140
        self.rect.x = SCREEN_WIDTH


    # Actualizacion
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
        color = BLACK

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
        color = BLACK

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


    # Inicializacion
    def __init__(self, x_pos):

        super().__init__()

        self.image = self.create_ground_surface()
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = SCREEN_HEIGHT - 80


    # Crear superficie del suelo
    def create_ground_surface(self):

        ground_surface = pygame.Surface((SCREEN_WIDTH, 80))
        ground_surface.fill(WHITE)

        # Línea superior
        pygame.draw.line(ground_surface, BLACK, (0, 0), (SCREEN_WIDTH, 0), 2)

        # Dibujar algunas piedras pequeñas aleatorias
        for _ in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(10, 70)
            size = random.randint(1, 3)
            pygame.draw.rect(ground_surface, BLACK, (x, y, size, size))

        return ground_surface


    # Actualizar
    def update(self, game_speed):

        self.rect.x -= game_speed

        if self.rect.x <= -SCREEN_WIDTH:
            self.kill()




# Clase para la nube
class Cloud(pygame.sprite.Sprite):


    # Inicializacion
    def __init__(self):

        super().__init__()

        self.image = self.create_cloud_surface()
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.rect.y = random.randint(50, 100)


    # Crear nube
    def create_cloud_surface(self):

        cloud_surface = pygame.Surface((60, 20), pygame.SRCALPHA)
        color = BLACK

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


    # Inicializacion
    def __init__(self):

        self.game_speed = 10
        self.score = 0
        self.high_score = load_highscore()  # Cargar puntuación más alta
        self.start_time = pygame.time.get_ticks()
        self.last_milestone = 0  # Para rastrear cuando reproducir el sonido de punto

        # Crear grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.cloud_group = pygame.sprite.Group()

        # Crear el dinosaurio
        self.dinosaur = Animal()
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
            ground = Ground(SCREEN_WIDTH * i)
            self.ground_group.add(ground)
            self.all_sprites.add(ground)


    # Crear Obstaculo
    def create_obstacle(self):

        # Probabilidad de crear un cactus o un pájaro
        if random.randint(0, 4) == 0 and self.score > 100:  # Pájaros solo después de cierta puntuación
            bird_img1 = Obstacle.create_bird_surface(1)
            bird_img2 = Obstacle.create_bird_surface(2)
            bird = Obstacle(bird_img1, "bird")
            bird.images = [bird_img1, bird_img2]
            bird.current_image = 0
        else:
            cactus_img = Obstacle.create_cactus_surface()
            bird = Obstacle(cactus_img, "cactus")

        self.obstacle_group.add(bird)
        self.all_sprites.add(bird)


    # Crear Nube
    def create_cloud(self):

        cloud = Cloud()

        self.cloud_group.add(cloud)
        self.all_sprites.add(cloud)


    # Actualizar Record
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
        if self.score > self.high_score:
            self.high_score = self.score
            save_highscore(self.high_score)  # Guardar la nueva puntuación más alta

        # Aumentar la velocidad del juego con el tiempo
        if self.score > 0 and self.score % 100 == 0:
            self.game_speed += 0.5


    # Display Puntaje
    def display_score(self):

        # Mostrar puntuación actual
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        SCREEN.blit(score_text, (SCREEN_WIDTH - 150, 10))

        # Mostrar récord
        high_score_text = font.render(f"HI: {self.high_score}", True, BLACK)
        SCREEN.blit(high_score_text, (SCREEN_WIDTH - 150, 40))


    # Display Game Over
    def display_game_over(self):

        game_over_text = font.render("GAME OVER", True, BLACK)
        restart_text = font.render("Press SPACE to restart", True, BLACK)

        SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 20))
        SCREEN.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 20))


    # Display Start
    def display_start_screen(self):

        title_text = font.render("Game", True, BLACK)
        start_text = font.render("Press SPACE to start", True, BLACK)
        instructions_text = font.render("SPACE/UP: Jump, DOWN: Duck", True, BLACK)

        SCREEN.blit(title_text, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 50))
        SCREEN.blit(start_text, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2))
        SCREEN.blit(instructions_text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 50))

        # Mostrar récord actual en la pantalla de inicio
        if self.high_score > 0:
            record_text = font.render(f"Record: {self.high_score}", True, BLACK)
            SCREEN.blit(record_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 80))


    # Verificar Coliciones con Obstáculos
    def check_collision(self):

        # Verificar colisiones con obstáculos
        if pygame.sprite.spritecollide(self.dinosaur, self.obstacle_group, False, pygame.sprite.collide_mask):
            self.dinosaur.die()
            self.game_over = True


    # Animacion pajaros
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
        if self.score > self.high_score:
            self.high_score = self.score
            save_highscore(self.high_score)

        # Reiniciar juego manteniendo la puntuación más alta
        old_high_score = self.high_score
        self.__init__()
        self.high_score = old_high_score


    # Correr
    def run(self):

        # Bucle principal del juego
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Guardar puntuación antes de salir
                    if self.score > self.high_score:
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
                SCREEN.fill(WHITE)
                self.display_start_screen()
                pygame.display.update()
                clock.tick(FPS)
                continue

            # Fondo blanco
            SCREEN.fill(WHITE)

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
                    ground = Ground(SCREEN_WIDTH - 5)
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
            self.display_score()

            # Mostrar pantalla de game over si es necesario
            if self.game_over:
                self.display_game_over()

            # Actualizar pantalla
            pygame.display.update()

            # Controlar FPS
            clock.tick(FPS)




# Iniciar el juego
if __name__ == "__main__":
    game = Game()
    game.run()