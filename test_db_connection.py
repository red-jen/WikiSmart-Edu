import psycopg2
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_sync_connection():
    """Test synchronous connection with psycopg2"""
    try:
        dsn = "host=127.0.0.1 port=5432 dbname=wikismart_db user=postgres password=password"
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        print("SUCCESS! Result:", result)
        cur.close()
        conn.close()
    except Exception as e:
        print("Error type:", type(e).__name__)
        print("Error:", repr(e))

if __name__ == "__main__":
    test_sync_connection()
