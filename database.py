"""
database.py - SQL Server connection & table initialisation
Uses Windows Authentication (trusted connection) with pyodbc.
"""
import pyodbc
import streamlit as st
from config import DB_HOST, DB_NAME, DB_TRUSTED_CONNECTION


# ── Connection helper ──────────────────────────────────────────────────────────
def get_connection():
    """Return a live pyodbc connection to SQL Server Express."""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_HOST};"
        f"DATABASE={DB_NAME};"
        f"Trusted_Connection={DB_TRUSTED_CONNECTION};"
    )
    return pyodbc.connect(conn_str)


# ── One-time schema setup ──────────────────────────────────────────────────────
def initialise_database():
    """
    Create the fitness_app database (if absent) and both core tables.
    Safe to run multiple times – uses IF NOT EXISTS guards.
    """
    # First connect to master so we can create the app database if needed
    master_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_HOST};"
        f"DATABASE=master;"
        f"Trusted_Connection={DB_TRUSTED_CONNECTION};"
    )
    try:
        conn = pyodbc.connect(master_str, autocommit=True)
        cur  = conn.cursor()

        cur.execute(
            f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{DB_NAME}') "
            f"CREATE DATABASE [{DB_NAME}];"
        )
        conn.close()

        # Now connect to the app database and create tables
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
            CREATE TABLE Users (
                id            INT IDENTITY(1,1) PRIMARY KEY,
                name          NVARCHAR(100)    NOT NULL,
                email         NVARCHAR(150)    NOT NULL UNIQUE,
                password_hash NVARCHAR(256)    NOT NULL,
                age           INT,
                gender        NVARCHAR(10),
                created_at    DATETIME DEFAULT GETDATE()
            );
        """)

        cur.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Progress' AND xtype='U')
            CREATE TABLE Progress (
                id      INT IDENTITY(1,1) PRIMARY KEY,
                user_id INT NOT NULL REFERENCES Users(id),
                weight  FLOAT NOT NULL,
                date    DATE  NOT NULL DEFAULT CAST(GETDATE() AS DATE)
            );
        """)

        conn.commit()
        conn.close()
        return True, "Database initialised successfully."

    except Exception as exc:
        return False, str(exc)
