# Single-VM deployment

Run all services with Docker Compose on a Linux VM (including an Oracle A1 ARM64
VM). Next.js remains a standalone server; static export is not required.

## Prepare the VM

1. Install Docker Engine and the Docker Compose v2 plugin or newer. Enable Docker
   at boot. Use a supported Linux image and install OS security updates regularly.
2. Copy/clone the repository, including `frontend/`, `backend/`, `Caddyfile`, and
   `docker-compose.yml`, into a stable directory such as `/srv/symcomp`. Builds
   need outbound access to image/package registries and Google Fonts.
3. Point the domain's DNS A record to the VM's reserved public IP. Only add an AAAA
   record if IPv6 is configured. Ask the `ime.usp.br` DNS administrator to make
   these changes for `symcomp.ime.usp.br`.
4. Allow inbound TCP 80/443 in both Oracle's security rules and the VM firewall.
   Restrict SSH to administrators. Do not publish 3000, 8000, or 5432.
5. Copy `.env.example` to `.env`, restrict its permissions (`chmod 600 .env`), and
   fill in the domain, database credentials, and signing key. Generate the password
   and signing key separately with `openssl rand -hex 32`. Use a URL-safe hex
   database password because Compose embeds it in `DATABASE_URL`. Do not commit
   `.env`. Production mode and the HTTPS token issuer are set by Compose.
6. Check that `COMPOSE_SUBNET` does not overlap existing Docker/VPN networks. Only
   forwarded headers from that private subnet are trusted by FastAPI. This network
   is for trusted application containers; do not attach unrelated containers.

Keep the directory/project name stable: Compose names persistent volumes from it.
If migrating an existing deployment, preserve its project name or explicitly
restore its database. Do not change the PostgreSQL major version without a planned
upgrade. Changing POSTGRES_PASSWORD does not change a password in an existing DB.

## Start and verify

```bash
docker compose config --quiet
docker compose up -d --build --wait
docker compose ps
curl -I http://symcomp.ime.usp.br/
curl -I https://symcomp.ime.usp.br/
curl --fail https://symcomp.ime.usp.br/api/v1/health
```

HTTP redirects to HTTPS. The HTTPS homepage temporarily redirects to `/semana`;
other frontend routes are preserved. Caddy forwards `/api/*` unchanged to FastAPI,
and other requests to Next.js. Certificates renew automatically, with state in
`caddy_data` and `caddy_config`. PostgreSQL uses `postgres_data`.

The backend runs `alembic upgrade head` before starting. Health checks gate initial
proxy startup; they do not automatically restart an unhealthy but running process.
The API health endpoint checks liveness, not database readiness. All services have
restart policies and bounded Docker logs.

The browser and API share one HTTPS origin. Refresh cookies remain Secure and
HttpOnly; no cross-origin CORS configuration is needed. The frontend auth UI is
still a placeholder, so complete its implementation before expecting login pages.
The Next.js API rewrite remains available for local development; production API
traffic goes directly from Caddy to FastAPI.

On A1, build images natively on the ARM64 VM or supply ARM64 images from CI; do not
copy an AMD64-only image from a workstation. Check image optimization and backend
login/refresh behavior on the actual target before launch.

## Backups and restore

Create daily PostgreSQL custom-format dumps outside the repository:

```bash
BACKUP_DIR=/srv/backups/symcomp sh /srv/symcomp/scripts/backup-db.sh
```

Example crontab for a user with Docker access (adjust paths):

```cron
0 3 * * * BACKUP_DIR=/srv/backups/symcomp /bin/sh /srv/symcomp/scripts/backup-db.sh >> /srv/backups/symcomp-backup.log 2>&1
```

Create `/srv/backups` with permissions for that user first. Monitor failures and
storage usage. Dumps contain private data: restrict access. Copy completed `.dump`
files daily to the NAS or other off-VM storage using your backup system. Local
dumps and Docker volumes alone do not protect against VM loss. Configure retention
there (for example, 7 daily and 4 weekly backups); the script never deletes dumps.
Back up `.env` separately in secure storage and retain Caddy volumes.

Test recovery into a new database, using a disposable environment when possible:

```bash
docker compose exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" symcomp_restore_check'
docker compose exec -T postgres sh -c 'pg_restore -U "$POSTGRES_USER" -d symcomp_restore_check --no-owner --exit-on-error' < /path/to/backup.dump
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d symcomp_restore_check -c "SELECT version_num FROM alembic_version;"'
```

For actual recovery, stop the backend and proxy, restore into a fresh database,
point POSTGRES_DB at that database, and restart the stack. Verify application data
and authentication before reopening traffic. Never use `docker compose down -v`
on production: it deletes database and certificate volumes.

## Updates

Take an off-VM database backup before updating. Review migrations, pull the desired
release, then rebuild and start with `docker compose up -d --build --wait`.
`docker compose pull` updates registry images; rebuilding refreshes application
images. Avoid concurrent deployments. Image rollback does not undo a database
migration; retain a compatible database backup. A single VM has downtime during
host failures and some updates.

## Development

Use `docker compose -f docker-compose.dev.yml up --build`. This is a standalone
file, not a production overlay, and uses the `symcomp-dev` project. Services bind
to loopback only. Do not override its project name to match production.
