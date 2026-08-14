# Radian Backend Code

## Start Django Project Commands:
```bash
python3 -m django --version
django-admin startproject radian_backend
cd radian_backend
python3 manage.py startapp order
```

## Database Setup Commands:
```bash
CREATE DATABASE radian;
CREATE USER radian WITH PASSWORD 'radian1234';
ALTER ROLE radian SET client_encoding TO 'utf8';
ALTER ROLE radian SET default_transaction_isolation TO 'read committed';
ALTER ROLE radian SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE radian TO radian;
```

## Create Python Virtual Env:
```bash
sudo apt-get install python3-pip
sudo pip3 install virtualenv 
virtualenv -p python3 env
source env/bin/activate
```

## Initial Setup to start server:
```bash
mkdir radian_backend/logs
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py collectstatic
```

## Creating docker image

Build docker image with tag 'development':
```bash
sudo docker build -t radian_app:development -f docker/dockerfile .
```

Start all containers including essential services(PostgreSQL): 
```bash  
sudo docker-compose -f docker/docker-compose.yml up -d
sudo docker compose -f docker/docker-compose.yml up -d
sudo docker compose -f docker/docker-compose-dev.yml up -d
```

Other Docker Commands:
```bash
docker images
docker ps -a
sudo docker stop radian_app radian_db
sudo docker rm radian_app radian_db
sudo docker rmi radian_app:development
```

Export Docker Image:
```bash
docker save --output radian_app.tar radian_app
docker load --input radian_app.tar
```


Pull ElasticSearch Docker image
```bash

# sudo docker run --network qarc_network --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "ES_JAVA_OPTS=-Xms128m -Xmx128m" -v $(pwd)/esdata:/data -d docker.elastic.co/elasticsearch/elasticsearch:8.3.0

sudo docker run --network qarc_network --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -v /home/ubuntu/elasticsearch/esdata:/data -d docker.elastic.co/elasticsearch/elasticsearch:7.15.1

sudo docker logs elasticsearch -f

sudo docker exec -it elasticsearch bash
```


# Python Linter
```bash
pip3 install pylint
```

To enable linters, open the Command Palette (Ctrl+Shift+P) and select the Python: Select Linter command. The Select Linter command adds "python.linting.<linter>Enabled": true to your settings, where <linter> is the name of the chosen linter. 


# Python Formatter

Install Black in your virtual environment:
```bash
pip3 install black
```

Open your VSCode settings, by going 'Code -> Preferences -> Settings'.
Search for "python formatting provider" and select "black" from the dropdown menu.
In the settings, search for "format on save" and enable the "Editor: Format on Save" option.



sudo docker-compose -f docker/docker-compose-dev.yml up -d


makemigration error command 
python manage.py makemigrations application account lead users document disbursements loan product asset branch

sudo docker exec -it radian_app bash


## Restoring DB inside container
sudo docker exec -it radian_db psql -h radian_db -U radian -d radian
sudo docker exec -it radian_db psql -h radian_db -d radian -U radian -f /var/lib/postgresql/data/radian_db_13_06_2024_1920_dev.sql

Enter password: radian1234



## Taking backup of database in docker container

```bash
sudo docker exec -it radian_db sh
su postgres
cd /var/lib/postgresql/data/
pg_dump -U radian -W -d radian > radian_db_10_07_2024_0152_uat.sql
```
pg_dump -U admin -W -d doculens > doculens_backup.sql

Enter password: radian1234

Locate *.sql file from below given path and do scp:
```bash
sudo ls /var/lib/docker/volumes/radian_data/_data/radian_db_10_07_2024_0152_uat.sql
```

Copy above file to home:
```bash
sudo cp /var/lib/docker/volumes/radian_data/_data/radian_db_10_07_2024_0152_uat.sql .
sudo chown 1000:1000 radian_db_10_07_2024_0152_uat.sql
sudo scp radian@uat-api.radianfinserv.com:radian_db_10_07_2024_0152_uat.sql /home/kp/workspace/postgres_backup/.
```

