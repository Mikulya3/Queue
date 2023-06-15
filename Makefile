.PHONY: runserver
runserver:
	poetry run python ./manage.py runserver

.PHONY: migrate
migrate:
	poetry run python manage.py migrate

.PHONY: makemigrations
makemigrations:
	poetry run python manage.py makemigrations

.PHONY: install
install:
	poetry install

.PHONY: superuser
superuser:
	poetry run python manage.py createsuperuser
