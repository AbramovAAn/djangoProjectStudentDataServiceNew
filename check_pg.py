# check_pg.py
import psycopg2, sys

def try_connect(db):
    try:
        conn = psycopg2.connect(
            dbname=db, user="sds", password="sds",
            host="127.0.0.1", port=5432, connect_timeout=5
        )
        conn.close()
        print(f"OK: connected to {db} as sds")
    except psycopg2.OperationalError as e:
        print(f"FAIL to {db}: {type(e).__name__} :: {e}")

for db in ("sds", "postgres"):
    try_connect(db)
