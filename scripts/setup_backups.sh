#!/bin/bash

# Configuration
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/backup_db.sh"
CRON_JOB="0 2 * * * /bin/bash ${SCRIPT_PATH} >> /var/log/applivo_backup.log 2>&1"

echo "Setting up automated backups..."

# Make backup script executable
chmod +x "${SCRIPT_PATH}"
echo "Set executable permissions on ${SCRIPT_PATH}"

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -F "${SCRIPT_PATH}") > /dev/null
if [ $? -eq 0 ]; then
    echo "Cron job already exists. Skipping installation."
else
    # Append cron job to current crontab
    (crontab -l 2>/dev/null; echo "${CRON_JOB}") | crontab -
    echo "Added daily backup cron job (02:00 AM)"
fi

echo "Setup complete! Backups will be stored in /opt/backups/applivo"
