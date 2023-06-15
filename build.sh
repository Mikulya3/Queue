set -o errexit

poetry install

python manage.py collectstatic --no-input
python manage.py migrate

# Check if CREATE_SUPERUSER variable is set
if [ ! -z "$CREATE_SUPERUSER" ]; then
  # Create superuser
  echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'password')" | python manage.py shell
fi

# Start the server
python manage.py runserver 0.0.0.0:$PORT