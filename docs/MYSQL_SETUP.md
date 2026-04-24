# MySQL Setup Guide

This guide is only for the `web-assistant` authentication/database setup.

Use it together with:

1. `RUN_WINDOWS.md`
2. `web-assistant/services/auth/setup_users_db.py`

## What You Need

- MySQL Server 8.0+
- Optional: MySQL Workbench
- Valid DB credentials for your local MySQL/XAMPP instance

## Database Used

The current web-assistant auth stack uses:

- database: `nasa_ai_system`
- main table: `users`
- primary user key: `user_id`
- additional tables: `notes`, `reminders`, `agent_interactions`, `federated_updates`, `reading_activities`

## The Normal Windows Flow

From the repo root:

```powershell
python -m venv venv
venv\Scripts\python -m pip install -r requirements_web_assistant.txt
venv\Scripts\python web-assistant/services/auth/setup_users_db.py
```

If DB auth fails, set these keys manually in `.env` and `web-assistant/.env`:

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

Then rerun the schema setup command.

## Required Env Keys

These values must be valid in both env files:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=nasa_ai_system
DB_TABLE=users
```

For SQLAlchemy in `web-assistant/.env`:

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/nasa_ai_system
```

If your local XAMPP MySQL root user has no password, leave:

```env
DB_PASSWORD=
```

## Automatic Setup Script

Bootstrap calls this script:

- `web-assistant/services/auth/setup_users_db.py`

You can also run it manually:

```bash
python web-assistant/services/auth/setup_users_db.py
```

It creates:

- `users`
- `notes`
- `reminders`
- `agent_interactions`
- `federated_updates`

It also seeds two default users:

- `testuser / test123` with role `astronaut`
- `admin / admin123` with role `admin`

## Workbench Option

If you prefer MySQL Workbench:

1. Connect to your local MySQL server
2. Open:
   `web-assistant/services/auth/setup_auth_mysql.sql`
3. Execute the script

## Quick Verification

### Verify the schema exists

```bash
mysql -u root -p nasa_ai_system -e "SHOW TABLES;"
```

### Verify users exist

```bash
mysql -u root -p nasa_ai_system -e "SELECT user_id, username, role FROM users;"
```

### Verify auth server login

```bash
curl -X POST http://localhost:7000/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"testuser\",\"password\":\"test123\"}"
```

## Common Problems

### Access denied for `root@localhost`

Cause:
- wrong `DB_USER` or `DB_PASSWORD`

Fix:
- update `.env`
- update `web-assistant/.env`
- rerun bootstrap or `setup_users_db.py`

### MySQL server not running

Fix one of these:

- start XAMPP MySQL
- start your standalone MySQL service

### Python can’t import MySQL packages

Fix:

```bash
venv\Scripts\python -m pip install mysql-connector-python PyMySQL
```

## Keep This Guide Focused

This file intentionally does not try to be a full MySQL manual.

It only covers what this repository needs for the current web-assistant authentication/database flow.

