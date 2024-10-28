#!/usr/bin/env python3

import socket
import sys
import threading

def servirPorSiempre(socketTcp, listaconexiones):
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print("Conectado a", client_addr)
            listaconexiones.append(client_conn)
            thread_read = threading.Thread(target=recibir_datos, args=[client_conn, client_addr, listaconexiones])
            thread_read.start()
            gestion_conexiones(listaconexiones)
    except Exception as e:
        print(e)

def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    #print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    #print(listaconexiones)

def recibir_datos(conn, addr, listaconexiones):
    try:
        cur_thread = threading.current_thread()
        print("Recibiendo datos del cliente {} en el {}".format(addr, cur_thread.name))
        while True:
            data = conn.recv(1024)
            if data.decode('utf-8') == "EOF":
                conn.sendall("".encode())
                print("Fin de conexión con", addr)
                break
            print(f"Mensaje recibido de {addr}: {data.decode()}")
            
            # Llamada a la función de envío masivo (opcional, solo si se desea hacer al recibir un mensaje)
            enviar_a_todos(listaconexiones, "Mensaje Masivo")

            # Respuesta al cliente individual
            #response = bytes(f"{cur_thread.name}: {data.decode()}", 'ascii')
            #conn.sendall(response)
    except Exception as e:
        print(e)
    finally:
        conn.close()

def enviar_a_todos(listaconexiones, mensaje):
    print("Enviando mensaje a todos los clientes...")
    for conn in listaconexiones:
        if conn.fileno() != -1:  # Solo envía a conexiones activas
            try:
                conn.sendall(bytes(mensaje, 'ascii'))
            except Exception as e:
                print(f"Error al enviar mensaje a {conn.getpeername()}: {e}")

listaConexiones = []
host, port, numConn = sys.argv[1:4]

if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <num_connections>")
    sys.exit(1)

serveraddr = (host, int(port))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(numConn))
    print("El servidor TCP está disponible y en espera de solicitudes")

    servirPorSiempre(TCPServerSocket, listaConexiones)
