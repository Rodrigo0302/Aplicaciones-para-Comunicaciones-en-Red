import threading
import time
import random

# Buffer compartido
buffer = []
buffer_size = 10

# Condiciones
condition = threading.Condition()
no_vacio = threading.Condition(condition)
no_lleno = threading.Condition(condition)

def productor(id, iteraciones):
    for _ in range(iteraciones):
        item = random.randint(1, 100)
        with condition:
            while len(buffer) >= buffer_size:
                no_lleno.wait()
            buffer.append(item)
            print(f'Productor {id} produjo {item}')
            no_vacio.notify()
        time.sleep(random.random())

def consumidor(id, iteraciones):
    for _ in range(iteraciones):
        with condition:
            while not buffer:
                no_vacio.wait()
            item = buffer.pop(0)
            print(f'Consumidor {id} consumió {item}')
            no_lleno.notify()
        time.sleep(random.random())

def main(num_productores, num_consumidores, iteraciones):
    productores = [threading.Thread(target=productor, args=(i, iteraciones)) for i in range(num_productores)]
    consumidores = [threading.Thread(target=consumidor, args=(i, iteraciones)) for i in range(num_consumidores)]

    for p in productores:
        p.start()
    for c in consumidores:
        c.start()

    for p in productores:
        p.join()
    for c in consumidores:
        c.join()

if __name__ == "__main__":
    num_productores = int(input("Ingrese el número de productores: "))
    num_consumidores = int(input("Ingrese el número de consumidores: "))
    iteraciones = int(input("Ingrese el número de iteraciones: "))
    main(num_productores, num_consumidores, iteraciones)