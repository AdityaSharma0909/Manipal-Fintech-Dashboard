#!/bin/bash

PG_PASSWORD=radian1234
PG_USER=radian
PG_DATABASE=radian
# Define the backup directory and file name
BACKUP_DIR="./db_backup"
BACKUP_FILE="backup.sql"

# Run the PostgreSQL backup command within the Docker container
sudo docker exec -t radian_db pg_dumpall -c -U radian > "$BACKUP_DIR/$BACKUP_FILE"

# Check if the backup was successful
if [ $? -eq 0 ]; then
    echo "Database backup successful."
else
    echo "Database backup failed."
    exit 1
fi

# Use curl or any HTTP client to send the backup file to your Django API
API_URL="https://dev-api.radianfinserv.com/core/upload-file"

curl -X POST -F "file=@$BACKUP_DIR/$BACKUP_FILE" "$API_URL"

# Clean up old backups if needed
# ...

# Exit
exit 0
