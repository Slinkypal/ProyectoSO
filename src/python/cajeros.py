import sys
import time
import random
import threading
from datetime import datetime
from config import H, K, ETIQUETA, obtener_conexion

sin_semaforo = "--sin-semaforo" in sys.argv
k_actual = K
for arg in sys.argv:
    if arg.startswith("--k="):
        k_actual = int(arg.split("=")[1])

semaforo = threading.Semaphore(k_actual)

def imprimir_comprobante():
    time.sleep(random.uniform(4.0, 4.5))

def reiniciar_datos():
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("DELETE FROM atencion")
    con.close()

def persona_cajero(num_persona):
    nombre = f"persona{num_persona}"
    for visita in range(1, 4):
        if not sin_semaforo:
            semaforo.acquire()
        try:
            print(f"{ETIQUETA} {nombre} entra al cajero (visita {visita})")
            inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            con = obtener_conexion()
            imprimir_comprobante()
            fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            with con.cursor() as cur:
                cur.execute(
                    "INSERT INTO atencion (persona, inicio, fin) VALUES (%s, %s, %s)",
                    (nombre, inicio, fin)
                )
            con.close()
            print(f"{ETIQUETA} {nombre} sale del cajero")
        finally:
            if not sin_semaforo:
                semaforo.release()
        time.sleep(random.uniform(0.05, 0.15))

if __name__ == "__main__":
    modo = "SIN SEMAFORO (ilimitado)" if sin_semaforo else f"CON SEMAFORO (K={k_actual} cajeros)"
    print(f"{ETIQUETA} Etapa 2 ({modo}) | H={H} personas, 3 visitas c/u")
    reiniciar_datos()
    hilos = []
    for i in range(1, H + 1):
        t = threading.Thread(target=persona_cajero, args=(i,))
        hilos.append(t)
        t.start()
    for t in hilos:
        t.join()
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM atencion")
        total = cur.fetchone()[0]
    con.close()
    print(f"{ETIQUETA} Proceso finalizado. Registros en atencion: {total} (esperados: {H * 3})")
