build-verbose:
	docker compose -f compose.local.yml build --no-cache  --progress plain

build-no-cache:
	docker compose -f compose.local.yml build --no-cache

build:
	docker compose -f compose.local.yml up --build -d --remove-orphans
logs:
	docker compose -f compose.local.yml logs -f

up:
	docker compose -f compose.local.yml up -d

down:
	docker compose -f compose.local.yml down

down-v:
	docker compose -f compose.local.yml down -v

show-logs:
	docker compose -f compose.local.yml up logs

show-logs-api:
	docker compose -f compose.local.yml up logs api

db-volume:
	docker volume inspect api_estate_prod_postgres_data

mailpit-volume:
	docker volume inspect api_estate_prod_mailpit_data

estate-db:
	docker compose -f compose.local.yml exec postgres psql --username=postgres --dbname=estate

#  make ARGS="message_text" alembic-auto
alembic-auto:
	docker compose -f compose.local.yml exec web alembic revision --autogenerate -m "$(ARGS)"  

alembic-up:
	docker compose -f compose.local.yml exec web alembic upgrade head