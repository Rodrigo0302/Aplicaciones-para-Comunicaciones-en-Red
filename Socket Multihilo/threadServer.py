# !/usr/bin/env python3
#Flores Estopier Rodrigo
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
            gestion_conexiones(listaConexiones)
    except Exception as e:
        print(e)

def gestion_conexiones(listaconexioness):
    listaconexiones = list(listaconexioness)
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    #print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    #print(listaconexiones)


def recibir_datos(conn, addr,listaconexiones):
    try:
        cur_thread = threading.current_thread()
        print("Recibiendo datos del cliente {} en el {}".format(addr, cur_thread.name))
        while True:
            data = conn.recv(1024)
            response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
            if data.decode('utf-8') == "EOF":
                print("Fin.")
                break
            #conn.sendall(response)
        #Enviar confirmación de finalización
        #conn.sendall(b"EOF")
    except Exception as e:
        print(e)
    finally:
        limpiarConexion(conn, addr, listaConexiones)

def limpiarConexion(conn, addr, listaconexiones):
    print(f"Cerrando conexión con {addr}")
    try:
        conn.close()  # Cerrar la conexión de manera segura
    except Exception as e:
        print(f"Error al cerrar conexión con {addr}:", e)
    finally:
        if conn in listaconexiones:
            listaconexiones.remove(conn)  # Remover la conexión de la lista
        print(f"Conexión con {addr} cerrada correctamente.")



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
