#!/usr/bin python3
#Flores Estopier Rodrigo
import socket
import time
HOST = "127.0.0.1"  # Hostname o  dirección IP del servidor
PORT = 8080  # Puerto del servidor
buffer_size = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
    TCPClientSocket.connect((HOST, PORT))
    print("Enviando mensaje...")
    with open("./MobyDick.txt", "r") as archivo:
        for linea in archivo.readlines():
            print(linea)
            TCPClientSocket.sendall( str.encode(linea))
    #Enviar mensaje de finalización
    TCPClientSocket.sendall(str.encode("EOF"))
    #Recibir respuesta del servidor
    #data = TCPClientSocket.recv(buffer_size)
    #if data.decode('utf-8') == "EOF":
    #    print("Fin.")
    print("Terminé")
