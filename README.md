# VU Sports Management

A Flask and MySQL portal connecting sports administrators, coaches and participants.

## Features

- Sport and user administration
- Coach registration and approval
- Participant registration and approval
- Coach and participant dashboards and profiles

## Technology

Python and Flask.

## Local setup

Clone the repository:

```bash
git clone https://github.com/nasirabbas827/vusports_final.git
cd vusports_final
```

Use a virtual environment:

```bash
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate
python -m pip install flask flask-mysqldb flask-mail
```

The install command lists packages used by the inspected source; this repository does not include a pinned dependency file. Saved machine learning models may require the versions used during training.

Complete the project-specific setup below, then run from the repository root:

```bash
python app.py
```

Open `http://127.0.0.1:5000/`.

## Project-specific setup

Import `Database/sports_db.sql` and configure the MySQL settings in `app.py`. Keep `static/profile_pics/` and `static/uploads/` writable for local uploads. Flask-MySQLdb may require MySQL client development libraries on your OS.

## Repository layout

| Path | Purpose |
|---|---|
| `Database/` | SQL database export |
| `app.py` | Flask application |
| `static/` | Static assets and uploads |
| `templates/` | HTML templates |

## Development notes

Setup steps describe local development. Configure your own database, mail and API credentials where applicable. Review debug settings and replace development secrets before deploying. The application was not executed as part of this documentation update.

Maintained by [Nasir Abbas](https://github.com/nasirabbas827).
