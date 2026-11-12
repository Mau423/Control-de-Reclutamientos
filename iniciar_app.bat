@echo off
cd /d "%~dp0"

echo Iniciando entorno virtual con uv...
uv sync

echo Activando entorno virtual y ejecutando la aplicación...
uv run flask --app wsgi run --host 127.0.0.1 --port 5000 --debug

echo Abriendo navegador...
start http://127.0.0.1:5000/health
