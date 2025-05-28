import random
import time
from enum import Enum
from colorama import init, Fore, Back, Style

# Inicializar colorama
init(autoreset=True)

class Dificultad(Enum):
    FACIL = 2
    MEDIO = 3
    DIFICIL = 4

class Personaje(Enum):
    GATO = 1
    RATON = 2

# Símbolos del juego con colores mejorados
SUELO = '🟪'
PARED = '🧱'
QUESO = '🧀'
META = '🏁'
GATO = '🐱'
RATON = '🐭'
TRAMPA = '🕳️'     # Restringe movimientos
TELEPORT = '🌀'  # Teletransporta a posición aleatoria
VELOCIDAD = '⚡'   # Da movimientos extra
ESCUDO = '🛡️'     # Protege por 3 turnos

class Tablero:
    def __init__(self, filas=8, columnas=8, num_paredes=10, num_quesos=3):
        self.filas = max(8, filas)
        self.columnas = max(8, columnas)
        self.num_paredes = num_paredes
        self.num_quesos = num_quesos
        self.tablero = []
        self.gato_pos = None
        self.raton_pos = None
        self.quesos = []
        self.destino = None
        self.destino_alcanzable = False
        self.efectos_raton = {
            'escudo': 0,
            'velocidad': 0
        }
        
    def inicializar(self):
        """Crea un tablero con paredes, quesos, meta, obstáculos y jugadores."""
        self.tablero = [["🟪" for _ in range(self.columnas)] for _ in range(self.filas)]
        self.efectos_raton = {'escudo': 0, 'velocidad': 0}
        self._colocar_elementos()
        
    def _colocar_elementos(self):
        # Colocar paredes
        paredes_colocadas = 0
        while paredes_colocadas < self.num_paredes:
            fila, col = random.randint(0, self.filas-1), random.randint(0, self.columnas-1)
            if self.tablero[fila][col] == "🟪":
                self.tablero[fila][col] = '🧱'
                paredes_colocadas += 1
    
        # Colocar quesos
        self.quesos = []
        for _ in range(self.num_quesos):
            while True:
                fila, col = random.randint(0, self.filas-1), random.randint(0, self.columnas-1)
                if self.tablero[fila][col] == "🟪":
                    self.tablero[fila][col] = '🧀'
                    self.quesos.append((fila, col))
                    break
    
        # Colocar meta
        while True:
            fila, col = random.randint(0, self.filas-1), random.randint(0, self.columnas-1)
            if self.tablero[fila][col] == "🟪":
                self.tablero[fila][col] = '🏁'
                self.destino = (fila, col)
                break
    
        # Colocar obstáculos/power-ups con distribución más central
        elementos_especiales = [TRAMPA, TELEPORT, VELOCIDAD, ESCUDO]
        for elemento in elementos_especiales:
            while True:
                # Calcular área central (tercio central del tablero)
                fila_central_min = self.filas // 3
                fila_central_max = 2 * (self.filas // 3)
                col_central_min = self.columnas // 3
                col_central_max = 2 * (self.columnas // 3)
                
                # 70% de probabilidad de aparecer en área central, 30% en cualquier lugar
                if random.random() < 0.7:
                    fila = random.randint(fila_central_min, fila_central_max)
                    col = random.randint(col_central_min, col_central_max)
                else:
                    fila = random.randint(0, self.filas-1)
                    col = random.randint(0, self.columnas-1)
                    
                if self.tablero[fila][col] == "🟪":
                    self.tablero[fila][col] = elemento
                    break
    
        # Colocar gato
        while True:
            gato_fila, gato_col = random.randint(0, self.filas-1), random.randint(0, self.columnas-1)
            if self.tablero[gato_fila][gato_col] == SUELO and (gato_fila, gato_col) != self.destino:
                self.gato_pos = (gato_fila, gato_col)
                self.tablero[gato_fila][gato_col] = GATO
                break
    
        # Colocar ratón
        while True:
            raton_fila, raton_col = random.randint(0, self.filas-1), random.randint(0, self.columnas-1)
            if (self.tablero[raton_fila][raton_col] == SUELO and 
                (raton_fila, raton_col) != self.destino and 
                (raton_fila, raton_col) != self.gato_pos):
                self.raton_pos = (raton_fila, raton_col)
                self.tablero[raton_fila][raton_col] = RATON
                break
    
    def aplicar_efecto_especial(self, posicion):
        """Aplica efectos especiales cuando el ratón pisa un power-up/obstáculo."""
        fila, col = posicion
        elemento = self.tablero[fila][col]
        
        if elemento == TRAMPA:
            print(f"\n{Fore.RED}¡Oh no! El ratón cayó en una trampa {TRAMPA.strip()}. Pierde un turno.")
            return True  # Indica que el ratón pierde el turno
            
        elif elemento == TELEPORT:
            # Encontrar una posición aleatoria válida
            while True:
                nueva_fila = random.randint(0, self.filas-1)
                nueva_col = random.randint(0, self.columnas-1)
                if (self.tablero[nueva_fila][nueva_col] == "🟪" and 
                    (nueva_fila, nueva_col) != self.gato_pos and
                    (nueva_fila, nueva_col) != self.destino):
                    break
            
            print(f"\n{Fore.MAGENTA}¡El ratón fue teletransportado! {TELEPORT.strip()} De ({fila},{col}) a ({nueva_fila},{nueva_col})")
            self.tablero[fila][col] = SUELO
            self.raton_pos = (nueva_fila, nueva_col)
            self.tablero[nueva_fila][nueva_col] = RATON
            return False
            
        elif elemento == VELOCIDAD:
            print(f"\n{Fore.CYAN}¡Power-up de velocidad! {VELOCIDAD.strip()} El ratón se moverá dos veces en el próximo turno.")
            self.efectos_raton['velocidad'] = 1  # Se aplicará en el siguiente turno
            self.tablero[fila][col] = SUELO
            return False
            
        elif elemento == ESCUDO:
            print(f"\n{Fore.BLUE}¡Escudo activado! {ESCUDO.strip()} El gato no podrá atrapar al ratón por 3 turnos.")
            self.efectos_raton['escudo'] = 3
            self.tablero[fila][col] = SUELO
            return False
            
        return False
    
    def movimientos_validos(self, posicion, personaje):
        """Devuelve los movimientos válidos desde una posición (4 direcciones)."""
        fila, col = posicion
        direcciones = [
            (-1, 0),  # Arriba
            (1, 0),   # Abajo
            (0, -1),  # Izquierda
            (0, 1)     # Derecha
        ]
        movimientos = []
        for df, dc in direcciones:
            nueva_fila, nueva_col = fila + df, col + dc
            if 0 <= nueva_fila < self.filas and 0 <= nueva_col < self.columnas:
                celda = self.tablero[nueva_fila][nueva_col]
                # El gato no puede pasar trampas ni teletransportadores
                if personaje == Personaje.GATO and celda in [TRAMPA, TELEPORT]:
                    continue
                if celda != PARED:
                    movimientos.append((nueva_fila, nueva_col))
        return movimientos
    
    def mover_personaje(self, personaje, nueva_pos):
        """Mueve un personaje a una nueva posición."""
        pos_actual = self.gato_pos if personaje == Personaje.GATO else self.raton_pos
        simbolo = GATO if personaje == Personaje.GATO else RATON
        
        # Verificar si el ratón activa un efecto especial
        efecto_activado = False
        if personaje == Personaje.RATON:
            efecto_activado = self.aplicar_efecto_especial(nueva_pos)
            if efecto_activado:  # Si cayó en trampa, no se mueve
                return True
        
        # Actualizar tablero si no hay efecto que lo impida
        if not efecto_activado:
            self.tablero[pos_actual[0]][pos_actual[1]] = SUELO
            self.tablero[nueva_pos[0]][nueva_pos[1]] = simbolo
            
            # Actualizar posición
            if personaje == Personaje.GATO:
                self.gato_pos = nueva_pos
            else:
                self.raton_pos = nueva_pos
                
                # Recolectar queso si es el ratón
                if nueva_pos in self.quesos:
                    self.quesos.remove(nueva_pos)
                    if not self.quesos:
                        self.destino_alcanzable = True
                        print(f"\n{Fore.GREEN}¡Todos los quesos recolectados! La meta está habilitada.")
                
                # Verificar si llegó a la meta después de recolectar todos los quesos
                if self.destino_alcanzable and nueva_pos == self.destino:
                    self.tablero[nueva_pos[0]][nueva_pos[1]] = RATON  # Asegurar que se vea el ratón en la meta
        
        # Actualizar efectos del ratón
        if personaje == Personaje.RATON:
            if self.efectos_raton['escudo'] > 0:
                self.efectos_raton['escudo'] -= 1
            if self.efectos_raton['velocidad'] > 0:
                self.efectos_raton['velocidad'] -= 1
        
        return efecto_activado
    
    def imprimir(self):
        """Muestra el tablero en la consola con diseño perfectamente alineado."""
        # Calcular el ancho necesario para centrar el tablero
        # Calcular margen para centrar
        ancho_tablero = len(self.tablero[0]) * 2 + 2
        margen = (80 - ancho_tablero) // 2  # Asumiendo 80 caracteres de ancho de consola
        espacio = " " * margen
        
        # Función para imprimir con margen izquierdo
        def print_centered(text):
            print(" " * margen + text)
        
        console_width = 80  # Default console width; adjust as needed
        print("\n" + "=" * console_width)
        print_centered(f"{Fore.YELLOW}Quesos restantes: {len(self.quesos)}")
        if self.destino_alcanzable:
            print_centered(f"{Fore.GREEN}¡Puedes ir a la meta (🏁)!")
        else:
            print_centered(f"{Fore.YELLOW}Recolecta todos los quesos para habilitar la meta.")
        
        # Mostrar efectos activos del ratón
        if self.efectos_raton['escudo'] > 0:
            print_centered(f"{Fore.BLUE}Escudo activo: {self.efectos_raton['escudo']} turnos restantes {ESCUDO.strip()}")
        if self.efectos_raton['velocidad'] > 0:
            print_centered(f"{Fore.CYAN}¡Velocidad extra en el próximo turno! {VELOCIDAD.strip()}")
        
        print_centered("=" * ancho_tablero + "\n")
        
        # Imprimir números de columnas (perfectamente centrados)
        # Imprimir borde superior
        espacio = " " * ((80 - (len(self.tablero[0]) * 2 + 2)) // 2)  # Define 'espacio' based on the console width
        print(espacio + "╔" + "═" * (len(self.tablero[0]) * 2 + 10) + "╗")
    
        # Imprimir filas con bordes laterales
        for fila in self.tablero:
            print(espacio + "║ " + " ".join(fila) + " ║")
    
        # Imprimir borde inferior
        print(espacio + "╚" + "═" * (len(self.tablero[0]) * 2 + 10) + "╝")
        
class JuegoGatoRaton:
    def __init__(self):
        self.tablero = None
        self.turno = 0
        self.dificultad = Dificultad.MEDIO
        self.jugador_humano = None
        
    def configurar_juego(self):
        """Configura los parámetros iniciales del juego."""
        print(f"\n{Fore.CYAN}¡Bienvenido al Juego del Gato y el Ratón con IA y Power-ups!")
        
        # Configurar tamaño del tablero
        filas = int(input(f"{Fore.WHITE}Introduce el número de filas del tablero (mínimo 8): ") or 8)
        columnas = int(input("Introduce el número de columnas del tablero (mínimo 8): ") or 8)
        
        # Seleccionar personaje
        print(f"\n{Fore.WHITE}Elige tu personaje:")
        print(f"{Fore.BLUE}1. Ratón (escapar del gato IA y recolectar quesos)")
        print(f"{Fore.RED}2. Gato (atrapar al ratón IA)")
        while True:
            try:
                seleccion = int(input("Selección (1-2): "))
                if seleccion in [1, 2]:
                    break
                print("Por favor, introduce 1 o 2")
            except ValueError:
                print("Por favor, introduce un número válido")
        
        self.jugador_humano = Personaje.RATON if seleccion == 1 else Personaje.GATO
        
        # Configurar dificultad
        print(f"\n{Fore.WHITE}Niveles de dificultad:")
        print(f"{Fore.GREEN}1. Fácil")
        print(f"{Fore.YELLOW}2. Medio")
        print(f"{Fore.RED}3. Difícil")
        while True:
            try:
                nivel = int(input("Selecciona dificultad (1-3): "))
                if nivel in [1, 2, 3]:
                    break
                print("Por favor, introduce un número entre 1 y 3")
            except ValueError:
                print("Por favor, introduce un número válido")
        
        self.dificultad = [Dificultad.FACIL, Dificultad.MEDIO, Dificultad.DIFICIL][nivel-1]
        self.tablero = Tablero(filas, columnas)
        self.tablero.inicializar()
        
    def evaluar_estado(self):
        """Evalúa qué tan buena es la posición actual para el ratón."""
        # Si el gato atrapa al ratón (a menos que tenga escudo)
        if (self.tablero.raton_pos == self.tablero.gato_pos and 
            self.tablero.efectos_raton['escudo'] == 0):
            return -float('inf')
        
        # Si el ratón llega a la meta habilitada
        if (self.tablero.destino_alcanzable and 
            self.tablero.raton_pos == self.tablero.destino):
            return float('inf')
        
        # Distancia al gato (el ratón quiere maximizar esto)
        distancia_gato = abs(self.tablero.raton_pos[0] - self.tablero.gato_pos[0]) + abs(self.tablero.raton_pos[1] - self.tablero.gato_pos[1])
        
        # Distancia al queso más cercano (si quedan quesos)
        if self.tablero.quesos:
            distancia_queso = min(abs(self.tablero.raton_pos[0] - q[0]) + abs(self.tablero.raton_pos[1] - q[1]) for q in self.tablero.quesos)
            return distancia_gato * 2 + (10 / (distancia_queso + 1))
        
        # Si no quedan quesos, priorizar llegar a la meta
        distancia_meta = abs(self.tablero.raton_pos[0] - self.tablero.destino[0]) + abs(self.tablero.raton_pos[1] - self.tablero.destino[1])
        return distancia_gato * 2 + (10 / (distancia_meta + 1))
    
    def minimax_alpha_beta(self, profundidad, alpha, beta, es_maximizador):
        """Algoritmo Minimax con poda Alpha-Beta."""
        # Verificar condiciones de terminación
        if (self.tablero.raton_pos == self.tablero.gato_pos and 
            self.tablero.efectos_raton['escudo'] == 0):
            return -1000 if es_maximizador else 1000
        if (self.tablero.destino_alcanzable and 
            self.tablero.raton_pos == self.tablero.destino):
            return 1000 if es_maximizador else -1000
        if profundidad == 0:
            return self.evaluar_estado()
        
        if es_maximizador:  # Turno del ratón
            valor = -float('inf')
            for mov in self.tablero.movimientos_validos(self.tablero.raton_pos, Personaje.RATON):
                # Guardar estado actual
                raton_pos_original = self.tablero.raton_pos
                quesos_original = self.tablero.quesos.copy()
                destino_alcanzable_original = self.tablero.destino_alcanzable
                efectos_original = self.tablero.efectos_raton.copy()
                
                # Simular movimiento
                self.tablero.raton_pos = mov
                if mov in self.tablero.quesos:
                    self.tablero.quesos.remove(mov)
                    if not self.tablero.quesos:
                        self.tablero.destino_alcanzable = True
                
                # Simular efectos especiales (solo para evaluación)
                celda = self.tablero.tablero[mov[0]][mov[1]]
                if celda == VELOCIDAD:
                    self.tablero.efectos_raton['velocidad'] = 1
                elif celda == ESCUDO:
                    self.tablero.efectos_raton['escudo'] = 3
                
                valor = max(valor, self.minimax_alpha_beta(
                    profundidad-1, alpha, beta, False
                ))
                
                # Restaurar estado
                self.tablero.raton_pos = raton_pos_original
                self.tablero.quesos = quesos_original.copy()
                self.tablero.destino_alcanzable = destino_alcanzable_original
                self.tablero.efectos_raton = efectos_original.copy()
                
                alpha = max(alpha, valor)
                if alpha >= beta:
                    break  # Poda Beta
            return valor
        else:  # Turno del gato
            valor = float('inf')
            for mov in self.tablero.movimientos_validos(self.tablero.gato_pos, Personaje.GATO):
                # Guardar estado actual
                gato_pos_original = self.tablero.gato_pos
                
                # Simular movimiento
                self.tablero.gato_pos = mov
                
                valor = min(valor, self.minimax_alpha_beta(
                    profundidad-1, alpha, beta, True
                ))
                
                # Restaurar estado
                self.tablero.gato_pos = gato_pos_original
                
                beta = min(beta, valor)
                if alpha >= beta:
                    break  # Poda Alpha
            return valor
    
    def mejor_movimiento_ia(self, personaje):
        """Elige el mejor movimiento para la IA usando Minimax."""
        mejor_valor = -float('inf') if personaje == Personaje.RATON else float('inf')
        mejor_mov = None
        posicion = self.tablero.raton_pos if personaje == Personaje.RATON else self.tablero.gato_pos
        
        for mov in self.tablero.movimientos_validos(posicion, personaje):
            # Guardar estado actual
            raton_pos_original = self.tablero.raton_pos
            gato_pos_original = self.tablero.gato_pos
            quesos_original = self.tablero.quesos.copy()
            destino_alcanzable_original = self.tablero.destino_alcanzable
            efectos_original = self.tablero.efectos_raton.copy()
            
            # Simular movimiento
            if personaje == Personaje.RATON:
                self.tablero.raton_pos = mov
                if mov in self.tablero.quesos:
                    self.tablero.quesos.remove(mov)
                    if not self.tablero.quesos:
                        self.tablero.destino_alcanzable = True
                
                # Simular efectos especiales para la evaluación
                celda = self.tablero.tablero[mov[0]][mov[1]]
                if celda == VELOCIDAD:
                    self.tablero.efectos_raton['velocidad'] = 1
                elif celda == ESCUDO:
                    self.tablero.efectos_raton['escudo'] = 3
            else:
                self.tablero.gato_pos = mov
            
            valor = self.minimax_alpha_beta(
                self.dificultad.value, 
                -float('inf'), 
                float('inf'), 
                personaje == Personaje.RATON
            )
            
            # Restaurar estado
            self.tablero.raton_pos = raton_pos_original
            self.tablero.gato_pos = gato_pos_original
            self.tablero.quesos = quesos_original.copy()
            self.tablero.destino_alcanzable = destino_alcanzable_original
            self.tablero.efectos_raton = efectos_original.copy()
            
            # Actualizar mejor movimiento
            if personaje == Personaje.RATON:
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_mov = mov
            else:
                if valor < mejor_valor:
                    mejor_valor = valor
                    mejor_mov = mov
        
        return mejor_mov if mejor_mov is not None else posicion
    
    def movimiento_humano(self, personaje):
        """Obtiene el movimiento del jugador humano usando teclas estilo PC"""
        pos_actual = self.tablero.raton_pos if personaje == Personaje.RATON else self.tablero.gato_pos
        mov_validos = self.tablero.movimientos_validos(pos_actual, personaje)
        
        # Mapeo de teclas a direcciones (relativas a la posición actual)
        teclas = {
            'w': (-1, 0),   # Arriba
            's': (1, 0),    # Abajo
            'a': (0, -1),   # Izquierda
            'd': (0, 1)     # Derecha
        }
        
        color = Fore.BLUE if personaje == Personaje.RATON else Fore.RED
        print(f"\n{color}Usa las siguientes teclas para moverte:")
        print("w - Arriba")
        print("a - Izquierda")
        print("s - Abajo")
        print("d - Derecha")
        print(f"{Fore.WHITE}Presiona la tecla y luego Enter")
        
        while True:
            tecla = input("Tu movimiento (w/a/s/d): ").lower()
            if tecla in teclas:
                df, dc = teclas[tecla]
                nueva_pos = (pos_actual[0] + df, pos_actual[1] + dc)
                if nueva_pos in mov_validos:
                    return nueva_pos
                print(f"{Fore.RED}Movimiento inválido. No puedes moverte allí.")
            else:
                print(f"{Fore.RED}Tecla inválida. Usa sólo: w (arriba), a (izquierda), s (abajo), d (derecha)")
    
    def jugar_partida(self):
        """Función principal para jugar una partida."""
        self.turno = 0
        self.configurar_juego()
        
        print(f"\n{Fore.CYAN}Objetivo:")
        if self.jugador_humano == Personaje.RATON:
            print(f"{Fore.BLUE}Recolecta todos los quesos (🧀) y luego llega a la meta (🏁).")
            print(f"El gato (🐱) te perseguirá usando inteligencia artificial.")
        else:
            print(f"{Fore.RED}Atrapa al ratón (🐭) antes de que recolecte todos los quesos y llegue a la meta.")
            print(f"El ratón usará inteligencia artificial para escapar.")
        
        print(f"\n{Fore.MAGENTA}Elementos especiales:")
        print(f"{TRAMPA.strip()} {Fore.WHITE}Trampa - El ratón pierde un turno")
        print(f"{TELEPORT.strip()} {Fore.MAGENTA}Teletransporte - Mueve al ratón a lugar aleatorio")
        print(f"{VELOCIDAD.strip()} {Fore.CYAN}Velocidad - El ratón se mueve dos veces en el próximo turno")
        print(f"{ESCUDO.strip()} {Fore.BLUE}Escudo - Protege al ratón del gato por 3 turnos")
        
        print(f"\n{Fore.YELLOW}Controles:")
        print("w - Arriba")
        print("a - Izquierda")
        print("s - Abajo")
        print("d - Derecha")
        
        input(f"\n{Fore.GREEN}Presiona Enter para comenzar...")
        
        while True:
            self.turno += 1
            print(f"\n{Fore.WHITE}--- Turno {self.turno} ---")
            self.tablero.imprimir()
            
            # Turno del ratón
            if self.jugador_humano == Personaje.RATON:
                nueva_pos = self.movimiento_humano(Personaje.RATON)
                efecto_activado = self.tablero.mover_personaje(Personaje.RATON, nueva_pos)
                
                # Si el ratón tiene velocidad, se mueve otra vez
                if (not efecto_activado and 
                    self.tablero.efectos_raton['velocidad'] > 0 and 
                    self.jugador_humano == Personaje.RATON):
                    print(f"\n{Fore.CYAN}¡Movimiento extra por velocidad! {VELOCIDAD.strip()}")
                    self.tablero.imprimir()
                    nueva_pos = self.movimiento_humano(Personaje.RATON)
                    self.tablero.mover_personaje(Personaje.RATON, nueva_pos)
            else:
                print(f"{Fore.BLUE}Turno del ratón (IA)...")
                time.sleep(1)
                nueva_pos = self.mejor_movimiento_ia(Personaje.RATON)
                efecto_activado = self.tablero.mover_personaje(Personaje.RATON, nueva_pos)
                
                # Si el ratón tiene velocidad, se mueve otra vez
                if not efecto_activado and self.tablero.efectos_raton['velocidad'] > 0:
                    print(f"\n{Fore.CYAN}¡El ratón usa su movimiento extra! {VELOCIDAD.strip()}")
                    time.sleep(1)
                    nueva_pos = self.mejor_movimiento_ia(Personaje.RATON)
                    self.tablero.mover_personaje(Personaje.RATON, nueva_pos)
            
            # Verificar si el ratón llegó a la meta después de recolectar todos los quesos
            if (self.tablero.destino_alcanzable and 
                self.tablero.raton_pos == self.tablero.destino):
                self.tablero.imprimir()
                print(f"{Fore.GREEN}¡El ratón recolectó todos los quesos y llegó a la meta! 🐭🎉")
                if self.jugador_humano == Personaje.RATON:
                    print(f"{Fore.GREEN}¡Ganaste!✨")
                else:
                    print(f"{Fore.RED}¡Perdiste!💔")
                break
            
            # Verificar si el gato atrapó al ratón (solo si no tiene escudo)
            if (self.tablero.raton_pos == self.tablero.gato_pos and 
                self.tablero.efectos_raton['escudo'] == 0):
                self.tablero.imprimir()
                print(f"{Fore.RED}¡El gato atrapó al ratón! 😸🎉")
                if self.jugador_humano == Personaje.GATO:
                    print(f"{Fore.GREEN}¡Ganaste!✨")
                else:
                    print(f"{Fore.RED}¡Perdiste!💔")
                break
            elif self.tablero.raton_pos == self.tablero.gato_pos:
                print(f"\n{Fore.BLUE}¡El escudo protegió al ratón del gato! {ESCUDO.strip()}")
            
            # Turno del gato
            if self.jugador_humano == Personaje.GATO:
                nueva_pos = self.movimiento_humano(Personaje.GATO)
                self.tablero.mover_personaje(Personaje.GATO, nueva_pos)
            else:
                print(f"{Fore.RED}Turno del gato (IA)...")
                time.sleep(1)
                nueva_pos = self.mejor_movimiento_ia(Personaje.GATO)
                self.tablero.mover_personaje(Personaje.GATO, nueva_pos)
            
            # Verificar si el gato atrapó al ratón (solo si no tiene escudo)
            if (self.tablero.raton_pos == self.tablero.gato_pos and 
                self.tablero.efectos_raton['escudo'] == 0):
                self.tablero.imprimir()
                print(f"{Fore.RED}¡El gato atrapó al ratón! 😸🎉🧶")
                if self.jugador_humano == Personaje.GATO:
                    print(f"{Fore.GREEN}¡Ganaste!✨")
                else:
                    print(f"{Fore.RED}¡Perdiste!💔")
                break
            elif self.tablero.raton_pos == self.tablero.gato_pos:
                print(f"\n{Fore.BLUE}¡El escudo protegió al ratón del gato! {ESCUDO.strip()}")
            
            time.sleep(1)  # Pequeña pausa entre turnos
    
    def jugar(self):
        """Función principal que maneja múltiples partidas."""
        while True:
            self.jugar_partida()
            
            # Preguntar si quiere jugar otra vez
            while True:
                respuesta = input(f"\n{Fore.WHITE}¿Quieres jugar otra vez? (s/n): ").lower()
                if respuesta in ['s', 'n']:
                    break
                print(f"{Fore.RED}Por favor, introduce 's' para sí o 'n' para no")
            
            if respuesta == 'n':
                print(f"\n{Fore.CYAN}¡Gracias por jugar! Hasta la próxima 👋")
                break

if __name__ == "__main__":
    juego = JuegoGatoRaton()
    juego.jugar()