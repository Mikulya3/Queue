set -o errexit

poetry install

python manage.py collectstatic --no-input
python manage.py migrate

if [ ! -z "$CREATE_SUPERUSER" ]; then
  # Create superuser
  python manage.py createsuperuser --noinput \
    --username=admin \
    --email=admin@example.com
fi

# Start the server
python manage.py runserver 0.0.0.0:$PORT