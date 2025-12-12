import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "knowledge.db"

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

    ######################################################
    ### Triggers to keep FTS in sync with chunks table ###
    ######################################################
    cursor.execute("DROP TRIGGER IF EXISTS chunks_ai;")
    cursor.execute("DROP TRIGGER IF EXISTS chunks_ad;")
    cursor.execute("DROP TRIGGER IF EXISTS chunks_au;")

    cursor.execute("""
    CREATE TRIGGER chunks_ai AFTER INSERT ON chunks BEGIN
        INSERT INTO chunks_fts(rowid, chunk_id, text)
        VALUES (new.rowid, new.chunk_id, new.text);
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER chunks_ad AFTER DELETE ON chunks BEGIN
        INSERT INTO chunks_fts(chunks_fts, rowid, chunk_id, text)
        VALUES ('delete', old.rowid, old.chunk_id, old.text);
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER chunks_au AFTER UPDATE ON chunks BEGIN
        INSERT INTO chunks_fts(chunks_fts, rowid, chunk_id, text)
        VALUES ('delete', old.rowid, old.chunk_id, old.text);

        INSERT INTO chunks_fts(rowid, chunk_id, text)
        VALUES (new.rowid, new.chunk_id, new.text);
    END;
    """)

    conn.commit() # validate all SQL commands
    conn.close()  # close the connection
