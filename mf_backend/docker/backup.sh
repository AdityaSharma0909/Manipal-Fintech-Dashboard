#!/bin/bash

sleep 500
mkdir -p /backup
PGPASSWORD=radian1234 pg_dump -h radian_db -U radian radian > /backup/radian_db.sql
cp /backup/radian_db.sql /host_backup/


# MinIO (S3-compatible) Upload
MINIO_ACCESS_KEY="4NUE88K5WYDMGK1Z9I21"
MINIO_SECRET_KEY="4SQXWJDD62GJZA6YA24I9QHEDRLWYXJKUXWHZOHB"
MINIO_SERVER="mum-objectstore.e2enetworks.net"
MINIO_BUCKET="curiecredit-dev"
FILE_NAME="radian_db.sql"

mc config host add myminio http://$MINIO_SERVER $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
mc cp /host_backup/$FILE_NAME myminio/$MINIO_BUCKET/$FILE_NAME