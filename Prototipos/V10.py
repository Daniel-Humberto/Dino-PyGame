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
ANCHO_PANTALLA = 750
ALTO_PANTALLA = 250
PANTALLA = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Juego del Dinosaurio")


# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS_CLARO = (200, 200, 200)  # Gris claro para nubes en modo día
GRIS_OSCURO = (100, 100, 100)   # Gris oscuro para nubes en modo noche


# Variables para control de día/noche
es_noche = False
colores_actuales = {
    'fondo': BLANCO,
    'primer_plano': NEGRO,
    'nube': GRIS_CLARO
}


# Reloj para controlar FPS
reloj = pygame.time.Clock()
FPS = 60


# Cargar fuente
fuente = pygame.font.Font(None, 30)


# Archivo para guardar la puntuación más alta
ARCHIVO_RECORD = "Record.json"


# Función para actualizar colores según el estado día/noche
def actualizar_colores(puntuacion):
    global es_noche, colores_actuales
    # Cambiar cada 100 puntos
    es_noche = (puntuacion // 100) % 2 == 1
    if es_noche:
        colores_actuales['fondo'] = NEGRO
        colores_actuales['primer_plano'] = BLANCO
        colores_actuales['nube'] = GRIS_OSCURO
    else:
        colores_actuales['fondo'] = BLANCO
        colores_actuales['primer_plano'] = NEGRO
        colores_actuales['nube'] = GRIS_CLARO


# Función para generar sonidos procedurales
def generar_sonidos():
    sonidos = {}

    # Sonido de salto (tono ascendente)
    sonido_salto = generar_tono(frecuencia=440, duracion=0.1, volumen=0.3, desvanecimiento=True)
    sonidos["salto"] = sonido_salto

    # Sonido de colisión (ruido blanco)
    sonido_colision = generar_ruido(duracion=0.3, volumen=0.4)
    sonidos["colision"] = sonido_colision

    # Sonido de punto (ping corto)
    sonido_punto = generar_tono(frecuencia=880, duracion=0.05, volumen=0.2)
    sonidos["punto"] = sonido_punto

    return sonidos


# Genera un tono simple usando numpy y lo convierte en un objeto Sound de Pygame
def generar_tono(frecuencia=440, duracion=0.1, volumen=0.5, desvanecimiento=False):
    tasa_muestreo = 44100
    t = np.linspace(0, duracion, int(tasa_muestreo * duracion), False)
    tono = np.sin(frecuencia * 2 * np.pi * t) * volumen

    if desvanecimiento:
        # Aplicar un fade-out al sonido
        muestras_desvanecimiento = int(tasa_muestreo * duracion * 0.5)
        desvanecimiento_salida = np.linspace(1.0, 0.0, muestras_desvanecimiento)
        tono[-muestras_desvanecimiento:] *= desvanecimiento_salida

    # Asegurarse de que los valores estén entre -1 y 1
    tono = np.clip(tono, -1, 1)

    # Convertir a formato de audio de pygame
    tono = (tono * 32767).astype(np.int16)

    # Crear objeto Sound de pygame
    objeto_sonido = pygame.mixer.Sound(tono)

    return objeto_sonido


# Genera ruido blanco usando numpy y lo convierte en un objeto Sound de Pygame
def generar_ruido(duracion=0.2, volumen=0.5):
    tasa_muestreo = 44100
    muestras = int(tasa_muestreo * duracion)

    # Generar ruido blanco
    ruido = np.random.uniform(-1, 1, muestras) * volumen

    # Aplicar un fade-out al ruido
    muestras_desvanecimiento = int(tasa_muestreo * duracion * 0.5)
    desvanecimiento_salida = np.linspace(1.0, 0.0, muestras_desvanecimiento)
    ruido[-muestras_desvanecimiento:] *= desvanecimiento_salida

    # Convertir a formato de audio de pygame
    ruido = (ruido * 32767).astype(np.int16)

    # Crear objeto Sound de pygame
    objeto_sonido = pygame.mixer.Sound(ruido)

    return objeto_sonido


# Cargar o crear el archivo de puntuación más alta
def cargar_record():
    try:
        with open(ARCHIVO_RECORD, 'r') as archivo:
            datos = json.load(archivo)
            return datos.get('record', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si el archivo no existe o está corrupto, devolver 0
        return 0


# Guardar la puntuación más alta
def guardar_record(puntuacion):
    datos = {'record': puntuacion}
    with open(ARCHIVO_RECORD, 'w') as archivo:
        json.dump(datos, archivo)


# Generar sonidos
sonidos_juego = generar_sonidos()


# Clase para el Dinosaurio
class Dinosaurio(pygame.sprite.Sprite):


    # Inicialización
    def __init__(self):
        super().__init__()

        # Inicializar variables de estado
        self.velocidad_salto = 0
        self.agachado = False
        self.indice_paso = 0
        self.gravedad = 1
        self.saltando = False
        self.vivo = True
        self.tamaño_pixel_render = 3

        # Datos de los sprites
        self.datos_perro_corriendo_1 = [
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

        self.datos_perro_corriendo_2 = [
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

        self.datos_perro_agachado_1 = [
            "     XXXXX    ",
            "   XX     X   ",
            "  XX       X  ",
            "XXX      XXX  ",
            "XXX         X ",
            "  X    XX    X ",
            "  XX  X  X   X ",
            "   XXXX   XXX "
        ]

        self.datos_perro_agachado_2 = [
            "     XXXXX    ",
            "   XX     X   ",
            "  XX       X  ",
            "XXX      XXX  ",
            "XXX         X ",
            "  X    XX    X ",
            "  XX  X  X   X ",
            "   XXXX   XXX "
        ]

        self.datos_perro_muerto = [
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
        self.regenerar_sprites()

        # Configurar posición inicial
        self.rect = self.image.get_rect()
        self.rect.x = 80
        self.y_base_corriendo = ALTO_PANTALLA - 80 - self.rect.height
        self.y_base_agachado = ALTO_PANTALLA - 80 - self.sprites_agachado[0].get_rect().height + 5
        self.rect.y = self.y_base_corriendo


    # Actualizar
    def actualizar(self):
        if self.vivo:
            if self.agachado:
                self.agacharse()
            elif self.saltando:
                self.saltar()
            else:
                self.correr()

            if self.indice_paso >= 20:
                self.indice_paso = 0


    # Agacharse
    def agacharse(self):
        self.image = self.sprites_agachado[self.indice_paso // 10]
        x_actual = self.rect.x
        inferior_actual = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = x_actual
        self.rect.bottom = inferior_actual
        self.indice_paso += 1


    # Correr
    def correr(self):
        self.image = self.sprites_corriendo[self.indice_paso // 10]
        x_actual = self.rect.x
        inferior_actual = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = x_actual
        self.rect.bottom = inferior_actual
        self.indice_paso += 1


    # Saltar
    def saltar(self):
        self.image = self.sprites_corriendo[0]

        if self.saltando:
            self.rect.y -= self.velocidad_salto
            self.velocidad_salto -= self.gravedad
            if self.rect.y >= self.y_base_corriendo:
                self.rect.y = self.y_base_corriendo
                self.saltando = False
                self.velocidad_salto = 0


    # Manejar entrada
    def manejar_entrada(self, teclas):
        if self.vivo:
            if (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and not self.saltando:
                self.agachado = True
                self.reproducir_sonido_salto()
            elif (teclas[pygame.K_UP] or teclas[pygame.K_SPACE] or teclas[pygame.K_w]) and not self.saltando and not self.agachado:
                self.saltando = True
                self.velocidad_salto = 20
                self.agachado = False
                self.reproducir_sonido_salto()
            elif not (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and not self.saltando:
                self.agachado = False


    # Reproducir sonido de salto
    def reproducir_sonido_salto(self):
        sonidos_juego["salto"].play()


    # Morir
    def morir(self):
        self.vivo = False
        self.image = self.imagen_muerto
        sonidos_juego["colision"].play()


    def regenerar_sprites(self):
        # Regenerar todos los sprites con los colores actuales
        self.sprites_corriendo = []
        self.sprites_agachado = []

        self.imagen_corriendo1 = self.crear_superficie_desde_pixel_art(self.datos_perro_corriendo_1, self.tamaño_pixel_render)
        self.dibujar_ojo(self.imagen_corriendo1, self.datos_perro_corriendo_1)
        self.sprites_corriendo.append(self.imagen_corriendo1)

        self.imagen_corriendo2 = self.crear_superficie_desde_pixel_art(self.datos_perro_corriendo_2, self.tamaño_pixel_render)
        self.dibujar_ojo(self.imagen_corriendo2, self.datos_perro_corriendo_2)
        self.sprites_corriendo.append(self.imagen_corriendo2)

        self.imagen_agachado1 = self.crear_superficie_desde_pixel_art(self.datos_perro_agachado_1, self.tamaño_pixel_render)
        self.dibujar_ojo(self.imagen_agachado1, self.datos_perro_agachado_1)
        self.sprites_agachado.append(self.imagen_agachado1)

        self.imagen_agachado2 = self.crear_superficie_desde_pixel_art(self.datos_perro_agachado_2, self.tamaño_pixel_render)
        self.dibujar_ojo(self.imagen_agachado2, self.datos_perro_agachado_2)
        self.sprites_agachado.append(self.imagen_agachado2)

        self.imagen_muerto = self.crear_superficie_desde_pixel_art(self.datos_perro_muerto, self.tamaño_pixel_render)
        self.dibujar_ojos_muerto(self.imagen_muerto, self.datos_perro_muerto)

        # Actualizar la imagen actual
        if self.vivo:
            if self.agachado:
                self.image = self.sprites_agachado[self.indice_paso // 10]
            else:
                self.image = self.sprites_corriendo[self.indice_paso // 10]
        else:
            self.image = self.imagen_muerto


    def crear_superficie_desde_pixel_art(self, datos_pixel, tamaño_pixel=2):
        altura = len(datos_pixel) * tamaño_pixel
        ancho = len(datos_pixel[0]) * tamaño_pixel if altura > 0 else 0

        superficie = pygame.Surface((ancho, altura), pygame.SRCALPHA)
        superficie.fill((0, 0, 0, 0))

        for r, cadena_fila in enumerate(datos_pixel):
            for c, pixel_caracter in enumerate(cadena_fila):
                if pixel_caracter == 'X':
                    pygame.draw.rect(superficie, colores_actuales['primer_plano'], (c * tamaño_pixel, r * tamaño_pixel, tamaño_pixel, tamaño_pixel))
        return superficie


    def dibujar_ojo(self, superficie, datos, caracter_ojo='.', tamaño_pixel_s=None):
        if tamaño_pixel_s is None:
            tamaño_pixel_s = self.tamaño_pixel_render
        for r, cadena_fila in enumerate(datos):
            for c, pixel_caracter in enumerate(cadena_fila):
                if pixel_caracter == caracter_ojo:
                    pygame.draw.rect(superficie, colores_actuales['primer_plano'], (c * tamaño_pixel_s, r * tamaño_pixel_s, tamaño_pixel_s, tamaño_pixel_s))


    def dibujar_ojos_muerto(self, superficie, datos, caracter_ojo='o', tamaño_pixel_s=None):
        if tamaño_pixel_s is None:
            tamaño_pixel_s = self.tamaño_pixel_render
        for r, cadena_fila in enumerate(datos):
            for c, pixel_caracter in enumerate(cadena_fila):
                if pixel_caracter == caracter_ojo:
                    pygame.draw.line(superficie, colores_actuales['primer_plano'], (c * tamaño_pixel_s, r * tamaño_pixel_s),
                                     ((c + 1) * tamaño_pixel_s - 1, (r + 1) * tamaño_pixel_s - 1), 1)
                    pygame.draw.line(superficie, colores_actuales['primer_plano'], ((c + 1) * tamaño_pixel_s - 1, r * tamaño_pixel_s),
                                     (c * tamaño_pixel_s, (r + 1) * tamaño_pixel_s - 1), 1)


# Clase para los obstáculos
class Obstaculo(pygame.sprite.Sprite):


    # Inicialización
    def __init__(self, imagen, tipo_obstaculo):
        super().__init__()

        self.image = imagen
        self.rect = self.image.get_rect()
        self.tipo = tipo_obstaculo

        if self.tipo == "cactus":
            self.rect.y = ALTO_PANTALLA - 120
        else:  # Es un pájaro
            self.rect.y = ALTO_PANTALLA - 180 if random.randint(0, 1) == 0 else ALTO_PANTALLA - 140
        self.rect.x = ANCHO_PANTALLA


    # Actualización
    def actualizar(self, velocidad_juego):
        self.rect.x -= velocidad_juego
        if self.rect.x < -self.rect.width:
            self.kill()


    # Crear cactus
    @staticmethod
    def crear_superficie_cactus():
        altura = random.randint(40, 60)
        ancho = 20
        superficie_cactus = pygame.Surface((ancho, altura), pygame.SRCALPHA)
        color = colores_actuales['primer_plano']

        # Tronco principal
        pygame.draw.rect(superficie_cactus, color, (8, 0, 4, altura))

        # Brazos
        altura_brazo = random.randint(15, 25)
        pygame.draw.rect(superficie_cactus, color, (0, altura // 3, 8, 4))  # Brazo izquierdo
        pygame.draw.rect(superficie_cactus, color, (0, altura // 3, 4, altura_brazo))

        pygame.draw.rect(superficie_cactus, color, (12, altura // 2, 8, 4))  # Brazo derecho
        pygame.draw.rect(superficie_cactus, color, (16, altura // 2, 4, altura_brazo))

        return superficie_cactus


    # Crear pájaro con alas en diferentes posiciones
    @staticmethod
    def crear_superficie_pajaro(paso):
        superficie_pajaro = pygame.Surface((40, 20), pygame.SRCALPHA)
        color = colores_actuales['primer_plano']

        # Cuerpo
        pygame.draw.rect(superficie_pajaro, color, (15, 10, 10, 10))

        # Cabeza
        pygame.draw.rect(superficie_pajaro, color, (30, 5, 10, 10))

        # Pico
        pygame.draw.rect(superficie_pajaro, color, (40, 8, 3, 4))

        # Alas (diferentes según el paso de animación)
        if paso == 1:
            pygame.draw.rect(superficie_pajaro, color, (15, 5, 15, 3))  # Alas arriba
        else:
            pygame.draw.rect(superficie_pajaro, color, (15, 15, 15, 3))  # Alas abajo

        return superficie_pajaro


# Clase para el suelo
class Suelo(pygame.sprite.Sprite):


    # Inicialización
    def __init__(self, posicion_x):
        super().__init__()

        self.image = self.crear_superficie_suelo()
        self.rect = self.image.get_rect()
        self.rect.x = posicion_x
        self.rect.y = ALTO_PANTALLA - 80


    # Crear superficie del suelo
    def crear_superficie_suelo(self):
        superficie_suelo = pygame.Surface((ANCHO_PANTALLA, 80))
        superficie_suelo.fill(colores_actuales['fondo'])

        # Línea superior
        pygame.draw.line(superficie_suelo, colores_actuales['primer_plano'], (0, 0), (ANCHO_PANTALLA, 0), 2)

        # Dibujar algunas piedras pequeñas aleatorias
        for _ in range(20):
            x = random.randint(0, ANCHO_PANTALLA)
            y = random.randint(10, 70)
            tamaño = random.randint(1, 3)
            pygame.draw.rect(superficie_suelo, colores_actuales['primer_plano'], (x, y, tamaño, tamaño))

        return superficie_suelo


    # Actualizar
    def actualizar(self, velocidad_juego):
        self.rect.x -= velocidad_juego

        if self.rect.x <= -ANCHO_PANTALLA:
            self.kill()


# Clase para la nube
class Nube(pygame.sprite.Sprite):


    # Inicialización
    def __init__(self):
        super().__init__()

        self.image = self.crear_superficie_nube()
        self.rect = self.image.get_rect()
        self.rect.x = ANCHO_PANTALLA + random.randint(800, 1000)
        self.rect.y = random.randint(50, 100)


    # Crear nube
    def crear_superficie_nube(self):
        superficie_nube = pygame.Surface((60, 20), pygame.SRCALPHA)
        color = colores_actuales['nube']

        # Forma básica de nube
        pygame.draw.rect(superficie_nube, color, (10, 10, 40, 10))
        pygame.draw.rect(superficie_nube, color, (5, 5, 10, 10))
        pygame.draw.rect(superficie_nube, color, (20, 5, 15, 5))
        pygame.draw.rect(superficie_nube, color, (45, 5, 10, 10))

        return superficie_nube


    # Actualizar
    def actualizar(self, velocidad_juego):
        self.rect.x -= velocidad_juego // 2

        if self.rect.x < -self.rect.width:
            self.kill()


# Clase principal del juego
class Juego:


    # Inicialización
    def __init__(self):
        self.velocidad_juego = 10
        self.puntuacion = 0
        self.record = cargar_record()  # Cargar puntuación más alta
        self.tiempo_inicio = pygame.time.get_ticks()
        self.ultimo_hito = 0  # Para rastrear cuando reproducir el sonido de punto

        # Crear grupos de sprites
        self.todos_sprites = pygame.sprite.Group()
        self.grupo_obstaculos = pygame.sprite.Group()
        self.grupo_suelo = pygame.sprite.Group()
        self.grupo_nubes = pygame.sprite.Group()

        # Crear el dinosaurio
        self.dinosaurio = Dinosaurio()
        self.todos_sprites.add(self.dinosaurio)

        # Crear el suelo inicial
        self.crear_suelo()

        # Control de tiempo para la generación de obstáculos
        self.temporizador_obstaculos = 0
        self.temporizador_nubes = 0

        # Estado del juego
        self.juego_terminado = False
        self.juego_iniciado = False


    # Crear el suelo para que cubra toda la pantalla
    def crear_suelo(self):
        for i in range(2):
            suelo = Suelo(ANCHO_PANTALLA * i)
            self.grupo_suelo.add(suelo)
            self.todos_sprites.add(suelo)


    # Crear Obstáculo
    def crear_obstaculo(self):
        # Probabilidad de crear un cactus o un pájaro
        if random.randint(0, 4) == 0 and self.puntuacion > 100:  # Pájaros solo después de cierta puntuación
            imagen_pajaro1 = Obstaculo.crear_superficie_pajaro(1)
            imagen_pajaro2 = Obstaculo.crear_superficie_pajaro(2)
            pajaro = Obstaculo(imagen_pajaro1, "pajaro")
            pajaro.imagenes = [imagen_pajaro1, imagen_pajaro2]
            pajaro.imagen_actual = 0
        else:
            imagen_cactus = Obstaculo.crear_superficie_cactus()
            pajaro = Obstaculo(imagen_cactus, "cactus")

        self.grupo_obstaculos.add(pajaro)
        self.todos_sprites.add(pajaro)


    # Crear Nube
    def crear_nube(self):
        nube = Nube()
        self.grupo_nubes.add(nube)
        self.todos_sprites.add(nube)


    # Actualizar Puntuación
    def actualizar_puntuacion(self):
        tiempo_actual = pygame.time.get_ticks()
        self.puntuacion = int((tiempo_actual - self.tiempo_inicio) / 100)

        # Verificar si se ha alcanzado un nuevo hito de puntuación (cada 100 puntos)
        hito_actual = self.puntuacion // 100

        if hito_actual > self.ultimo_hito:
            # Reproducir sonido de punto
            sonidos_juego["punto"].play()
            self.ultimo_hito = hito_actual

        # Actualizar la puntuación más alta si es necesario
        if self.puntuacion > self.record:
            self.record = self.puntuacion
            guardar_record(self.record)  # Guardar la nueva puntuación más alta

        # Aumentar la velocidad del juego con el tiempo
        if self.puntuacion > 0 and self.puntuacion % 100 == 0:
            self.velocidad_juego += 0.5


    # Mostrar Puntuación
    def mostrar_puntuacion(self):
        # Mostrar puntuación actual
        texto_puntuacion = fuente.render(f"Puntos: {self.puntuacion}", True, colores_actuales['primer_plano'])
        PANTALLA.blit(texto_puntuacion, (ANCHO_PANTALLA - 150, 10))

        # Mostrar récord
        texto_record = fuente.render(f"RECORD: {self.record}", True, colores_actuales['primer_plano'])
        PANTALLA.blit(texto_record, (ANCHO_PANTALLA - 150, 40))


    # Mostrar Game Over
    def mostrar_juego_terminado(self):
        texto_juego_terminado = fuente.render("JUEGO TERMINADO", True, colores_actuales['primer_plano'])
        texto_reiniciar = fuente.render("Presiona ESPACIO para reiniciar", True, colores_actuales['primer_plano'])

        PANTALLA.blit(texto_juego_terminado, (ANCHO_PANTALLA // 2 - 100, ALTO_PANTALLA // 2 - 20))
        PANTALLA.blit(texto_reiniciar, (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 + 20))


    # Mostrar Pantalla de Inicio
    def mostrar_pantalla_inicio(self):
        texto_titulo = fuente.render("Juego del Dinosaurio", True, colores_actuales['primer_plano'])
        texto_inicio = fuente.render("Presiona ESPACIO para iniciar", True, colores_actuales['primer_plano'])
        texto_instrucciones = fuente.render("ESPACIO/ARRIBA: Saltar, ABAJO: Agacharse", True, colores_actuales['primer_plano'])

        PANTALLA.blit(texto_titulo, (ANCHO_PANTALLA // 2 - 80, ALTO_PANTALLA // 2 - 50))
        PANTALLA.blit(texto_inicio, (ANCHO_PANTALLA // 2 - 130, ALTO_PANTALLA // 2))
        PANTALLA.blit(texto_instrucciones, (ANCHO_PANTALLA // 2 - 170, ALTO_PANTALLA // 2 + 50))

        # Mostrar récord actual en la pantalla de inicio
        if self.record > 0:
            texto_record = fuente.render(f"Récord: {self.record}", True, colores_actuales['primer_plano'])
            PANTALLA.blit(texto_record, (ANCHO_PANTALLA // 2 - 60, ALTO_PANTALLA // 2 + 80))


    # Verificar Colisiones con Obstáculos
    def verificar_colision(self):
        # Verificar colisiones con obstáculos
        if pygame.sprite.spritecollide(self.dinosaurio, self.grupo_obstaculos, False, pygame.sprite.collide_mask):
            self.dinosaurio.morir()
            self.juego_terminado = True


    # Animación pájaros
    def animar_pajaros(self):
        # Animar los pájaros
        for obstaculo in self.grupo_obstaculos:
            if hasattr(obstaculo, 'tipo') and obstaculo.tipo == "pajaro" and hasattr(obstaculo, 'imagenes'):
                # Cambiar imagen cada cierto tiempo para animar
                if pygame.time.get_ticks() % 200 < 100:
                    obstaculo.image = obstaculo.imagenes[0]
                else:
                    obstaculo.image = obstaculo.imagenes[1]


    # Reiniciar Juego
    def reiniciar_juego(self):
        # Guardar puntuación máxima antes de reiniciar
        if self.puntuacion > self.record:
            self.record = self.puntuacion
            guardar_record(self.record)

        # Reiniciar juego manteniendo la puntuación más alta
        record_anterior = self.record
        self.__init__()
        self.record = record_anterior


# Ejecutar
    def ejecutar(self):
        # Bucle principal del juego
        ejecutando = True
        ultima_puntuacion = -1  # Para detectar cambios en la puntuación
        
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    # Guardar puntuación antes de salir
                    if self.puntuacion > self.record:
                        guardar_record(self.puntuacion)
                    ejecutando = False
                    pygame.quit()
                    sys.exit()
                
                # Iniciar o reiniciar el juego con la barra espaciadora
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_UP:
                        if not self.juego_iniciado:
                            self.juego_iniciado = True
                            self.tiempo_inicio = pygame.time.get_ticks()
                        elif self.juego_terminado:
                            self.reiniciar_juego()
            
            # Obtener teclas presionadas
            teclas = pygame.key.get_pressed()
            
            # Pantalla de inicio
            if not self.juego_iniciado:
                PANTALLA.fill(colores_actuales['fondo'])
                self.mostrar_pantalla_inicio()
                pygame.display.update()
                reloj.tick(FPS)
                continue
            
            # Fondo según el estado día/noche
            PANTALLA.fill(colores_actuales['fondo'])
            
            # Actualizar colores según la puntuación
            actualizar_colores(self.puntuacion)
            
            # Regenerar sprites del dinosaurio si cambió el modo día/noche
            if self.puntuacion // 100 != ultima_puntuacion // 100:
                self.dinosaurio.regenerar_sprites()
                ultima_puntuacion = self.puntuacion
            
            # Manejar entrada del dinosaurio
            self.dinosaurio.manejar_entrada(teclas)
            
            # Actualizar sprites solo si el juego no ha terminado
            if not self.juego_terminado:
                # Generar nubes
                self.temporizador_nubes += 1
                if self.temporizador_nubes >= 100:
                    self.crear_nube()
                    self.temporizador_nubes = 0
                
                # Generar obstáculos
                self.temporizador_obstaculos += 1
                if self.temporizador_obstaculos >= 50 + random.randint(0, 50):
                    self.crear_obstaculo()
                    self.temporizador_obstaculos = 0
                
                # Verificar si se necesita crear más suelo
                if len(self.grupo_suelo) < 2:
                    suelo = Suelo(ANCHO_PANTALLA - 5)
                    self.grupo_suelo.add(suelo)
                    self.todos_sprites.add(suelo)
                
                # Actualizar puntuación
                self.actualizar_puntuacion()
                
                # Animar pájaros
                self.animar_pajaros()
                
                # Actualizar todos los sprites
                for sprite in self.todos_sprites:
                    if isinstance(sprite, (Suelo, Obstaculo, Nube)):
                        sprite.actualizar(self.velocidad_juego)
                    else:
                        sprite.actualizar()
                
                # Comprobar colisiones
                self.verificar_colision()
            
            # Dibujar todos los sprites
            self.todos_sprites.draw(PANTALLA)
            
            # Mostrar puntuación
            self.mostrar_puntuacion()
            
            # Mostrar pantalla de game over si es necesario
            if self.juego_terminado:
                self.mostrar_juego_terminado()
            
            # Actualizar pantalla
            pygame.display.update()
            
            # Controlar FPS
            reloj.tick(FPS)


# Iniciar el juego
if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
