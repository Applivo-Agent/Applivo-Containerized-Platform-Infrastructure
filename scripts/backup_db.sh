#!/bin/bash

# Configuration
BACKUP_DIR="/opt/backups/applivo"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/applivo_${TIMESTAMP}.sql.gz"
DB_USER="applivo"
DB_NAME="applivo"
DB_CONTAINER="database"

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

echo "Starting database backup for ${DB_NAME}..."

# Perform backup
# Using -T to disable pseudo-terminal allocation for cron compatibility
docker compose exec -T "${DB_CONTAINER}" pg_dump -U "${DB_USER}" "${DB_NAME}" | gzip > "${BACKUP_FILE}"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup successful: ${BACKUP_FILE}"
    
    # Clean up old backups
    echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
    find "${BACKUP_DIR}" -name "applivo_*.sql.gz" -mtime +${RETENTION_DAYS} -exec rm {} \;
    echo "Cleanup complete."
else
    echo "ERROR: Backup failed!"
    exit 1
fi
