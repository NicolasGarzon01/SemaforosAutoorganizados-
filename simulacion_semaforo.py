# ===================================================================
# SIMULACIÓN DE SEMÁFOROS AUTO-ORGANIZADOS
# Versión final con interfaz gráfica, sonido, tráfico dinámico y controles de prueba.
# ===================================================================

import time
import random
import pygame

# ===================================================================
# 1. CONFIGURACIÓN INICIAL DE PYGAME
# ===================================================================
pygame.init()
pygame.mixer.init()

try:
    SONIDO_CAMBIO = pygame.mixer.Sound("cambio_luz.mp3")
except pygame.error:
    print("Advertencia: No se encontró 'cambio_luz.mp3'. La simulación se ejecutará sin sonido.")
    class DummySound:
        def play(self): pass
    SONIDO_CAMBIO = DummySound()

# ===================================================================
# 2. CLASE PARA CADA VEHÍCULO 🚗
# ===================================================================
class Vehiculo:
    """Representa un único vehículo en la simulación."""
    def __init__(self, via, carril_y, carril_x):
        self.via = via
        self.velocidad = random.uniform(2.5, 4.0)
        self.color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
        
        if self.via == 'principal':
            self.rect = pygame.Rect(-40, carril_y, 30, 18)
        else:
            self.rect = pygame.Rect(carril_x, 610, 18, 30)

    def mover(self, semaforo_principal, semaforo_secundario):
        """Actualiza la posición del vehículo, deteniéndose si es necesario."""
        if self.via == 'principal':
            if semaforo_principal.estado != 'verde' and 310 < self.rect.centerx < 345:
                return
            self.rect.x += self.velocidad
        else:
            if semaforo_secundario.estado != 'verde' and 355 < self.rect.centery < 390:
                return
            self.rect.y -= self.velocidad

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)

# ===================================================================
# 3. CLASE PARA CADA SEMÁFORO 🚦
# ===================================================================
class Semaforo:
    """Gestiona el estado y el temporizador de un semáforo."""
    def __init__(self, nombre):
        self.nombre = nombre
        self.estado = "rojo"
        self.timer = 0

    def cambiar_a(self, nuevo_estado):
        if self.estado != nuevo_estado:
            self.estado = nuevo_estado
            self.timer = 0
            print(f"🚦 El semáforo {self.nombre} ha cambiado a {self.estado.upper()}")
            SONIDO_CAMBIO.play()

    def actualizar_timer(self, paso):
        self.timer += paso

