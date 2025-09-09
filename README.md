# Simulación de Semáforos Auto-organizados

Este proyecto es una simulación de un sistema de semáforos inteligentes y auto-organizados, desarrollada en Python utilizando la librería Pygame. El objetivo es modelar un cruce de tráfico donde los semáforos se adaptan dinámicamente al flujo de vehículos, siguiendo un conjunto de reglas predefinidas para optimizar la eficiencia y la seguridad.

---

## Características

* Simulación en tiempo real de una intersección en T.
* Lógica de semáforos adaptativa basada en 6 reglas de auto-organización.
* Generación dinámica de vehículos para un flujo de tráfico realista.
* Interfaz gráfica (GUI) para visualizar el tráfico y el estado de los semáforos.
* Efectos de sonido para los cambios de estado de los semáforos.
* Controles de teclado para forzar y probar escenarios de bloqueo.

---

## Las Reglas del Sistema

La lógica de los semáforos se basa en las siguientes reglas, evaluadas en orden de prioridad:

1.  **Acumulación de Presión:** Si un número de vehículos superior a un umbral espera en una luz roja, se solicita un cambio.
2.  **Tiempo Mínimo en Verde:** Una vez en verde, la luz debe permanecer así por un tiempo mínimo para garantizar el flujo.
3.  **No Interrumpir Pelotón:** Se evita el cambio a rojo si un grupo pequeño de coches está a punto de cruzar la intersección.
4.  **Eficiencia:** Si la vía verde está vacía y hay vehículos esperando en la roja, se solicita un cambio para no desperdiciar tiempo.
5.  **Bloqueo Simple:** Si la vía de salida de una luz verde está bloqueada, el semáforo cambia a rojo para evitar el colapso.
6.  **Bloqueo Total (Emergencia):** Si las salidas de ambas vías están bloqueadas, ambos semáforos se ponen en rojo hasta que una se libere.

---

## Tecnologías Utilizadas

* **Python 3**
* **Pygame** para la interfaz gráfica, el sonido y la gestión de eventos.

---

## 🚀 Instalación y Uso

Sigue estos pasos para ejecutar la simulación en tu máquina local.

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/NicolasGarzon01/semaforoAutoorganizado.git](https://github.com/NicolasGarzon01/semaforoAutoorganizado.git)
    ```

2.  **Navega a la carpeta del proyecto:**
    ```bash
    cd semaforoAutoorganizado
    ```

3.  **Instala las dependencias:**
    Asegúrate de tener Pygame instalado. Si no, ejecuta:
    ```bash
    pip install pygame
    ```

4.  **Ejecuta la simulación:**
    ```bash
    python simulacion_semaforo.py
    ```
> Para los efectos de sonido, asegúrate de tener un archivo `cambio_luz.mp3` en la misma carpeta.

---

## Controles de Prueba

Puedes forzar ciertos escenarios durante la simulación para probar las reglas de bloqueo:

* **Tecla `B`**: Fuerza un bloqueo en la salida de la **Vía Principal**.
* **Tecla `N`**: Fuerza un bloqueo en la salida de la **Vía Secundaria**.
* **Tecla `R`**: **Reinicia** (`Reset`) ambos bloqueos manuales, devolviendo el control a la simulación.

---

## Autores

* **Nicolás Garzón**
* **Juan Felipe Alvarez**
