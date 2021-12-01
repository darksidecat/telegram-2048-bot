# 2048 Bot

<a href="https://t.me/another_2048_bot"><img src="https://img.shields.io/badge/Telegram-%40another__2048__bot-blue"></a>  

The creation of this bot is inspired by [@MasterGroosha](https://github.com/MasterGroosha) [telegram-bombsweeper-bot](https://github.com/MasterGroosha/telegram-bombsweeper-bot)

### Used technologies
* Python;
* aiogram v3 (Telegram Bot framework);
* Docker and Docker Compose (containerization);
* PostgreSQL (database);
* Redis (persistent storage for some ongoing game data);
* SQLAlchemy (working with database from Python);
* Alembic (database migrations made easy);

## Installation
Make directories for bot's data:

Grab `.env-example` file, rename it to `.env`, open and fill the necessary data.

Change `redis.conf` values for your preference.

Run script
`.make_volumes.sh`
Directories wil be created in `${HOME}/${VOLUMES_DIR}` path

Finally, start your bot with `docker-compose up -d` command.
