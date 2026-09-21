# Ovoza Professional V17

Telegram bot for finding event teams in Tashkent.

## Local

Configure `BOT_TOKEN` and `ADMIN_IDS` in `config.py`, then run:

```bash
python3 bot.py
```

## Render

This version includes a root `render.yaml`. Connect the private GitHub repository as a Render Blueprint. Render will create a web service and a PostgreSQL database. During the initial Blueprint setup, enter:

- `BOT_TOKEN` — BotFather token
- `ADMIN_IDS` — comma-separated Telegram IDs, e.g. `123456789,987654321`

`DATABASE_URL` is connected automatically from the Render Postgres database. The service exposes `/health` for Render health checks.

The Telegram bot itself uses long polling; the HTTP server exists only for Render health checks and inbound traffic.

## Important

Render Free web services can spin down after inactivity, and Free Render Postgres databases currently expire after 30 days. For permanent production use, move the service/database to an appropriate paid plan or another persistent PostgreSQL provider.
