import time
import sys
import socket
import threading

buffer_size = 1024
juego_terminado = threading.Event()  # Variable de control para detener el envío

def imprimir_tablero(tablero, filas, columnas):
    print("   " + " ".join([str(i) for i in range(columnas)]))
    for idx, fila in enumerate(tablero):
        print(f"{idx:2} " + " ".join(fila))

def recibir_mensajes(cliente, tablero_local, filas, columnas, minas):
    while True:
        try:
            # Recibir respuesta del servidor
            data = cliente.recv(buffer_size).decode()

            if data == "mina pisada":
                print("¡Han pisado una mina!")
                for _ in range(minas):
                    mina = cliente.recv(buffer_size).decode()
                    mina_x, mina_y = map(int, mina.split(","))
                    tablero_local[mina_x][mina_y] = 'M'
                imprimir_tablero(tablero_local, filas, columnas)
                duracion = cliente.recv(buffer_size).decode()
                print(f"Duración del juego: {duracion}.")
                cliente.send("EOF".encode())
                juego_terminado.set()  # Señalar el fin del juego
                break
                
            elif data.__contains__("ganaste"):
                print("¡Felicidades! Has ganado la partida.")
                duracion = data.split(",")[1]
                print(f"Duración del juego: {duracion} segundos.")
                #imprimir_tablero(tablero_local, filas, columnas)
                juego_terminado.set()  # Señalar el fin del juego
                break
            elif data.__contains__("Casilla libre"):
                print(data)
                #Obtener la coordenada de la casilla descubierta
                x, y = map(int, cliente.recv(buffer_size).decode().split(","))
                tablero_local[x][y] = 'O'
                imprimir_tablero(tablero_local, filas, columnas)
            elif data.__contains__("Fin del juego."):
                print(data)
                duracion = cliente.recv(buffer_size).decode()
                print(f"Duración del juego: {duracion} segundos.")
                cliente.send("EOF".encode())
                juego_terminado.set()  # Señalar el fin del juego
                break
            elif data == "Casilla ya descubierta.":
                print("Casilla ya descubierta.")
            elif data == "Coordenadas fuera de rango.":
                print(data)
       
            else:
                print("Mensaje del servidor:", data)
        except Exception as e:
            print("Error al recibir mensaje:", e)
            juego_terminado.set()
            break

def enviar_mensajes(cliente):
    while not juego_terminado.is_set():  # Revisar si el juego ha terminado
        try:
            x = int(input("Ingrese la coordenada X: "))
            y = int(input("Ingrese la coordenada Y: "))
            mensaje_coordenadas = f"{x},{y}"
            cliente.send(mensaje_coordenadas.encode())
            #Esperar un segundo para evitar que el cliente envíe mensajes muy rápido
            time.sleep(1)

        except ValueError:
            #print("Coordenadas inválidas. Deben ser números enteros.")
            print("")
        except Exception as e:
            print("Error al enviar mensaje:", e)
            juego_terminado.set()  # Detener si ocurre un error en el envío
            break

def iniciar_cliente(ip_servidor, puerto_servidor):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip_servidor, puerto_servidor))
    print(f"Conectado al servidor {ip_servidor}:{puerto_servidor}")

    try:
        # Obtener dificultad del servidor
        dificultad = cliente.recv(buffer_size).decode()
        cliente.send("R".encode())  # Confirmación de recepción de dificultad

        print("Dificultad recibida del servidor.")
        filas, columnas, minas = (9, 9, 10) if dificultad == '1' else (16, 16, 40)

        # Recibir confirmación de inicio del juego
        data = cliente.recv(buffer_size).decode()
        if data == "Juego iniciado.":
            print(data)
            tablero_local = [['-' for _ in range(columnas)] for _ in range(filas)]
            imprimir_tablero(tablero_local, filas, columnas)

            # Iniciar hilos para recibir y enviar mensajes
            hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(cliente, tablero_local, filas, columnas, minas))
            hilo_envio = threading.Thread(target=enviar_mensajes, args=(cliente,))

            hilo_recepcion.start()
            hilo_envio.start()

            hilo_recepcion.join()
            hilo_envio.join()  # Asegurar que el hilo de envío también termine

        else:
            print("Error al iniciar el juego.")
    except Exception as e:
        print("Error:", e)
    finally:
        cliente.close()  # Cerrar la conexión con el servidor
        print("Conexión cerrada.")
        sys.exit(0)

if __name__ == "__main__":
    ip_servidor = input("Ingrese la IP del servidor: ")
    puerto_servidor = int(input("Ingrese el puerto del servidor: "))
    iniciar_cliente(ip_servidor, puerto_servidor)
