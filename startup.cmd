@echo off
echo === Iniciando aplicación Django en Azure ===
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput