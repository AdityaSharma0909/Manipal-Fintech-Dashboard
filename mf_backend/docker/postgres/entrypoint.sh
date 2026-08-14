#!/bin/bash

# Export all environment variables to a file
printenv | grep -v "no_proxy" >> /etc/environment

echo "Backup entrypoint in $APP_ENV environment"

# Start the cron service
service cron start

# Log cron status
service cron status >> /var/log/cron.log 2>&1


# Start PostgreSQL
# docker-entrypoint.sh postgres
exec docker-entrypoint.sh postgres
