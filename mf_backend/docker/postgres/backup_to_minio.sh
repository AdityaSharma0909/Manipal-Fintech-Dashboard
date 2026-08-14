#!/bin/bash

# Use the APP_ENV environment variable
echo "Running backup in $APP_ENV environment"

# Variables
DATABASE_NAME="radian"
MINIO_BUCKET_NAME="manipal-dev"
MINIO_ACCESS_KEY="4NUE88K5WYDMGK1Z9I21"
MINIO_SECRET_KEY="4SQXWJDD62GJZA6YA24I9QHEDRLWYXJKUXWHZOHB"
MINIO_SERVER_URL="https://mum-objectstore.e2enetworks.net"
TIMESTAMP=$(date +"%Y_%m_%d_%H:%M:%S")

# APP_ENV="${APP_ENV:-PROD}"
# BACKUP_FILE="/backup_${DATABASE_NAME}_${TIMESTAMP}.sql"


if [ "$APP_ENV" == "" ]; then
  echo "APP_ENV not found."
  exit 1
elif [ "$APP_ENV" == "DEV" ]; then
  MINIO_BUCKET_NAME="manipal-dev"

elif [ "$APP_ENV" == "PROD" ]; then
  MINIO_BUCKET_NAME="manipal-prod"

else
  echo "APP_ENV is invalid."
  exit 1
fi

LOG_FILE="/var/log/backup_to_minio.log"
BACKUP_FILE="/${APP_ENV}_backup_${DATABASE_NAME}_${TIMESTAMP}.sql"



# Perform the backup
PGPASSWORD="radian1234" pg_dump -U radian -d ${DATABASE_NAME} > ${BACKUP_FILE} 2>> ${LOG_FILE}
# PGPASSWORD="radian1234" pg_dump -U radian -d radian > test2.sql

echo "Taking backup to $MINIO_BUCKET_NAME"

# Configure MinIO client
/usr/local/bin/mc alias set minio ${MINIO_SERVER_URL} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY} >> ${LOG_FILE} 2>&1
# mc alias set minio https://mum-objectstore.e2enetworks.net 4NUE88K5WYDMGK1Z9I21 4SQXWJDD62GJZA6YA24I9QHEDRLWYXJKUXWHZOHB
echo "connected to minio"

# Upload the backup to MinIO
/usr/local/bin/mc cp ${BACKUP_FILE} minio/${MINIO_BUCKET_NAME}/db_backups/ >> ${LOG_FILE} 2>&1
# mc cp test.sql minio/radian-dev/db_backups/
echo "uploaded to minio"

# Remove the local backup file
rm ${BACKUP_FILE} >> ${LOG_FILE} 2>&1
