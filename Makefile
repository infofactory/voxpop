docker-build:
	docker build -t lisbona:latest .

docker-start:
	docker-compose up --remove-orphans $(options)

docker-stop:
	docker-compose down --remove-orphans $(options)
	docker rmi lisbona:latest

docker-shell:
	docker-compose run --rm $(options) website /bin/bash

docker-migrations:
	docker-compose run --rm $(options) website python manage.py makemigrations
	docker-compose run --rm $(options) website python manage.py migrate

docker-superuser:
	docker-compose run --rm $(options) website python manage.py createsuperuser

docker-init: docker-build docker-start