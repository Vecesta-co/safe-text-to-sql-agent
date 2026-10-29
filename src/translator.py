import re
from typing import Optional
from .models import DatabaseSchema

def translate_nl_to_sql(query: str, schema: DatabaseSchema) -> str:
    """Deterministic, schema-aware rule and template translator from natural query to SQL."""
    q = query.strip().lower()

    # Pattern: Top tracks by price / duration
    if "top" in q and ("track" in q or "song" in q):
        limit_match = re.search(r"\b(\d+)\b", q)
        limit = int(limit_match.group(1)) if limit_match else 5
        if "duration" in q or "long" in q:
            return f"SELECT name, genre, milliseconds / 1000 AS duration_seconds FROM tracks ORDER BY milliseconds DESC LIMIT {limit};"
        return f"SELECT name, genre, unit_price FROM tracks ORDER BY unit_price DESC LIMIT {limit};"

    # Pattern: Sales / Revenue by country
    if "sales" in q or "revenue" in q or "spend" in q:
        if "country" in q:
            return "SELECT billing_country, ROUND(SUM(total), 2) AS total_revenue FROM invoices GROUP BY billing_country ORDER BY total_revenue DESC;"
        elif "customer" in q:
            return """SELECT c.first_name || ' ' || c.last_name AS customer_name, ROUND(SUM(i.total), 2) AS total_spent 
FROM customers c JOIN invoices i ON c.customer_id = i.customer_id 
GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 10;"""
        return "SELECT ROUND(SUM(total), 2) AS grand_total_revenue, COUNT(*) AS invoice_count FROM invoices;"

    # Pattern: Artists / Albums
    if "artist" in q:
        if "album" in q:
            return """SELECT ar.name AS artist_name, COUNT(al.album_id) AS album_count 
FROM artists ar LEFT JOIN albums al ON ar.artist_id = al.artist_id 
GROUP BY ar.artist_id ORDER BY album_count DESC;"""
        return "SELECT artist_id, name FROM artists ORDER BY name ASC;"

    # Pattern: Albums by specific artist or list albums
    if "album" in q:
        m = re.search(r"albums? (?:by|of|for) ([a-zA-Z0-9\s/]+)", q)
        if m:
            artist_name = m.group(1).strip()
            return f"SELECT a.title, ar.name AS artist_name FROM albums a JOIN artists ar ON a.artist_id = ar.artist_id WHERE ar.name LIKE '%{artist_name}%';"
        return "SELECT a.album_id, a.title, ar.name AS artist_name FROM albums a JOIN artists ar ON a.artist_id = ar.artist_id ORDER BY a.title ASC;"

    # Pattern: Customers by country / total count
    if "customer" in q:
        if "count" in q or "how many" in q or "total" in q:
            return "SELECT COUNT(*) AS total_customers FROM customers;"
        # Specific country
        for country in ["usa", "brazil", "canada", "spain", "uk", "germany", "france"]:
            if country in q:
                return f"SELECT customer_id, first_name, last_name, email, country FROM customers WHERE LOWER(country) = '{country}';"
        return "SELECT customer_id, first_name, last_name, email, country FROM customers ORDER BY last_name ASC;"

    # Pattern: Invoices / Orders
    if "invoice" in q or "order" in q:
        return "SELECT invoice_id, customer_id, invoice_date, billing_country, total FROM invoices ORDER BY invoice_date DESC;"

    # Pattern: Genre query
    if "genre" in q or "rock" in q or "metal" in q or "jazz" in q:
        for g in ["Rock", "Metal", "Jazz", "Electronic", "Classical", "Pop"]:
            if g.lower() in q:
                return f"SELECT track_id, name, genre, unit_price FROM tracks WHERE LOWER(genre) = '{g.lower()}' ORDER BY name ASC;"
        return "SELECT genre, COUNT(*) AS track_count FROM tracks GROUP BY genre ORDER BY track_count DESC;"

    # Pattern: Tracks / Songs general
    if "track" in q or "song" in q:
        return "SELECT track_id, name, genre, unit_price FROM tracks ORDER BY name ASC;"

    # Generic Fallback: Search tables in schema
    for tname in schema.tables:
        if tname.rstrip("s") in q or tname in q:
            return f"SELECT * FROM {tname} LIMIT 20;"

    # Default fallback
    return "SELECT * FROM artists LIMIT 10;"

