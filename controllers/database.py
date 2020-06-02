import psycopg2
from psycopg2.errors import UniqueViolation
from os import environ

DB_CONFIG = {
    'host': environ.get('DB_HOST', 'localhost'),
    'port': int(environ.get('DB_PORT', 5432)),
    'user': environ.get('DB_USER', 'motor'),
    'password': environ.get('DB_PASSWORD', 'energy'),
    'dbname': environ.get('DB_DATABASE', 'motor')
}

DB = psycopg2.connect(**DB_CONFIG)

if __name__ == "__main__":
    cur = DB.cursor()
    cur.execute('SELECT version(), \'Welcome to Motor energy\'')

    print(cur.query.decode() + '\n')
    print('{}\n{}'.format(*cur.fetchone()))

    cur.close()