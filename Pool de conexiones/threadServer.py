#!/usr/bin/env python3
# Flores Estopier Rodrigo
import socket
import sys
import threading


class Conexion:
    def __init__(self, ip, port, conn_socket, thread, state=0):
        self.ip = ip
        self.port = port
        self.conn_socket = conn_socket
        self.thread = thread
        self.state = state

    def update_state(self, new_state):
        self.state = new_state


def servirPorSiempre(socketTcp, lista_conexiones):
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print("Conectado a", client_addr)
            # Estado 0: starting
            nueva_conexion = Conexion(client_addr[0], client_addr[1], client_conn, None, state=0)
            lista_conexiones.append(nueva_conexion)

            thread_read = threading.Thread(target=recibir_datos, args=[nueva_conexion, lista_conexiones])
            nueva_conexion.thread = thread_read  # Asignar el hilo a la conexión
            thread_read.start()
            gestion_conexiones(lista_conexiones)
    except Exception as e:
        print(e)


def gestion_conexiones(lista_conexiones):
    # Revisar y actualizar el estado de cada conexión
    for conexion in list(lista_conexiones):
        if conexion.conn_socket.fileno() == -1:
            # Estado 4: failed
            conexion.update_state(4)
            lista_conexiones.remove(conexion)
    print("hilos activos:", threading.active_count())
    print("conexiones: ", len(lista_conexiones))
    #Imprimir el estado de cada conexion
    for conexion in lista_conexiones:
        print(f"Conexión {conexion.ip}:{conexion.port} en estado {conexion.state}")



def recibir_datos(conexion, lista_conexiones):
    try:
        conexion.update_state(1)  # Estado 1: running
        cur_thread = threading.current_thread()
        print("Recibiendo datos del cliente {}:{} en el {}".format(conexion.ip, conexion.port, cur_thread.name))

        while True:
            data = conexion.conn_socket.recv(1024)
            if not data:
                break
            mensaje = data.decode('utf-8')

            if mensaje == "EOF":
                conexion.update_state(2)  # Estado 2: stopping
                print("Cliente {}:{} ha solicitado terminar.".format(conexion.ip, conexion.port))
                break
            
            print(f"Mensaje recibido de {conexion.ip}:{conexion.port}: {mensaje}")

            
            # Llamada a la función de envío masivo para distribuir el mensaje
            enviar_a_todos(lista_conexiones, "Mensaje Universal desde el servidor")

            

        # Estado 3: stopped
        conexion.update_state(3)
    except Exception as e:
        print(e)
        # Estado 4: failed
        conexion.update_state(4)
    finally:
        limpiarConexion(conexion, lista_conexiones)


def enviar_a_todos(lista_conexiones, mensaje):
    """Envia el mensaje a todos los clientes conectados"""
    print("Enviando mensaje a todos los clientes...")
    for conexion in lista_conexiones:
        if conexion.state == 1:  # Solo envía a conexiones activas
            try:
                conexion.conn_socket.sendall(bytes(mensaje, 'utf-8'))
            except Exception as e:
                print(f"Error al enviar mensaje a {conexion.ip}:{conexion.port}: {e}")


def limpiarConexion(conexion, lista_conexiones):
    print(f"Cerrando conexión con {conexion.ip}:{conexion.port}")
    try:
        conexion.conn_socket.close()  # Cerrar la conexión de manera segura
    except Exception as e:
        print(f"Error al cerrar conexión con {conexion.ip}:{conexion.port}:", e)
    finally:
        if conexion in lista_conexiones:
            lista_conexiones.remove(conexion)  # Remover la conexión de la lista
        print(f"Conexión con {conexion.ip}:{conexion.port} cerrada correctamente.")


# Inicialización del servidor y lista de conexiones
listaConexiones = []
if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <num_connections>")
    sys.exit(1)

host, port, numConn = sys.argv[1:4]
serveraddr = (host, int(port))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(numConn))
    print("El servidor TCP está disponible y en espera de solicitudes")

    servirPorSiempre(TCPServerSocket, listaConexiones)
