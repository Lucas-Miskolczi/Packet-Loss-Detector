from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
import psycopg2
from psycopg2 import sql
from app.models import Base

'''
Using psycopg2 -> Low-level lib for Postgre -> Works well with Docker
'''

def create_database_if_not_exists(): ### If the database does not exist, create it ###
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        conn.autocommit = True ### No need to do commit after every SQL command ###
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRES_DB,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Database '{POSTGRES_DB}' does not exist. Creating it...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(POSTGRES_DB)
            ))
        else:
            print(f"Database '{POSTGRES_DB}' already exists.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error checking/creating database: {e}")


create_database_if_not_exists() ### Call function ###

'''
Sessionmaker -> Factory for new Session objects
https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker
'''

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine) ### Call the ORM from models to create the tables ###
