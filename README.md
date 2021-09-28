# 2048 Bot


The creation of this bot is inspired by [@MasterGroosha](https://github.com/MasterGroosha) [telegram-bombsweeper-bot](https://github.com/MasterGroosha/telegram-bombsweeper-bot)

Used technologies
Python;
aiogram v3 (Telegram Bot framework);
Docker and Docker Compose (containerization);
PostgreSQL (database);
Redis (persistent storage for some ongoing game data);
SQLAlchemy (working with database from Python);
Alembic (database migrations made easy);

## Installation
Make 3 directories for bot's data:

`mkdir -p {pg-data,redis-data,redis-config}`

Put `redis.conf` file into `redis-config` directory. Change its values for your preference.

Grab `.env-example` file, rename it to `.env`, open and fill the necessary data.

Finally, start your bot with `docker-compose up -d` command.
