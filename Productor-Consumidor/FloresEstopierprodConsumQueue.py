import threading
import logging
import time
import queue
#Productor-Consumidor con Queue
#Flores Estopier Rodrigo
#15-11-2024

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )

# Buffer compartido
buffer_size = 10
buffer = queue.Queue(buffer_size)

def productor(id, iteraciones):
    for _ in range(iteraciones):
        item = 'p'
        try:
            buffer.put(item, timeout=1)
            logging.debug(f'Productor {id} produjo {item}')
            logging.debug(f'Elementos Buffer despues de producir: {buffer.qsize()}')
        except queue.Full:
            logging.debug(f'Productor {id} se bloqueó (buffer lleno)')
        time.sleep(1)
       

def consumidor(id, iteraciones):
    for _ in range(iteraciones):
        try:
            item = buffer.get(timeout=1)
            logging.debug(f'Consumidor {id} consumió {item}')
            logging.debug(f'Elementos Buffer despues de consumir: {buffer.qsize()}')
        except queue.Empty:
            logging.debug(f'Consumidor {id} se bloqueó (buffer vacío)')
        time.sleep(1)
        

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