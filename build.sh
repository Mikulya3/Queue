set -o errexit

poetry install

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py createsuperuser --username admin2 --password 123456