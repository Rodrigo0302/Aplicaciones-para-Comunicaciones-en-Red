import socket
import json

def imprimir_tablero(tablero, filas, columnas):
    print("   " + " ".join([str(i) for i in range(columnas)]))
    for idx, fila in enumerate(tablero):
        print(f"{idx:2} " + " ".join(fila))

def iniciar_cliente(ip_servidor, puerto_servidor):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip_servidor, puerto_servidor))
    print(f"Conectado al servidor {ip_servidor}:{puerto_servidor}")

    try:
        # Elegir dificultad
        dificultad = input("Elige la dificultad (principiante/avanzado): ")
        mensaje_dificultad = {"tipo": "dificultad", "dificultad": dificultad}
        cliente.send(json.dumps(mensaje_dificultad).encode())

        # Recibir confirmación
        data = cliente.recv(1024).decode()
        confirmacion = json.loads(data)
        if confirmacion.get("tipo") == "control" and confirmacion.get("resultado") == "confirmacion":
            print(confirmacion.get("mensaje"))
            # Inicializar tablero local
            if dificultad == "principiante":
                filas, columnas = 9, 9
            elif dificultad == "avanzado":
                filas, columnas = 16, 16
            else:
                print("Dificultad no válida.")
                cliente.close()
                return
            tablero_local = [['-' for _ in range(columnas)] for _ in range(filas)]
            imprimir_tablero(tablero_local, filas, columnas)
        else:
            print("Error al iniciar el juego.")
            cliente.close()
            return

        # Bucle del juego
        while True:
            # Ingresar coordenadas
            try:
                x = int(input("Ingrese la coordenada X: "))
                y = int(input("Ingrese la coordenada Y: "))
            except ValueError:
                print("Coordenadas inválidas. Deben ser números enteros.")
                continue

            mensaje_coordenadas = {"tipo": "coordenadas", "x": x, "y": y}
            cliente.send(json.dumps(mensaje_coordenadas).encode())

            # Recibir respuesta del servidor
            data = cliente.recv(1024).decode()
            respuesta = json.loads(data)

            if respuesta.get("tipo") == "control":
                resultado = respuesta.get("resultado")
                mensaje = respuesta.get("mensaje")
                print(mensaje)

                if resultado == "Ok":
                    tablero_local[x][y] = 'O'  # O para casilla libre
                    imprimir_tablero(tablero_local, filas, columnas)
                elif resultado == "mina pisada":
                    print("Has perdido. Mostrando todas las minas:")
                    # Recibir todas las minas
                    while True:
                        data_mina = cliente.recv(1024).decode()

                        if not data_mina:
                            break
                        mina = json.loads(data_mina)
                        print(mina)
                        if mina.get("tipo") == "control" and mina.get("resultado") == "mina":
                            mina_x = mina.get("x")
                            mina_y = mina.get("y")
                            tablero_local[mina_x][mina_y] = 'M'
                    imprimir_tablero(tablero_local, filas, columnas)
                    break
                elif resultado == "ganaste":
                    print("¡Felicidades! Has ganado la partida.")
                    print(f"Duración del juego: {respuesta.get('duracion')}")
                    imprimir_tablero(tablero_local, filas, columnas)
                    break
                elif resultado == "error":
                    print(f"Error: {mensaje}")
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
