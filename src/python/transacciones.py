import sys
import time
import random
import threading
from datetime import datetime
from config import K, B, N, C, ETIQUETA, obtener_conexion

b_actual = B
c_actual = C
for arg in sys.argv:
    if arg.startswith("--b="):
        b_actual = int(arg.split("=")[1])
    elif arg.startswith("--c="):
        c_actual = int(arg.split("=")[1])

cola = []
vacios = threading.Semaphore(b_actual)
llenos = threading.Semaphore(0)
mutex = threading.Lock()

contador_lock = threading.Lock()
siguiente_num = 1

def preparar_transaccion():
    time.sleep(random.uniform(0.005, 0.030))

def procesar_en_servidor():
    time.sleep(random.uniform(0.050, 0.150))

def reiniciar_datos():
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("DELETE FROM transaccion")
    con.close()

def cajero(id_cajero):
    global siguiente_num
    nombre = f"cajero{id_cajero}"
    while True:
        with contador_lock:
            if siguiente_num > N:
                break
            num_tx = siguiente_num
            siguiente_num += 1

        preparar_transaccion()

        vacios.acquire()
        mutex.acquire()
        cola.append((num_tx, nombre))
        ocupacion = len(cola)
        mutex.release()
        llenos.release()
        print(f"{ETIQUETA} {nombre} dejo tx #{num_tx} en cola (ocupacion: {ocupacion}/{b_actual})")

def trabajador(id_trab):
    nombre = f"trabajador{id_trab}"
    con = obtener_conexion()
    while True:
        llenos.acquire()
        mutex.acquire()
        item = cola.pop(0)
        en_cola_al_sacar = len(cola)
        mutex.release()
        vacios.release()

        if item is None:
            print(f"{ETIQUETA} {nombre} recibio marca de fin y termina")
            break

        num_tx, nombre_cajero = item
        procesar_en_servidor()
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        with con.cursor() as cur:
            cur.execute(
                "INSERT INTO transaccion (num, cajero, trabajador, en_cola, guardado) VALUES (%s, %s, %s, %s, %s)",
                (num_tx, nombre_cajero, nombre, en_cola_al_sacar, ahora)
            )
        print(f"{ETIQUETA} {nombre} guardo tx #{num_tx} de {nombre_cajero} (quedaron en cola: {en_cola_al_sacar})")
    con.close()

if __name__ == "__main__":
    print(f"{ETIQUETA} Etapa 3 | K={K} cajeros, B={b_actual} cola, N={N} transacciones, C={c_actual} trabajadores")
    reiniciar_datos()

    hilos_trab = []
    for i in range(1, c_actual + 1):
        t = threading.Thread(target=trabajador, args=(i,))
        hilos_trab.append(t)
        t.start()

    hilos_caj = []
    for i in range(1, K + 1):
        t = threading.Thread(target=cajero, args=(i,))
        hilos_caj.append(t)
        t.start()

    for t in hilos_caj:
        t.join()

    # Una marca de fin por cada trabajador
    for _ in range(c_actual):
        vacios.acquire()
        mutex.acquire()
        cola.append(None)
        mutex.release()
        llenos.release()

    for t in hilos_trab:
        t.join()

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("SELECT COUNT(*), MAX(en_cola) FROM transaccion")
        total, max_cola = cur.fetchone()
    con.close()
    print(f"{ETIQUETA} Finalizado. Transacciones guardadas: {total}/{N} | Maximo en_cola registrado: {max_cola}")
