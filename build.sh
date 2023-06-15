set -o errexit

poetry install
python manage.py collectstatic --no-input
python manage.py migrate
# Run createsuperuser command
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        password='complexpassword123',
        email='admin@example.com'
    )
EOF