# ===================================================================
# 4. CLASE PRINCIPAL DE LA SIMULACIÓN (CONTROLADOR)
# ===================================================================
class Simulacion:
    """Orquesta toda la simulación, aplicando la lógica y gestionando la GUI."""
    def __init__(self):
        # Objetos
        self.semaforo_principal = Semaforo("Principal")
        self.semaforo_secundario = Semaforo("Secundario")
        self.vehiculos_principales, self.vehiculos_secundarios = [], []

        # Parámetros de las reglas
        self.U_TIEMPO_MIN_VERDE, self.N_UMBRAL_CONTADOR, self.M_UMBRAL_PELOTON = 10, 15, 2
        
        # Variables de Sensores
        self.vehiculos_d_principal, self.vehiculos_r_principal, self.bloqueo_e_principal = 0, 0, False
        self.vehiculos_d_secundario, self.vehiculos_r_secundario, self.bloqueo_e_secundario = 0, 0, False
        self.contador_presion_rojo = 0

        # Zonas de Detección
        self.ZONA_D_PRINCIPAL = pygame.Rect(0, 260, 310, 80)
        self.ZONA_R_PRINCIPAL = pygame.Rect(310, 260, 35, 80)
        self.ZONA_E_PRINCIPAL = pygame.Rect(450, 260, 50, 80)
        self.ZONA_D_SECUNDARIA = pygame.Rect(360, 390, 80, 210)
        self.ZONA_R_SECUNDARIA = pygame.Rect(360, 350, 80, 40)
        self.ZONA_E_SECUNDARIA = pygame.Rect(360, 200, 80, 50)
        
        # Configuración de Pygame
        self.ancho, self.alto = 800, 600
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Simulación de Tráfico Auto-organizado")
        self.reloj = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        
        # Colores
        self.COLOR_FONDO, self.COLOR_CALLE = (20, 20, 20), (100, 100, 100)
        self.COLOR_VERDE_ON, self.COLOR_AMARILLO_ON, self.COLOR_ROJO_ON = (0, 255, 0), (255, 255, 0), (255, 0, 0)
        self.COLOR_LUZ_OFF = (40, 40, 40)

    def _generar_vehiculos(self):
        if random.random() < 0.05: self.vehiculos_principales.append(Vehiculo('principal', random.choice([265, 295]), 0))
        if random.random() < 0.03: self.vehiculos_secundarios.append(Vehiculo('secundaria', 0, random.choice([365, 395])))

    def _actualizar_sensores_reales(self):
        # Reiniciar contadores antes de recalcular
        self.vehiculos_d_principal, self.vehiculos_r_principal = 0, 0
        self.vehiculos_d_secundario, self.vehiculos_r_secundario = 0, 0
        
        # Solo reinicia los bloqueos si no están siendo forzados manualmente
        if not pygame.key.get_pressed()[pygame.K_b]: self.bloqueo_e_principal = False
        if not pygame.key.get_pressed()[pygame.K_n]: self.bloqueo_e_secundario = False

        for v in self.vehiculos_principales:
            if self.ZONA_D_PRINCIPAL.colliderect(v.rect): self.vehiculos_d_principal += 1
            if self.ZONA_R_PRINCIPAL.colliderect(v.rect): self.vehiculos_r_principal += 1
            if self.ZONA_E_PRINCIPAL.colliderect(v.rect) and v.velocidad < 1: self.bloqueo_e_principal = True
        
        for v in self.vehiculos_secundarios:
            if self.ZONA_D_SECUNDARIA.colliderect(v.rect): self.vehiculos_d_secundario += 1
            if self.ZONA_R_SECUNDARIA.colliderect(v.rect): self.vehiculos_r_secundario += 1
            if self.ZONA_E_SECUNDARIA.colliderect(v.rect) and v.velocidad < 1: self.bloqueo_e_secundario = True

    def _imprimir_estado_consola(self):
        print("-" * 50)
        print(f"ESTADO: Principal: {self.semaforo_principal.estado.upper()} ({self.semaforo_principal.timer}s) | "
              f"Secundario: {self.semaforo_secundario.estado.upper()} ({self.semaforo_secundario.timer}s)")
        print(f"SENSORES Vía Principal: [d]={self.vehiculos_d_principal}, [r]={self.vehiculos_r_principal}, [e bloqueado?]={self.bloqueo_e_principal}")
        print(f"SENSORES Vía Secundaria: [d]={self.vehiculos_d_secundario}, [r]={self.vehiculos_r_secundario}, [e bloqueado?]={self.bloqueo_e_secundario}")
        print(f"Contador de Presión (Regla 1): {self.contador_presion_rojo}")

    def _dibujar_escena(self):
        self.pantalla.fill(self.COLOR_FONDO)
        pygame.draw.rect(self.pantalla, self.COLOR_CALLE, (0, 250, 800, 100))
        pygame.draw.rect(self.pantalla, self.COLOR_CALLE, (350, 0, 100, 600))
        
        for v in self.vehiculos_principales: v.dibujar(self.pantalla)
        for v in self.vehiculos_secundarios: v.dibujar(self.pantalla)
        
        sp_r, sp_a, sp_v = (self.COLOR_ROJO_ON if self.semaforo_principal.estado == 'rojo' else self.COLOR_LUZ_OFF), (self.COLOR_AMARILLO_ON if self.semaforo_principal.estado == 'amarillo' else self.COLOR_LUZ_OFF), (self.COLOR_VERDE_ON if self.semaforo_principal.estado == 'verde' else self.COLOR_LUZ_OFF)
        ss_r, ss_a, ss_v = (self.COLOR_ROJO_ON if self.semaforo_secundario.estado == 'rojo' else self.COLOR_LUZ_OFF), (self.COLOR_AMARILLO_ON if self.semaforo_secundario.estado == 'amarillo' else self.COLOR_LUZ_OFF), (self.COLOR_VERDE_ON if self.semaforo_secundario.estado == 'verde' else self.COLOR_LUZ_OFF)
        pygame.draw.rect(self.pantalla, (50, 50, 50), (310, 160, 30, 90)); pygame.draw.rect(self.pantalla, (50, 50, 50), (460, 350, 30, 90))
        pygame.draw.circle(self.pantalla, sp_r, (325, 175), 12); pygame.draw.circle(self.pantalla, sp_a, (325, 205), 12); pygame.draw.circle(self.pantalla, sp_v, (325, 235), 12)
        pygame.draw.circle(self.pantalla, ss_r, (475, 365), 12); pygame.draw.circle(self.pantalla, ss_a, (475, 395), 12); pygame.draw.circle(self.pantalla, ss_v, (475, 425), 12)
        
        texto_estado = self.font.render(f'Principal: {self.semaforo_principal.estado.upper()} ({self.semaforo_principal.timer}s) | Secundario: {self.semaforo_secundario.estado.upper()} ({self.semaforo_secundario.timer}s)', True, (255,255,255))
        self.pantalla.blit(texto_estado, (10, 10))
        pygame.display.flip()
        
    def _aplicar_logica(self):
        """El 'cerebro' de la simulación donde se aplican las 6 reglas."""
        s_verde, s_rojo = (self.semaforo_principal, self.semaforo_secundario) if self.semaforo_principal.estado in ["verde", "amarillo"] else (self.semaforo_secundario, self.semaforo_principal)

        if s_verde.estado == "amarillo":
            if s_verde.timer >= 3:
                s_verde.cambiar_a("rojo"); pygame.time.wait(1000)
                s_rojo.cambiar_a("verde"); self.contador_presion_rojo = 0
            return
        
        if s_verde.estado == "rojo" and s_rojo.estado == "rojo":
            if not self.bloqueo_e_principal and self.vehiculos_d_principal > 0: self.semaforo_principal.cambiar_a("verde")
            elif not self.bloqueo_e_secundario and self.vehiculos_d_secundario > 0: self.semaforo_secundario.cambiar_a("verde")
            return

        (vehiculos_d_verde, vehiculos_r_verde, bloqueo_e_verde) = (self.vehiculos_d_principal, self.vehiculos_r_principal, self.bloqueo_e_principal) if s_verde.nombre == "Principal" else (self.vehiculos_d_secundario, self.vehiculos_r_secundario, self.bloqueo_e_secundario)
        (vehiculos_d_rojo, _, bloqueo_e_rojo) = (self.vehiculos_d_secundario, self.vehiculos_r_secundario, self.bloqueo_e_secundario) if s_rojo.nombre == "Principal" else (self.vehiculos_d_principal, self.vehiculos_r_principal, self.bloqueo_e_principal)
        
        if bloqueo_e_verde and bloqueo_e_rojo: s_verde.cambiar_a("rojo"); s_rojo.cambiar_a("rojo"); return
        
        self.contador_presion_rojo += vehiculos_d_rojo
        solicitar_cambio = False
        if bloqueo_e_verde: solicitar_cambio = True
        if s_verde.timer < self.U_TIEMPO_MIN_VERDE: return
        if vehiculos_d_verde == 0 and vehiculos_d_rojo > 0: solicitar_cambio = True
        if self.contador_presion_rojo > self.N_UMBRAL_CONTADOR: solicitar_cambio = True
        if solicitar_cambio:
            if 0 < vehiculos_r_verde <= self.M_UMBRAL_PELOTON: return
            s_verde.cambiar_a("amarillo")

    def iniciar(self):
        """Contiene el bucle principal de Pygame que corre la simulación."""
        self.semaforo_principal.cambiar_a("verde")
        running = True
        tiempo_logica = 0
        
        while running:
            # --- GESTIÓN DE EVENTOS (INCLUYE CONTROLES DE PRUEBA) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b: # Tecla 'B' para bloquear vía Principal
                        self.bloqueo_e_principal = True
                        print("!! BLOQUEO FORZADO EN VÍA PRINCIPAL !!")
                    if event.key == pygame.K_n: # Tecla 'N' para bloquear vía Secundaria
                        self.bloqueo_e_secundario = True
                        print("!! BLOQUEO FORZADO EN VÍA SECUNDARIA !!")
                    if event.key == pygame.K_r: # Tecla 'R' para reiniciar bloqueos
                        self.bloqueo_e_principal = False
                        self.bloqueo_e_secundario = False
                        print("!! BLOQUEOS REINICIADOS !!")
            
            # La lógica de decisión se ejecuta una vez por segundo
            tiempo_logica += self.reloj.get_time()
            if tiempo_logica > 1000:
                tiempo_logica = 0
                self._actualizar_sensores_reales()
                self._aplicar_logica()
                self.semaforo_principal.actualizar_timer(1)
                self.semaforo_secundario.actualizar_timer(1)
                self._imprimir_estado_consola()

            # Las animaciones y generación de vehículos se ejecutan en cada frame
            self._generar_vehiculos()
            for v in self.vehiculos_principales: v.mover(self.semaforo_principal, self.semaforo_secundario)
            for v in self.vehiculos_secundarios: v.mover(self.semaforo_principal, self.semaforo_secundario)
            
            self.vehiculos_principales = [v for v in self.vehiculos_principales if v.rect.x < self.ancho + 40]
            self.vehiculos_secundarios = [v for v in self.vehiculos_secundarios if v.rect.y > -40]
            
            self._dibujar_escena()
            self.reloj.tick(60) # Limita la simulación a 60 FPS
        
        pygame.quit()
        print("\nSimulación terminada.")

# ===================================================================
# 5. PUNTO DE ENTRADA PARA EJECUTAR LA SIMULACIÓN
# ===================================================================
if __name__ == "__main__":
    sim = Simulacion()
    sim.iniciar()