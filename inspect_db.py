import sqlite3
import json

db_path = r'C:\Users\abdul\.omniroute\storage.sqlite'
conn = sqlite3.connect(db_path)
c = conn.cursor()

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables count:", len(tables))

interesting = [t for t in tables if any(k in t.lower() for k in ['prov', 'cred', 'model', 'route', 'key', 'sett'])]
print("Interesting tables:", interesting)

for t in interesting:
    try:
        count = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        cols = [d[0] for d in c.execute(f"SELECT * FROM {t} LIMIT 1").description]
        print(f"\n--- {t} ({count} rows) ---")
        print("Cols:", cols)
        rows = c.execute(f"SELECT * FROM {t} LIMIT 5").fetchall()
        for r in rows:
            print("Row:", r)
    except Exception as e:
        print(f"Error reading {t}: {e}")