Restore in local with specific table:
```bash
pg_restore -U radian --data-only -d radian -t table_name radian_db_10_07_2024_0152_uat.sql

```

Restore in local with whole database:
```bash
psql -U radian -d radian -f radian_db_10_07_2024_0152_uat.sql

OR

psql -U postgres -d radian -f radian_db_10_07_2024_0152_uat.sql
```

sudo docker run --rm -p 6379:6379 --name redis-redisjson -d redislabs/rejson:latest


### Run celery
* Run celery beat to schedule the task :
```bash
celery -A radian_backend beat -l info -s celery/celerybeat-schedule
```
* Run celery worker to run tasks :

```bash
celery -A radian_backend worker -l info --pool=solo
```


find . -path "*/migrations/*.py" -not -name "__init__.py" -delete




SELECT                
    pg_terminate_backend(pid) 
FROM 
    pg_stat_activity 
WHERE 
    -- don't kill my own connection!
    pid <> pg_backend_pid()
    -- don't kill the connections to other databases
    AND datname = 'radian'
    ;




## ElasticSearch Indexing commands
sudo docker exec -it radian_app bash
python3 manage.py search_index --rebuild -f
python3 manage.py search_index --rebuild --models users -f



Start elasticsearch containers including essential services(PostgreSQL) on PROD: 
```bash  
sudo docker-compose -f docker/elastic-docker-compose.yml up -d
sudo docker compose -f docker/elastic-docker-compose.yml up -d
```

Start elasticsearch containers including essential services(PostgreSQL) on DEV: 
```bash  
sudo docker-compose -f docker/elastic-docker-compose.yml up -d
sudo docker compose -f docker/elastic-docker-compose.yml up -d
```



Checking type:
```bash
keytool -list -v -keystore radianfinserv_uat.jks | grep 'Keystore type'
```

Convert JKS to PKCS12:
```bash
keytool -importkeystore -srckeystore radianfinserv_uat.jks -destkeystore radianfinserv_uat.jks -deststoretype pkcs12
```

Passing jks file and passphrase to create pem without passphrase:
```bash
openssl pkcs12 -in radianfinserv_uat2.jks -out radianfinserv_uat.pem -nodes -password pass:radian
```

du -cha --max-depth=1 / | grep -E "M|G"



## Generating RSA 2048 bit key pairs by OpenSSL Commands:

<!-- -des3 is used for passphrase -->
<!-- openssl genrsa -des3 -out cipherpay_private_key.pem 2048 --> 

> generate a private key with the correct length
openssl genrsa -out cipherpay_private_key.pem 2048

> generate corresponding public key
openssl rsa -in cipherpay_private_key.pem -pubout -out cipherpay_public_key.pem

> optional: create a self-signed certificate
openssl req -new -x509 -key cipherpay_private_key.pem -out cert.pem -days 360

> optional: convert pem to pfx
openssl pkcs12 -export -inkey cipherpay_private_key.pem -in cert.pem -out cert.pfx


## CipherPay Callback URL: https://dev-api.radianfinserv.com/payment/upi/callback/
## WandImagemagick Issue:
vi /etc/ImageMagick-6/policy.xml 

  <policy domain="coder" rights="read|write" pattern="PDF" />


## AXIS Bank Integration work:

openssl genrsa -aes128 -out dev-api.radianfinserv.com.key 2048
openssl genrsa -aes128 -out uat-api.radianfinserv.com.key 2048

passphrase: radian1234

openssl req -new -key dev-api.radianfinserv.com.key -out dev-api.radianfinserv.com.csr
openssl req -new -key uat-api.radianfinserv.com.key -out uat-api.radianfinserv.com.csr




# Axis Bank OpenSSL commands:

openssl pkcs12 -export -out dev-api.radianfinserv.com.p12 -inkey dev-api.radianfinserv.com.key  -in RADIAN-client-certificate.crt -name radian   -certfile UATRoot_Cert.crt -certfile UATIntermediate_Cert.crt


