import threading
#Flores Estopier Rodrigo
output_file = "output.txt"

num_hilos = 5
barrera = threading.Barrier(num_hilos)

eventos = [threading.Event() for _ in range(num_hilos)]

def worker(hilo_id, prev_event, current_event, barrera):

    print(f"Hilo {hilo_id} esperando en la barrera.")
    barrera.wait()
    print(f"Hilo {hilo_id} pasó la barrera.")

    # Esperar a que el evento previo esté activado
    if hilo_id >1:
        prev_event.wait()

    print(f"Hilo {hilo_id} escribiendo.")
    # Escribir en el archivo
    with open(output_file, "a") as f:
        f.write(f"Hilo {hilo_id}\n")
        print(f"Hilo {hilo_id} escribió en el archivo.")

    # Activar el evento del siguiente hilo
    current_event.set()

# Inicializar los hilos
threads = []
for i in range(num_hilos):
    prev_event = eventos[i - 1] if i > 0 else threading.Event()  # Evento previo o vacío para el primer hilo
    t = threading.Thread(target=worker, args=(i + 1, prev_event, eventos[i], barrera))
    threads.append(t)

# Activar el primer evento para iniciar la secuencia
#eventos[0].set()

# Iniciar y esperar los hilos
for t in threads:
    t.start()

for t in threads:
    t.join()

print("Todos los hilos han terminado.")
