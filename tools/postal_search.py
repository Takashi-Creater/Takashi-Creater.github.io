#!/usr/bin/env python3
import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'postal.db'


def search(q: str, limit: int = 20):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        if q.isdigit() and len(q) >= 3:
            sql = '''
            SELECT zip, pref, city, town, office_name, is_business
            FROM postal_master
            WHERE zip LIKE ?
            LIMIT ?
            '''
            rows = conn.execute(sql, (q + '%', limit)).fetchall()
        else:
            like = f'%{q}%'
            sql = '''
            SELECT zip, pref, city, town, office_name, is_business
            FROM postal_master
            WHERE (pref || city || town) LIKE ?
               OR IFNULL(office_name,'') LIKE ?
            LIMIT ?
            '''
            rows = conn.execute(sql, (like, like, limit)).fetchall()

        for r in rows:
            label = f"{r['pref']}{r['city']}{r['town']}"
            if r['is_business'] and r['office_name']:
                label = f"{label} {r['office_name']}"
            print(f"{r['zip']}\t{label}")
    finally:
        conn.close()


def main():
    p = argparse.ArgumentParser(description='Search local postal DB')
    p.add_argument('query', help='zip prefix or address keyword')
    p.add_argument('--limit', type=int, default=20)
    args = p.parse_args()

    if not DB.exists():
        print(f'DB not found: {DB}')
        print('Run: python3 tools/import_postal_csv.py')
        raise SystemExit(1)

    search(args.query, args.limit)


if __name__ == '__main__':
    main()
