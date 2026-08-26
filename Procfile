release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn project.wsgi --log-file -
