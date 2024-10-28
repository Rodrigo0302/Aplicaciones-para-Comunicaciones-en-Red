#!/usr/bin python3
#Flores Estopier Rodrigo

#Agregamos la libreria para utilizar selectores
import selectors
import socket
#Creamos un objeto selector
sel = selectors.DefaultSelector()

HOST = "localhost"  # Direccion IP del servidor
PORT = 65432  # Puerto que usa el cliente  (los puertos sin provilegios son > 1023)
buffer_size = 1024

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print("Conectado a", addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(buffer_size)  # Should be ready
    if data:
        print('Recibido', data, 'de', conn.getpeername())
        conn.send(data)  # Hope it won't block
    else:
        print('Cerrando conexion', conn.getpeername())
        sel.unregister(conn)
        conn.close()


sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(10)
print("El servidor TCP está disponible y en espera de solicitudes")
#Establecemos el socket en modo no bloqueante
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)



