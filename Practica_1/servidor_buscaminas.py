#Flores Estopier Rodrigo
#Aplicaciones para comunicaciones en red 6CV1
#Fecha de creacion: 28/09/2024

import socket
import random
from datetime import datetime

buffer_size = 1024

class Tablero:
    def __init__(self, filas, columnas, numminas):
        self.filas = filas
        self.columnas = columnas
        self.numminas = numminas
        self.tablero = [['0' for _ in range(columnas)] for _ in range(filas)]
        self.colocar_minas()
        self.iniciar_tiempo()
        self.casillas_descubiertas = 0

    def colocar_minas(self):
        minas_colocadas = 0
        #print(self.filas)
        #print(self.columnas)
        while minas_colocadas < self.numminas:
            x = random.randint(0, self.filas - 1)
            y = random.randint(0, self.columnas - 1)
            if self.tablero[x][y] != 'M':
                self.tablero[x][y] = 'M'
                #print(f"Mina colocada en: {x}, {y}")
                minas_colocadas += 1
        self.imprimir_tablero()
    def imprimir_tablero(self):
        for i in range(self.filas):
            for j in range(self.columnas):
                print(self.tablero[i][j], end=" ")
            print()

        

    def iniciar_tiempo(self):
        self.tiempo_inicio = datetime.now()

    def finalizar_tiempo(self):
        self.tiempo_fin = datetime.now()
        self.duracion = self.tiempo_fin - self.tiempo_inicio

def manejar_cliente(conn, addr):
    print(f"Conexión establecida desde {addr}")
    try:
        # Recibir elección de dificultad
        data = conn.recv(buffer_size)
        dificultad = data.decode()
        print(f"Dificultad elegida: {dificultad}")
        dificultad = int(dificultad)

        if dificultad == 1:
            filas, columnas, minas = 9, 9, 10
        elif dificultad == 2:
            filas, columnas, minas = 16, 16, 40
        else:
            # Enviar mensaje de error
            mensaje = "Dificultad no válida."
            conn.send(mensaje.encode())
            conn.close()
            return

        # Crear tablero
        tablero = Tablero(filas, columnas, minas)

        # Enviar confirmación
        confirmacion = "Juego iniciado."
        conn.send(confirmacion.encode())

        # Bucle del juego
        while True:
            data = conn.recv(buffer_size)
            if not data:
                break
            mensaje = data.decode()
            x,y = mensaje.split(",")
            print(f"Coordenadas recibidas: {x}, {y}")

            if x.isdigit() and y.isdigit():
                x = int(x)
                y = int(y)

                if x < 0 or x >= filas or y < 0 or y >= columnas:
                    respuesta = "Coordenadas fuera de rango."
                    conn.send(respuesta.encode())
                    continue

                if tablero.tablero[x][y] == 'M':
                    # Perdiste
                    tablero.finalizar_tiempo()
                    respuesta = "mina pisada"
                    conn.send(respuesta.encode())

                    # Enviar todas las minas
                    for i in range(filas):
                        for j in range(columnas):
                            if tablero.tablero[i][j] == 'M':
                                mina = f"{i},{j}"
                                #print(f"Mina en: {mina}")
                                conn.send(mina.encode())
                                # Esperar a que el cliente reciba la mina
                                conn.recv(buffer_size)
                    #Esperar a que el cliente reciba las minas
                    conn.recv(buffer_size)
                    conn.send(str(tablero.duracion).encode())            
                    break
                else:
                    # Casilla libre
                    tablero.casillas_descubiertas += 1
                    respuesta = "Casilla libre."
                    conn.send(respuesta.encode())

                    #print(tablero.casillas_descubiertas)
                    #print(filas * columnas - minas)
                    # Verificar si ganó
                    if tablero.casillas_descubiertas == (filas * columnas - minas):
                        #print("Ganaste")
                        tablero.finalizar_tiempo()
                        respuesta_ganar = "ganaste"
                        conn.send(respuesta_ganar.encode() +",".encode()+str(tablero.duracion).encode())
                        break
            else:
                print("Coordenadas inválidas. Deben ser números enteros.")
            #print("Turno")
            conn.send("a".encode())

        print(f"Conexión cerrada desde {addr}")
    except Exception as e:
        print(f"Error con {addr}: {e}")
    finally:
        conn.close()

def iniciar_servidor(ip, puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((ip, puerto))
    servidor.listen()
    print(f"Servidor escuchando en {ip}:{puerto}")

    Client_conn, Client_addr = servidor.accept()
    manejar_cliente(Client_conn, Client_addr)



if __name__ == "__main__":
    ip_servidor = input("Ingrese la IP del servidor: ")
    puerto_servidor = int(input("Ingrese el puerto del servidor: "))
    iniciar_servidor(ip_servidor, puerto_servidor)