openssl pkcs12 -in dev-api.radianfinserv.com.p12 -out client_cert.pem -clcerts -nokeys
openssl pkcs12 -in dev-api.radianfinserv.com.p12 -out client_key.pem -nocerts -nodes

openssl pkcs12 -in file.12 -out file.pem -nodes

Passwords: radian1234

## To copy certificates on the server
scp ./cipherpay_private_key.pem radian@101.53.135.26:/home/radian/radian-los-backend/keys/cipherpay
scp ./cipherpay_public_key.pem radian@101.53.135.26:/home/radian/radian-los-backend/keys/cipherpay
scp ./body_public_key.pem radian@101.53.135.26:/home/radian/radian-los-backend/keys/cipherpay
scp ./header_public_key.pem radian@101.53.135.26:/home/radian/radian-los-backend/keys/cipherpay

## To copy certificated on server to docker
sudo docker cp /home/radian/radian-los-backend/keys/cipherpay/cipherpay_private_key.pem radian_app:/app/keys/cipherpay
sudo docker cp /home/radian/radian-los-backend/keys/cipherpay/cipherpay_public_key.pem radian_app:/app/keys/cipherpay
sudo docker cp /home/radian/radian-los-backend/keys/cipherpay/body_public_key.pem radian_app:/app/keys/cipherpay
sudo docker cp /home/radian/radian-los-backend/keys/cipherpay/header_public_key.pem radian_app:/app/keys/cipherpay


## To test cipherpay program
cd radian-los-backend/
source radian-env/bin/activate

pip3 install psycopg2-binary

python3 manage.py shell
exec(open('payment/tests/qr_code_raw_test.py').read())

scp ./payment/tests/qr_code_raw_test.py radian@101.53.135.26:/home/radian/radian-los-backend/payment/tests
scp ./payment/utils/cipherkey_utils.py radian@101.53.135.26:/home/radian/radian-los-backend/payment/utils

vi /home/radian/radian-los-backend/payment/tests/qr_code_raw_test.py
vi /home/radian/radian-los-backend/payment/utils/cipherkey_utils.py

git restore ./payment/tests/qr_code_raw_test.py
git restore ./payment/utils/cipherkey_utils.py

## Creating Bitbucket Pipeline

ssh-keygen -t rsa -b 4096 -C "kartik.patel@getafixtechnologies.com"
ssh-copy-id -i ~/.ssh/kartik.patel@getafixtechnologies.com.pub radian@dev-api.radianfinserv.com



## 16 Feb 2024 Sprint deployment steps:

1. Excute Script:

```bash
python3 manage.py shell
exec(open('excel_script/asset_calculation_of_application.py').read())
```


https://nominatim.openstreetmap.org/search?postalcode=560068&format=jsonv2&country=India



## Application migration issue of pending trigger event
sudo docker exec -it radian_db psql -h radian_db -U radian -d radian
ALTER TABLE application_application DISABLE TRIGGER ALL;

ALTER TABLE application_application ENABLE TRIGGER ALL;

## After the cron job is supposed to run, you can check the log files to see what went wrong.
sudo docker exec -it custom-postgres-container /bin/bash
cat /var/log/cron.log
cat /var/log/backup_to_minio.log


Deployment Steps:
> Take pull from uat branch from phase1_dev branch to get changes done directly on UAT >  git pull origin uat
> Create PR and merge phase1_dev to uat
> Take Database Backup
> Deploy backend
> Execute Audit History Script
> Deploy CRM
> Test Audit History & Axis Leads on CRM.



DETAIL:  The database was created using collation version 2.36, but the operating system provides version 2.31.
HINT:  Rebuild all objects in this database that use the default collation and run ALTER DATABASE radian REFRESH COLLATION VERSION, or build PostgreSQL with the right library version.
PostgreSQL is available
