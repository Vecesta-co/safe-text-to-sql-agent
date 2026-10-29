import sqlite3
import os
from contextlib import contextmanager
from typing import Generator

def create_sample_chinook_db(db_path: str):
    """Create realistic Chinook-style music store database in SQLite."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE artists (
        artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );

    CREATE TABLE albums (
        album_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist_id INTEGER NOT NULL,
        FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
    );

    CREATE TABLE tracks (
        track_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        album_id INTEGER NOT NULL,
        genre TEXT NOT NULL,
        unit_price REAL NOT NULL,
        milliseconds INTEGER NOT NULL,
        FOREIGN KEY (album_id) REFERENCES albums (album_id)
    );

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        country TEXT NOT NULL,
        total_spent REAL DEFAULT 0.0
    );

    CREATE TABLE invoices (
        invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        invoice_date TEXT NOT NULL,
        billing_country TEXT NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    );

    CREATE TABLE invoice_items (
        invoice_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        track_id INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id),
        FOREIGN KEY (track_id) REFERENCES tracks (track_id)
    );

    -- Seed Artists
    INSERT INTO artists (name) VALUES 
    ('AC/DC'), ('Accept'), ('Aerosmith'), ('Miles Davis'), 
    ('Led Zeppelin'), ('Daft Punk'), ('Queen'), ('Pink Floyd');

    -- Seed Albums
    INSERT INTO albums (title, artist_id) VALUES 
    ('Back in Black', 1), ('Highway to Hell', 1), ('Balls to the Wall', 2),
    ('Get a Grip', 3), ('Kind of Blue', 4), ('Led Zeppelin IV', 5),
    ('Discovery', 6), ('A Night at the Opera', 7), ('The Dark Side of the Moon', 8);

    -- Seed Tracks
    INSERT INTO tracks (name, album_id, genre, unit_price, milliseconds) VALUES 
    ('Hells Bells', 1, 'Rock', 0.99, 312000),
    ('Back in Black', 1, 'Rock', 0.99, 255000),
    ('Shoot to Thrill', 1, 'Rock', 0.99, 317000),
    ('Highway to Hell', 2, 'Rock', 0.99, 208000),
    ('Balls to the Wall', 3, 'Metal', 0.99, 342000),
    ('Livin on the Edge', 4, 'Rock', 0.99, 381000),
    ('So What', 5, 'Jazz', 1.29, 562000),
    ('Blue in Green', 5, 'Jazz', 1.29, 337000),
    ('Stairway to Heaven', 6, 'Rock', 1.49, 482000),
    ('Black Dog', 6, 'Rock', 0.99, 296000),
    ('One More Time', 7, 'Electronic', 1.29, 320000),
    ('Harder, Better, Faster, Stronger', 7, 'Electronic', 1.29, 224000),
    ('Bohemian Rhapsody', 8, 'Rock', 1.49, 354000),
    ('Time', 9, 'Rock', 1.29, 421000),
    ('Money', 9, 'Rock', 1.29, 382000);

    -- Seed Customers
    INSERT INTO customers (first_name, last_name, email, country, total_spent) VALUES 
    ('Alex', 'Mercer', 'alex@example.com', 'USA', 45.50),
    ('Beatriz', 'Silva', 'beatriz@example.com', 'Brazil', 38.20),
    ('Carlos', 'Santana', 'carlos@example.com', 'Spain', 52.10),
    ('Diana', 'Prince', 'diana@example.com', 'Canada', 89.00),
    ('Edward', 'Norton', 'edward@example.com', 'UK', 24.50),
    ('Fiona', 'Gallagher', 'fiona@example.com', 'USA', 112.40);

    -- Seed Invoices
    INSERT INTO invoices (customer_id, invoice_date, billing_country, total) VALUES 
    (1, '2026-01-15', 'USA', 9.90),
    (2, '2026-01-20', 'Brazil', 14.85),
    (3, '2026-02-05', 'Spain', 19.80),
    (4, '2026-02-14', 'Canada', 32.50),
    (5, '2026-03-01', 'UK', 7.92),
    (6, '2026-03-12', 'USA', 42.10);

    -- Seed Invoice Items
    INSERT INTO invoice_items (invoice_id, track_id, unit_price, quantity) VALUES 
    (1, 1, 0.99, 10),
    (2, 7, 1.29, 10),
    (3, 9, 1.49, 12),
    (4, 11, 1.29, 25),
    (5, 5, 0.99, 8),
    (6, 13, 1.49, 28);
    """)

    conn.commit()
    conn.close()

@contextmanager
def get_readonly_connection(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    """Provide a strictly read-only SQLite connection context."""
    # URI read-only connection
    abs_path = os.path.abspath(db_path).replace("\\", "/")
    uri = f"file:{abs_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        yield conn
    finally:
        conn.close()

