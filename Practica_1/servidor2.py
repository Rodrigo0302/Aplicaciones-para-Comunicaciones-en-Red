import socket
import threading
import json
import random
from datetime import datetime

def es_bisiesto(anio):
    return (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)

class Tablero:
    def __init__(self, filas, columnas, minas):
        self.filas = filas
        self.columnas = columnas
        self.minas = minas
        self.tablero = [['0' for _ in range(columnas)] for _ in range(filas)]
        self.colocar_minas()
        self.iniciar_tiempo()
        self.casillas_descubiertas = 0

    def colocar_minas(self):
        minas_colocadas = 0
        while minas_colocadas < self.minas:
            x = random.randint(0, self.filas - 1)
            y = random.randint(0, self.columnas - 1)
            if self.tablero[x][y] != 'M':
                self.tablero[x][y] = 'M'
                print(f"Mina colocada en: {x}, {y}")
                minas_colocadas += 1

    def iniciar_tiempo(self):
        self.tiempo_inicio = datetime.now()

    def finalizar_tiempo(self):
        self.tiempo_fin = datetime.now()
        self.duracion = self.tiempo_fin - self.tiempo_inicio

def manejar_cliente(conn, addr):
    print(f"Conexión establecida desde {addr}")
    try:
        # Recibir elección de dificultad
        data = conn.recv(1024).decode()
        eleccion = json.loads(data)
        dificultad = eleccion.get("dificultad")

        if dificultad == "principiante":
            filas, columnas, minas = 9, 9, 10
        elif dificultad == "avanzado":
            filas, columnas, minas = 16, 16, 40
        else:
            # Enviar mensaje de error
            mensaje = {"tipo": "control", "resultado": "error", "mensaje": "Dificultad no válida."}
            conn.send(json.dumps(mensaje).encode())
            conn.close()
            return

        # Crear tablero
        tablero = Tablero(filas, columnas, minas)

        # Enviar confirmación
        confirmacion = {"tipo": "control", "resultado": "confirmacion", "mensaje": "Juego iniciado."}
        conn.send(json.dumps(confirmacion).encode())

        # Bucle del juego
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            mensaje = json.loads(data)
            if mensaje.get("tipo") == "coordenadas":
                x = mensaje.get("x")
                y = mensaje.get("y")
                if x < 0 or x >= filas or y < 0 or y >= columnas:
                    respuesta = {"tipo": "control", "resultado": "error", "mensaje": "Coordenadas fuera de rango."}
                    conn.send(json.dumps(respuesta).encode())
                    continue

                if tablero.tablero[x][y] == 'M':
                    # Perdiste
                    tablero.finalizar_tiempo()
                    respuesta = {"tipo": "control", "resultado": "mina pisada", "mensaje": "Has perdido."}
                    conn.send(json.dumps(respuesta).encode())
                    # Enviar todas las minas
                    for i in range(filas):
                        for j in range(columnas):
                            if tablero.tablero[i][j] == 'M':
                                todas_minas = {"tipo": "control", "resultado": "mina", "x": i, "y": j}
                                conn.send(json.dumps(todas_minas).encode())
                    break
                else:
                    # Casilla libre
                    tablero.casillas_descubiertas += 1
                    respuesta = {"tipo": "control", "resultado": "Ok", "mensaje": "Casilla libre."}
                    conn.send(json.dumps(respuesta).encode())

                    # Verificar si ganó
                    if tablero.casillas_descubiertas == (filas * columnas - minas):
                        tablero.finalizar_tiempo()
                        respuesta_ganar = {
                            "tipo": "control",
                            "resultado": "ganaste",
                            "mensaje": "Has ganado la partida.",
                            "duracion": str(tablero.duracion)
                        }
                        conn.send(json.dumps(respuesta_ganar).encode()
                                   )
                        break

        print(f"Conexión cerrada desde {addr}")
    except Exception as e:
        print(f"Error con {addr}: {e}")
    finally:
        conn.close()

def iniciar_servidor(ip, puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((ip, puerto))
    servidor.listen(5)
    print(f"Servidor escuchando en {ip}:{puerto}")

    while True:
        conn, addr = servidor.accept()
        cliente_thread = threading.Thread(target=manejar_cliente, args=(conn, addr))
        cliente_thread.start()

if __name__ == "__main__":
    ip_servidor = input("Ingrese la IP del servidor: ")
    puerto_servidor = int(input("Ingrese el puerto del servidor: "))
    iniciar_servidor(ip_servidor, puerto_servidor)
