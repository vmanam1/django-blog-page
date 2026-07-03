# Django Blogging Platform

[![CI](https://github.com/vmanam1/django-blog-page/actions/workflows/ci.yml/badge.svg)](https://github.com/vmanam1/django-blog-page/actions/workflows/ci.yml)
[![Live](https://img.shields.io/badge/live-Render-46E3B7)](https://django-blog-bqma.onrender.com/)

**Live application:** [https://django-blog-bqma.onrender.com/](https://django-blog-bqma.onrender.com/)

A server-rendered blogging application built with Django. Users can register, manage a
profile, publish posts, browse posts by author, and update or delete only their own content.

I originally built this project during the third year of my B.Tech. In 2026 I modernized
the original implementation to demonstrate how I now approach security, testing, continuous
integration, dependency management, and production deployment.

## Features

- Account registration, login, POST-only logout, and password reset
- One profile and profile image per user
- Create, read, update, and delete operations for blog posts
- Object-level authorization for post updates and deletion
- Paginated home and author pages
- Case-insensitive unique email validation
- Local media storage in development and optional Amazon S3 storage in production
- Console email in development and configurable SMTP delivery in production
- PostgreSQL-ready production configuration with SQLite for local development
- Automated tests, Ruff linting, and GitHub Actions CI

Email addresses are currently validated for format and uniqueness. Account ownership
verification through an emailed activation link is not yet implemented.

## Modernization completed

The original college project was upgraded without replacing its core Django architecture:

- Removed committed credentials, the local SQLite database, uploaded user files, and Python
  bytecode from the published repository.
- Rebuilt Git history as a clean public portfolio snapshot under `vmanam1`.
- Upgraded Django 4.2 to Django 5.2 LTS and Python 3.12-compatible dependencies.
- Replaced hardcoded settings with environment variables and safe development defaults.
- Added PostgreSQL support through `DATABASE_URL`, while retaining SQLite locally.
- Upgraded Bootstrap 4 to Bootstrap 5 and made logout a CSRF-protected POST action.
- Fixed profile signal registration, duplicate-email handling, URL consistency, and production
  host/port detection.
- Added production security settings, WhiteNoise static assets, Gunicorn, and an HTTP health
  endpoint.
- Added 11 tests, Ruff linting/formatting, and GitHub Actions continuous integration.
- Added a free-tier deployment using Render for Django and Neon for PostgreSQL.
- Added optional Brevo SMTP configuration for password-reset delivery and optional Amazon S3
  storage for persistent profile images.

## Technology

- Python 3.12 and Django 5.2 LTS
- Django templates, Crispy Forms, and Bootstrap 5.3
- SQLite for development; PostgreSQL for production
- WhiteNoise for versioned static assets
- Amazon S3 through `django-storages` for optional uploaded-media storage
- Gunicorn as the production WSGI server
- Render Blueprint infrastructure configuration
- Ruff and Django's test framework

## How the application works

### Request lifecycle

1. A browser request reaches Django through the development server or Gunicorn.
2. `django_project/urls.py` routes account, admin, health-check, and blog requests.
3. Blog routes are delegated to `blog/urls.py` and handled by class-based views.
4. A view reads or writes Django models through the ORM.
5. The view renders a template with context data or redirects after a successful write.
6. Django middleware provides sessions, authentication, CSRF protection, messages, and
   security headers.

### Applications and models

`blog` owns the `Post` model and the public/content-management views. Each post belongs to
one Django `User`. Deleting a user cascades to that user's posts.

`users` owns the `Profile` model and registration/profile forms. Each profile has a one-to-one
relationship with a user. A post-save signal creates a profile whenever a user is created.

```text
User 1 ----- 1 Profile
  |
  +----- * Post
```

### Authorization

Reading posts is public. Creating a post requires authentication. Update and delete views use
both `LoginRequiredMixin` and `UserPassesTestMixin`; the latter compares the logged-in user to
the post author. CSRF tokens protect every state-changing HTML form.

### Files and email

With no S3 bucket configured, uploaded profile images are stored under `media/`. When
`AWS_STORAGE_BUCKET_NAME` is present, Django switches its default storage backend to S3.
Static CSS is independent of uploaded media: WhiteNoise collects, fingerprints, and serves it
in production.

Development password-reset emails are printed to the terminal. Configure the SMTP variables
to send real email. Never commit SMTP or cloud credentials.

## Local setup

### 1. Clone and enter the project

```bash
git clone https://github.com/vmanam1/django-blog-page.git
cd django-blog-page
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 4. Configure the environment

```powershell
Copy-Item .env.example .env
```

On macOS/Linux use `cp .env.example .env`. The defaults in the example file are suitable for
local development. Replace `DJANGO_SECRET_KEY` with a generated value:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Initialize and run

```bash
python manage.py migrate
python manage.py createsuperuser  # optional admin account
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The admin is at `/admin/` and the health check is at `/health/`.

## Environment variables

| Variable | Purpose | Development default |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Signs sessions and security tokens | Local-only unsafe key |
| `DJANGO_DEBUG` | Enables Django debugging | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated accepted host names | `localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS deployment origins | Empty |
| `DATABASE_URL` | Database connection URL | Local SQLite |
| `EMAIL_BACKEND` | Django email backend | Console backend |
| `EMAIL_HOST_USER` | SMTP username/from address | Empty |
| `EMAIL_HOST_PASSWORD` | SMTP password or app password | Empty |
| `AWS_ACCESS_KEY_ID` | S3 IAM access key | Empty |
| `AWS_SECRET_ACCESS_KEY` | S3 IAM secret | Empty |
| `AWS_STORAGE_BUCKET_NAME` | Enables S3 media storage when set | Empty/local media |
| `AWS_S3_REGION_NAME` | AWS bucket region | `eu-north-1` |

Production startup fails if debug is disabled without an explicit secret key.

## Quality checks

Run the same checks used by GitHub Actions:

```bash
ruff check .
ruff format --check .
python manage.py makemigrations --check --dry-run
python manage.py test
```

The tests cover registration, profile creation, duplicate-email rejection, authentication
requirements, post creation, post ownership permissions, deletion, and POST-only logout.

## Deployment on Render

The live deployment is available at
[django-blog-bqma.onrender.com](https://django-blog-bqma.onrender.com/).

```text
Browser -> Render free web service -> Django/Gunicorn -> Neon PostgreSQL
                         |
                         +-> WhiteNoise static files
                         +-> optional Brevo SMTP / Amazon S3
```

`render.yaml` declares a free web service that connects to an external PostgreSQL database.
`build.sh` installs dependencies, collects static assets, and applies database migrations;
Gunicorn serves Django, and Render monitors `/health/`.

1. Push the repository to GitHub.
2. In Render, create a new Blueprint and select this repository.
3. Create a free Neon PostgreSQL database and copy its connection string.
4. Review the generated Render web service and enter that connection string as the secret
   `DATABASE_URL` value. Never commit it to Git.
5. Render exposes its assigned hostname through `RENDER_EXTERNAL_HOSTNAME`; Django adds that
   hostname and its HTTPS origin to the security allowlists automatically.
6. For persistent profile images, create a private IAM user and S3 bucket, then set the three
   `AWS_*` secret variables in Render. Without S3, uploaded files on an ephemeral web-service
   filesystem will not be durable.
7. Configure SMTP variables if password-reset emails should be delivered externally.

Do not use the development SQLite database in production and do not commit `.env`.

Render's free instance can spin down while inactive, so the first request after inactivity can
take approximately a minute. Neon can also suspend idle database compute and wake it on demand.
Uploaded profile images are not durable on Render until S3 is configured.

## Screenshots

| Home | Login | Profile |
| --- | --- | --- |
| <img src="images/Screenshot%20(52).png" alt="Home page" width="250"> | <img src="images/Screenshot%20(53).png" alt="Login page" width="250"> | <img src="images/Screenshot%20(57).png" alt="Profile page" width="250"> |

These screenshots document the original version. The interface now uses Bootstrap 5, so minor
visual differences are expected.

## Repository history and security

Generated bytecode, local databases, local uploads, and environment files are excluded from
Git. If a credential is ever committed, removing it in a later commit is not sufficient:
revoke it first, then purge it from repository history before publishing rewritten history.

See `.env.example` for safe configuration placeholders.

## Possible next improvements

- Email ownership verification
- Drafts, tags, search, comments, and rich-text editing
- API endpoints and a separate frontend
- Image resizing and asynchronous background processing
- Rate limiting and social authentication
- Browser-level end-to-end tests and accessibility audits

## License

Licensed under the [MIT License](LICENSE).
