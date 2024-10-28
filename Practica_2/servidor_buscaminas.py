import socket
import threading
import sys
import random
from datetime import datetime
import time

buffer_size = 1024
# Crear una bandera de control para detener el hilo
detener_hilo = threading.Event()

class Conexion:
    def __init__(self, ip, port, conn_socket, thread, state=0):
        self.ip = ip
        self.port = port
        self.conn_socket = conn_socket
        self.thread = thread
        self.state = state

    def update_state(self, new_state):
        self.state = new_state

class Tablero:
    def __init__(self, filas, columnas, numminas):
        self.filas = filas
        self.columnas = columnas
        self.numminas = numminas
        self.tablero = [['0' for _ in range(columnas)] for _ in range(filas)]
        self.colocar_minas()
        self.iniciar_tiempo()
        self.casillas_descubiertas = 0
        self.casillas_descubiertasTuplas = []

    def colocar_minas(self):
        minas_colocadas = 0     
        while minas_colocadas < self.numminas:
            x = random.randint(0, self.filas - 1)
            y = random.randint(0, self.columnas - 1)
            if self.tablero[x][y] != 'M':
                self.tablero[x][y] = 'M'
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


def manejar_cliente(conexxion, addr, tablero, conexiones):
    conexxion.update_state(1)  # Estado 1: running
    print(f"Conexión establecida desde {addr}")

    try:
        # Enviar la dificultad al cliente
        dificultad = 1 if tablero.filas == 9 else 2
        conexxion.conn_socket.send(str(dificultad).encode())
        
        # Recibir confirmación de recepción de dificultad
        while True:
            try:
                dataC = conexxion.conn_socket.recv(buffer_size)
                if dataC:
                    break
            except BlockingIOError:
                # No hay datos disponibles en este momento, continuar
                continue


        
        
        # Enviar confirmación
        conexxion.conn_socket.send("Juego iniciado.".encode())

        while True:
            try:
                data = conexxion.conn_socket.recv(buffer_size)
                if not data:
                    break

                if data.decode() == "EOF":
                    conexxion.update_state(2)  # Estado 2: stopping
                    break

                x, y = map(int, data.decode().split(","))
                if x < 0 or x >= filas or y < 0 or y >= columnas:
                    conexxion.conn_socket.send("Coordenadas fuera de rango.".encode())
                    continue
                if (x, y) in tablero.casillas_descubiertasTuplas:
                    conexxion.conn_socket.send("Casilla ya descubierta.".encode())
                    continue

                # Verificar si hay mina
                if tablero.tablero[x][y] == 'M':
                    tablero.finalizar_tiempo()
                    broadcast(conexiones, f"{addr} pisó una mina")
                    time.sleep(1)
                    broadcast(conexiones, "mina pisada")
                    time.sleep(1)
                    for i in range(filas):
                        for j in range(columnas):
                            if tablero.tablero[i][j] == 'M':
                                broadcast(conexiones, f"{i},{j}")
                                time.sleep(0.01)
                    broadcast(conexiones, str(tablero.duracion))
                    break
                else:
                    tablero.casillas_descubiertas += 1
                    tablero.casillas_descubiertasTuplas.append((x, y))

                    if tablero.casillas_descubiertas == (filas * columnas - minas):
                        tablero.finalizar_tiempo()
                        conexxion.conn_socket.send(f"ganaste,{str(tablero.duracion)}".encode())
                        #Enviar mensaje a todos los clientes
                        time.sleep(1)
                        broadcast(conexiones, f"{addr} ganó. Fin del juego.")
                        time.sleep(1)
                        broadcast(conexiones, str(tablero.duracion))
                        break
                    else:
                        broadcast(conexiones, f"{addr} descubrió {x},{y} - Casilla libre")
                        broadcast(conexiones, f"{x},{y}")
            except BlockingIOError:
                # No hay datos disponibles en este momento, continuar
                pass
    except Exception as e:
        print(f"Error con {addr}")
        conexxion.update_state(4)
    finally:
        limpiarConexion(conexxion, conexiones)


def limpiarConexion(conexion, lista_conexiones):
    print(f"Cerrando conexión con {conexion.ip}:{conexion.port}")
    try:
        conexion.conn_socket.close()
        conexion.update_state(3)  # Estado 3: stopped
    except Exception as e:
        print(f"Error al cerrar conexión con {conexion.ip}:{conexion.port}: {e}")
        conexion.update_state(4)  # Estado 4: failed
    finally:
        if conexion in lista_conexiones:
            lista_conexiones.remove(conexion)
        print(f"Conexión con {conexion.ip}:{conexion.port} cerrada correctamente.")
        #gestion_conexiones(lista_conexiones)
        if len(lista_conexiones) == 0:
            detener_hilo.set()
            print("No hay más conexiones. Finalizando el juego.")


def broadcast(conexiones, mensaje):
    for conn in conexiones:
        if conn.state == 1:  # Solo envía a conexiones activas
            try:
                conn.conn_socket.send(mensaje.encode())
            except Exception as e:
                conn.update_state(4) # Estado 4: failed
                print(f"Error al enviar mensaje: {e}")


def gestion_conexiones(lista_conexiones):
    for conexion in list(lista_conexiones):
        if conexion.conn_socket.fileno() == -1:
            conexion.update_state(4)
            lista_conexiones.remove(conexion)
        print(f"Conexión {conexion.ip}:{conexion.port} en estado {conexion.state}")
    print("Hilos activos:", threading.active_count())
    print("Conexiones:", len(lista_conexiones))
    

def servirPorSiempre(socketTcp, lista_conexiones, tablero):
    while not detener_hilo.is_set():
        try:
            client_conn, client_addr = socketTcp.accept()
            print("Conectando a", client_addr)
            # Estado 0: starting
            nueva_conexion = Conexion(client_addr[0], client_addr[1], client_conn, None, state=0)
            lista_conexiones.append(nueva_conexion)

            # Crear y arrancar el hilo para el cliente
            thread_read = threading.Thread(target=manejar_cliente, args=(nueva_conexion, client_addr, tablero, lista_conexiones))
            nueva_conexion.thread = thread_read  # Asignar el hilo a la conexión
            thread_read.start()
            
            gestion_conexiones(lista_conexiones)
        except BlockingIOError:
            time.sleep(5)
            gestion_conexiones(lista_conexiones)

     # Una vez que se setea detener_hilo, cerrar todas las conexiones y esperar a que terminen sus hilos
    for conexion in lista_conexiones:
        limpiarConexion(conexion, lista_conexiones)

    print("Servidor cerrado y todos los hilos de cliente han finalizado.")

    


# Inicialización del servidor y lista de conexiones
listaConexiones = []
if len(sys.argv) != 5:
    print("usage:", sys.argv[0], "<host> <port> <num_connections> <dificultad (1,2)>")
    sys.exit(1)

host, port, numConn, dificultad = sys.argv[1:5]
serveraddr = (host, int(port))

# Crear tablero
if dificultad == '1':
    filas, columnas, minas = 9, 9, 10
elif dificultad == '2':
    filas, columnas, minas = 16, 16, 40
else:
    print("Dificultad no válida. Intente de nuevo.")
    sys.exit(1)

tablero = Tablero(filas, columnas, minas)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(numConn))
    TCPServerSocket.setblocking(False)
    print("El servidor TCP está disponible y en espera de solicitudes")

    servirPorSiempre(TCPServerSocket, listaConexiones, tablero)
    TCPServerSocket.close()
    print("Cerrando el servidor...")
