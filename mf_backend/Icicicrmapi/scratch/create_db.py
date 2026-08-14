import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_db():
    try:
        # Connect to default 'postgres' database
        con = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='password',
            host='localhost'
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'icici_crm_dev'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute('CREATE DATABASE icici_crm_dev')
            print("Database 'icici_crm_dev' created successfully.")
        else:
            print("Database 'icici_crm_dev' already exists.")
            
        cur.close()
        con.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_db()
