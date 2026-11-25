#!/bin/bash
while true; do
    clear
    echo "=========================================================="
    echo -e "\033[1;31m[G1-banco]\033[0m MONITOR DE HILOS Y CONEXIONES MYSQL"
    echo "=========================================================="
    PID_PY=$(pgrep -f "python3.*(carrera|cajeros|transacciones)\.py" | head -n 1)
    if [ -n "$PID_PY" ]; then
        HILOS_PY=$(ps -T -p "$PID_PY" --no-headers | wc -l)
        echo "Proceso Python activo (PID $PID_PY) -> Hilos (ps -T): $HILOS_PY"
    else
        echo "Proceso Python activo: Ninguno"
    fi
    PID_MYSQL=$(pgrep -x mysqld | head -n 1)
    if [ -n "$PID_MYSQL" ]; then
        HILOS_MYSQL=$(ps -T -p "$PID_MYSQL" --no-headers | wc -l)
        echo "Servicio mysqld (PID $PID_MYSQL) -> Hilos totales: $HILOS_MYSQL"
    fi
    echo "----------------------------------------------------------"
    echo "Conexiones abiertas por app_g1 en MySQL:"
    mysql -u app_g1 -p"ClaveSeguraG1_2026!" -e "SELECT ID, USER, DB, COMMAND, TIME, STATE FROM information_schema.PROCESSLIST WHERE USER='app_g1';" 2>/dev/null
    echo "=========================================================="
    sleep 1
done
