import sys
import time
import random
import threading
from datetime import datetime
from config import S, H, M, ETIQUETA, obtener_conexion

mutex = threading.Lock()
usar_mutex = "--mutex" in sys.argv

def contar_billetes():
    time.sleep(random.uniform(0, 0.005))

def reiniciar_datos():
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("DELETE FROM deposito")
        cur.execute("UPDATE cuenta SET saldo = %s WHERE id = 1", (S,))
    con.close()

def persona_deposita(num_persona):
    nombre = f"persona{num_persona}"
    con = obtener_conexion()
    for i in range(M):
        if usar_mutex:
            mutex.acquire()
        try:
            with con.cursor() as cur:
                cur.execute("SELECT saldo FROM cuenta WHERE id = 1")
                valor_leido = cur.fetchone()[0]
                contar_billetes()
                nuevo_saldo = valor_leido + 1
                cur.execute("UPDATE cuenta SET saldo = %s WHERE id = 1", (nuevo_saldo,))
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                cur.execute(
                    "INSERT INTO deposito (persona, cuenta_id, valor_leido, momento) VALUES (%s, 1, %s, %s)",
                    (nombre, valor_leido, ahora)
                )
        finally:
            if usar_mutex:
                mutex.release()
    con.close()
    print(f"{ETIQUETA} {nombre} termino sus {M} depositos")

if __name__ == "__main__":
    modo = "CON MUTEX" if usar_mutex else "SIN MUTEX"
    print(f"{ETIQUETA} Etapa 1 ({modo}) | H={H} personas, M={M} depositos, S={S}")
    reiniciar_datos()
    hilos = []
    for i in range(1, H + 1):
        t = threading.Thread(target=persona_deposita, args=(i,))
        hilos.append(t)
        t.start()
    for t in hilos:
        t.join()
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("SELECT saldo FROM cuenta WHERE id = 1")
        saldo_final = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM deposito")
        total_dep = cur.fetchone()[0]
    con.close()
    print(f"{ETIQUETA} Saldo esperado: {S + H * M} | Saldo real: {saldo_final} | Registros en deposito: {total_dep}")
