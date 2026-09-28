#!/bin/sh
# Run from any directory; BACKUP_DIR must be outside the repository.
set -eu
cd "$(dirname "$0")/.."
: "${BACKUP_DIR:?Set BACKUP_DIR to a backup directory}"
umask 077
mkdir -p "$BACKUP_DIR"
backup="$BACKUP_DIR/symcomp-$(date -u +%Y%m%dT%H%M%SZ)-$$.dump"
trap 'rm -f "$backup.partial"' EXIT HUP INT TERM
docker compose exec -T postgres sh -c 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup.partial"
mv "$backup.partial" "$backup"
printf '%s\n' "$backup"
