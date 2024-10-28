#!/usr/bin/env python3
# Flores Estopier Rodrigo

import socket
import sys
import threading

def recibir_mensajes(cliente_socket):
    try:
        while True:
            mensaje = cliente_socket.recv(1024)
            if not mensaje:
                print("Conexión cerrada por el servidor.")
                break
            print("Mensaje recibido:", mensaje.decode())
    except Exception as e:
        print("Error en la recepción de mensajes:", e)
    finally:
        cliente_socket.close()

def enviar_mensajes(cliente_socket):
    try:
        while True:
            mensaje = input("Escribe un mensaje para enviar al servidor (o enter para terminar): ")
            if not mensaje:
                cliente_socket.sendall(str.encode("EOF"))
                print("Cerrando conexión...")
                break
            cliente_socket.sendall(mensaje.encode())
    except Exception as e:
        print("Error al enviar el mensaje:", e)

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente_socket:
    cliente_socket.connect((host, port))
    print("Conectado al servidor en {}:{}".format(host, port))

    # Inicia hilo para recibir mensajes del servidor
    thread_recibir = threading.Thread(target=recibir_mensajes, args=[cliente_socket])
    thread_recibir.start()

    # Inicia hilo para enviar mensajes al servidor
    thread_enviar = threading.Thread(target=enviar_mensajes, args=[cliente_socket])
    thread_enviar.start()

    # Espera a que ambos hilos terminen
    thread_recibir.join()
    thread_enviar.join()
    print("Conexión cerrada.")
