import pygame
import random
import sys
import os




# Inicializar pygame
pygame.init()


# Configuración de la ventana
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 250
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Pixel")


# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Reloj para controlar FPS
clock = pygame.time.Clock()
FPS = 60


# Cargar fuente
font = pygame.font.Font(None, 30)




# Clase para el Dinosaurio
class Dinosaur(pygame.sprite.Sprite):


    def __init__(self):
        super().__init__()

        # Imágenes del dinosaurio (serán reemplazadas con pixelart)
        self.running_sprites = []
        self.ducking_sprites = []

        # Para este ejemplo, creamos dinosaurio con pixelart básico
        self.running_img1 = self.create_dino_surface(False, 1)
        self.running_img2 = self.create_dino_surface(False, 2)
        self.ducking_img1 = self.create_dino_surface(True, 1)
        self.ducking_img2 = self.create_dino_surface(True, 2)
        self.dead_img = self.create_dino_surface(False, 0)

        self.running_sprites.append(self.running_img1)
        self.running_sprites.append(self.running_img2)
        self.ducking_sprites.append(self.ducking_img1)
        self.ducking_sprites.append(self.ducking_img2)

        self.image = self.running_sprites[0]
        self.rect = self.image.get_rect()
        self.rect.x = 80
        self.rect.y = SCREEN_HEIGHT - 140

        self.jump_velocity = 0
        self.ducking = False
        self.step_index = 0
        self.gravity = 1.5
        self.jumping = False
        self.alive = True


    def create_dino_surface(self, ducking, step):
        # Crear imagen pixelart del dinosaurio
        width = 40 if ducking else 20
        height = 20 if ducking else 40
        dino_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        if ducking:
            # Dibujar dinosaurio agachado
            color = BLACK
            # Cuerpo
            pygame.draw.rect(dino_surface, color, (0, 10, 80, 30))
            # Cabeza
            pygame.draw.rect(dino_surface, color, (30, 0, 10, 10))
            # Ojo
            pygame.draw.rect(dino_surface, WHITE, (35, 2, 2, 2))

            # Piernas (dependiendo del step)
            if step == 1:
                pygame.draw.rect(dino_surface, color, (5, 18, 5, 2))
                pygame.draw.rect(dino_surface, color, (20, 18, 5, 2))
            elif step == 2:
                pygame.draw.rect(dino_surface, color, (10, 18, 5, 2))
                pygame.draw.rect(dino_surface, color, (25, 18, 5, 2))
        else:
            # Dibujar dinosaurio normal
            color = BLACK
            # Cuerpo
            pygame.draw.rect(dino_surface, color, (0, 15, 15, 25))
            # Cabeza
            pygame.draw.rect(dino_surface, color, (10, 0, 10, 20))
            # Ojo
            pygame.draw.rect(dino_surface, WHITE, (15, 5, 2, 2))
            # Cola
            pygame.draw.rect(dino_surface, color, (0, 20, 5, 5))

            # Piernas (dependiendo del step)
            if step == 0:  # Muerto
                pygame.draw.rect(dino_surface, color, (2, 38, 5, 2))
                pygame.draw.rect(dino_surface, color, (10, 38, 5, 2))
            elif step == 1:
                pygame.draw.rect(dino_surface, color, (2, 38, 5, 2))
                pygame.draw.rect(dino_surface, color, (10, 38, 5, 2))
            elif step == 2:
                pygame.draw.rect(dino_surface, color, (5, 38, 5, 2))
                pygame.draw.rect(dino_surface, color, (13, 38, 5, 2))

        return dino_surface


    def update(self):
        if self.alive:
            if self.ducking:
                self.duck()
            if not self.ducking:
                if self.jumping:
                    self.jump()
                else:
                    self.run()

            # Actualizar índice de animación
            if self.step_index >= 10:
                self.step_index = 0


    def duck(self):
        self.image = self.ducking_sprites[self.step_index // 5]
        self.rect = self.image.get_rect()
        self.rect.x = 80
        self.rect.y = SCREEN_HEIGHT - 120
        self.step_index += 1


    def run(self):
        self.image = self.running_sprites[self.step_index // 5]
        self.rect = self.image.get_rect()
        self.rect.x = 80
        self.rect.y = SCREEN_HEIGHT - 140
        self.step_index += 1


    def jump(self):
        self.image = self.running_sprites[0]
        if self.jumping:
            self.rect.y -= self.jump_velocity
            self.jump_velocity -= self.gravity

            if self.rect.y >= SCREEN_HEIGHT - 140:
                self.rect.y = SCREEN_HEIGHT - 140
                self.jumping = False
                self.jump_velocity = 0


    def handle_input(self, keys):
        if self.alive:
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.ducking = True
                self.jumping = False
            elif (keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]) and not self.jumping:
                self.jumping = True
                self.ducking = False
                self.jump_velocity = 14
                self.play_jump_sound()
            elif not (keys[pygame.K_DOWN] or keys[pygame.K_s]):
                self.ducking = False


    def play_jump_sound(self):
        # Aquí puedes agregar el sonido de salto
        pass


    def die(self):
        self.alive = False
        self.image = self.dead_img




# Clase para los obstáculos
class Obstacle(pygame.sprite.Sprite):


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


    def update(self, game_speed):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            self.kill()


    @staticmethod
    def create_cactus_surface():
        # Crear cactus pixelart
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


    @staticmethod
    def create_bird_surface(step):
        # Crear pájaro pixelart con alas en diferentes posiciones
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


    def __init__(self, x_pos):
        super().__init__()

        self.image = self.create_ground_surface()
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = SCREEN_HEIGHT - 80


    def create_ground_surface(self):
        # Crear superficie del suelo con pixelart
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


    def update(self, game_speed):
        self.rect.x -= game_speed

        if self.rect.x <= -SCREEN_WIDTH:
            self.kill()




# Clase para la nube
class Cloud(pygame.sprite.Sprite):


    def __init__(self):
        super().__init__()

        self.image = self.create_cloud_surface()
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.rect.y = random.randint(50, 100)


    def create_cloud_surface(self):
        # Crear nube pixelart
        cloud_surface = pygame.Surface((60, 20), pygame.SRCALPHA)
        color = BLACK

        # Forma básica de nube
        pygame.draw.rect(cloud_surface, color, (10, 10, 40, 10))
        pygame.draw.rect(cloud_surface, color, (5, 5, 10, 10))
        pygame.draw.rect(cloud_surface, color, (20, 5, 15, 5))
        pygame.draw.rect(cloud_surface, color, (45, 5, 10, 10))

        return cloud_surface


    def update(self, game_speed):
        self.rect.x -= game_speed // 2

        if self.rect.x < -self.rect.width:
            self.kill()




# Clase principal del juego
class Game:


    def __init__(self):
        self.game_speed = 10
        self.score = 0
        self.high_score = 0
        self.start_time = pygame.time.get_ticks()

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


    def create_ground(self):
        # Crear el suelo para que cubra toda la pantalla
        for i in range(2):
            ground = Ground(SCREEN_WIDTH * i)
            self.ground_group.add(ground)
            self.all_sprites.add(ground)


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


    def create_cloud(self):
        cloud = Cloud()
        self.cloud_group.add(cloud)
        self.all_sprites.add(cloud)


    def update_score(self):
        current_time = pygame.time.get_ticks()
        self.score = int((current_time - self.start_time) / 100)

        if self.score > self.high_score:
            self.high_score = self.score

        # Aumentar la velocidad del juego con el tiempo
        if self.score > 0 and self.score % 100 == 0:
            self.game_speed += 0.5


    def display_score(self):
        # Mostrar puntuación actual
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        SCREEN.blit(score_text, (SCREEN_WIDTH - 150, 10))

        # Mostrar récord
        high_score_text = font.render(f"HI: {self.high_score}", True, BLACK)
        SCREEN.blit(high_score_text, (SCREEN_WIDTH - 150, 40))


    def display_game_over(self):
        game_over_text = font.render("GAME OVER", True, BLACK)
        restart_text = font.render("Press SPACE to restart", True, BLACK)

        SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 20))
        SCREEN.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 20))


    def display_start_screen(self):
        title_text = font.render("Chrome Dino Pixelart", True, BLACK)
        start_text = font.render("Press SPACE to start", True, BLACK)
        instructions_text = font.render("SPACE/UP: Jump, DOWN: Duck", True, BLACK)

        SCREEN.blit(title_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 50))
        SCREEN.blit(start_text, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2))
        SCREEN.blit(instructions_text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 50))


    def check_collision(self):
        # Verificar colisiones con obstáculos
        if pygame.sprite.spritecollide(self.dinosaur, self.obstacle_group, False, pygame.sprite.collide_mask):
            self.dinosaur.die()
            self.game_over = True


    def animate_birds(self):
        # Animar los pájaros
        for obstacle in self.obstacle_group:
            if hasattr(obstacle, 'type') and obstacle.type == "bird" and hasattr(obstacle, 'images'):
                # Cambiar imagen cada cierto tiempo para animar
                if pygame.time.get_ticks() % 200 < 100:
                    obstacle.image = obstacle.images[0]
                else:
                    obstacle.image = obstacle.images[1]


    def reset_game(self):
        # Reiniciar juego
        self.__init__()


    def run(self):
        # Bucle principal del juego
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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