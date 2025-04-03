#!/bin/bash

# Script para iniciar pgAdmin como un servidor independiente
echo "Iniciando servidor pgAdmin en puerto 5050..."

# Asegurar que las dependencias están instaladas
pip install flask psycopg2-binary gunicorn

# Iniciar el servidor pgAdmin
gunicorn --bind 0.0.0.0:5050 --reuse-port --reload 'pgadmin:create_app()'

echo "Servidor pgAdmin detenido."