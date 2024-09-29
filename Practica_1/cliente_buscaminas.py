import socket

buffer_size = 1024
def imprimir_tablero(tablero, filas, columnas):
    print("   " + " ".join([str(i) for i in range(columnas)]))
    for idx, fila in enumerate(tablero):
        print(f"{idx:2} " + " ".join(fila))

def iniciar_cliente(ip_servidor, puerto_servidor):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip_servidor, puerto_servidor))
    print(f"Conectado al servidor {ip_servidor}:{puerto_servidor}")

    try:
        while True:
            # Seleccionar dificultad
            print("Dificultades disponibles.")
            print("1. Principiante (9x9, 10 minas)")
            print("2. Avanzado (16x16, 40 minas)")
            dificultad = int(input("Seleccione la dificultad (1 o 2): ")) 

            #Inicializar tablero local
            if dificultad == 1:
                filas, columnas,minas = 9, 9, 10
                break
            elif dificultad == 2:
                filas, columnas,minas = 16, 16, 40
                break
            else:
                print("Dificultad no válida. Intente de nuevo.")

        
        cliente.send(str(dificultad).encode())

        # Recibir confirmación
        data = cliente.recv(buffer_size).decode()
        if data == "Juego iniciado.":
            print(data)
            
            tablero_local = [['-' for _ in range(columnas)] for _ in range(filas)]
            imprimir_tablero(tablero_local, filas, columnas)
        else:
            print("Error al iniciar el juego.")
            cliente.close() 
            return
        print("------------------------------")
        # Bucle del juego
        while True:
            # Ingresar coordenadas
            try:
                x = int(input("Ingrese la coordenada X: "))
                y = int(input("Ingrese la coordenada Y: "))
            except ValueError:
                print("Coordenadas inválidas. Deben ser números enteros.")
                continue

            mensaje_coordenadas = f"{x},{y}"
            cliente.send(mensaje_coordenadas.encode())

            # Recibir respuesta del servidor
            data = cliente.recv(1024).decode()

            if data == "Coordenadas fuera de rango.":
                print(data)
            elif data == "mina pisada":
                print(data)
                # Recibir todas las minas
                for i in range(minas):
                        mina = cliente.recv(buffer_size).decode()
                        #Confirmar recepción de mina
                        cierre = cliente.send("R".encode())
                        #print(f"Mina en: {mina}")
                        mina_x, mina_y = mina.split(",")
                        tablero_local[int(mina_x)][int(mina_y)] = 'M'
                #Enviar confirmación de recepción de minas
                cierre = cliente.send("R".encode())
                #Recibir duración del juego
                data = cliente.recv(buffer_size).decode()
                imprimir_tablero(tablero_local, filas, columnas)
                print(f"¡Has pisado una mina! Duración del juego: {data}.")
                break

            elif data == "Casilla libre.":
                print(data)    
                tablero_local[x][y] = 'O'  # O para casilla libre
                imprimir_tablero(tablero_local, filas, columnas)
                #Verificar si se ha ganado
                respuesta = cliente.recv(buffer_size).decode()
                #print(respuesta)
                if respuesta.__contains__("ganaste"):
                    print("¡Felicidades! Has ganado la partida.")
                    print(f"Duración del juego: {respuesta.split(",")[1]} segundos.")
                    imprimir_tablero(tablero_local, filas, columnas)
                    cierre = cliente.send("".encode())
                    break
            else:
                print("Respuesta no reconocida del servidor.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cliente.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    ip_servidor = input("Ingrese la IP del servidor: ")
    puerto_servidor = int(input("Ingrese el puerto del servidor: "))
    iniciar_cliente(ip_servidor, puerto_servidor)
