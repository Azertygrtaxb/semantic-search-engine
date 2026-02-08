import sqlite3
from pathlib import Path

DB_PATH = Path("./data/documents.db")

def get_connection():
    """
    Returns a SQLite3 connection to the documents database.
    The database file is created if it does not exist.
    """
    DB_PATH.parent.mkdir(exist_ok=True)   # DB_PATH.parent is the ./data/ directory
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row        # enable dictionary-like row access : row["doc_id"], row["filename"], etc.
    return conn


def init_db():
    """
    Initialize database schema:
    - documents
    - chunks
    - chunks_fts
    """

    conn = get_connection()   # get a valid SQLite3 connection
    cursor = conn.cursor()    # cursor is the object that executes SQL commands

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        category TEXT,
        created_at TEXT NOT NULL,
        metadata_json TEXT
    );
    """)

    cursor.execute(""" CREATE TABLE IF NOT EXISTS chunks (
        chunk_id TEXT PRIMARY KEY,
        doc_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        text TEXT NOT NULL,
        FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
    );
    """)

    cursor.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
    USING fts5(
        chunk_id,
        text,
        content='chunks',
        content_rowid='rowid'
    );
    """)

    conn.commit() # validate all SQL commands
    conn.close()  # close the connection
