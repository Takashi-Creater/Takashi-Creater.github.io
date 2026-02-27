#!/usr/bin/env python3
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
DB = DATA / 'postal.db'

KEN_ALL = DATA / 'KEN_ALL.CSV'
JIGYOSYO = DATA / 'JIGYOSYO.CSV'


def clean(s: str) -> str:
    if s is None:
        return ''
    return s.strip().replace('　', ' ')


def normalize_town(town: str) -> str:
    t = clean(town)
    ng = ['以下に掲載がない場合', '（その他）']
    for w in ng:
        t = t.replace(w, '')
    return t.strip(' ()（）')


def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript(
        '''
        PRAGMA journal_mode=WAL;
        DROP TABLE IF EXISTS postal_master;
        CREATE TABLE postal_master (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          zip TEXT NOT NULL,
          pref_kana TEXT,
          city_kana TEXT,
          town_kana TEXT,
          pref TEXT,
          city TEXT,
          town TEXT,
          is_business INTEGER NOT NULL DEFAULT 0,
          office_name TEXT,
          address_raw TEXT,
          source TEXT NOT NULL
        );

        CREATE INDEX idx_postal_zip ON postal_master(zip);
        CREATE INDEX idx_postal_addr ON postal_master(pref, city, town);
        CREATE INDEX idx_postal_office ON postal_master(office_name);
        '''
    )
    conn.commit()


def import_ken_all(conn: sqlite3.Connection, path: Path):
    if not path.exists():
        print(f'[skip] not found: {path}')
        return 0

    n = 0
    with path.open('r', encoding='cp932', errors='replace', newline='') as f:
        reader = csv.reader(f)
        rows = []
        for r in reader:
            if len(r) < 9:
                continue
            zip_code = clean(r[2])
            pref_kana = clean(r[3])
            city_kana = clean(r[4])
            town_kana = clean(r[5])
            pref = clean(r[6])
            city = clean(r[7])
            town = normalize_town(r[8])
            addr = f'{pref}{city}{town}'
            rows.append((zip_code, pref_kana, city_kana, town_kana, pref, city, town, 0, None, addr, 'KEN_ALL'))
            n += 1

    conn.executemany(
        '''INSERT INTO postal_master
        (zip,pref_kana,city_kana,town_kana,pref,city,town,is_business,office_name,address_raw,source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
        rows,
    )
    conn.commit()
    print(f'[ok] KEN_ALL imported: {n}')
    return n


def import_jigyosyo(conn: sqlite3.Connection, path: Path):
    if not path.exists():
        print(f'[skip] not found: {path}')
        return 0

    n = 0
    with path.open('r', encoding='cp932', errors='replace', newline='') as f:
        reader = csv.reader(f)
        rows = []
        for r in reader:
            if len(r) < 8:
                continue
            office_name = clean(r[2])
            pref = clean(r[3])
            city = clean(r[4])
            town = clean(r[5])
            zip_code = clean(r[7])
            addr = f'{pref}{city}{town}'
            rows.append((zip_code, None, None, None, pref, city, town, 1, office_name, addr, 'JIGYOSYO'))
            n += 1

    conn.executemany(
        '''INSERT INTO postal_master
        (zip,pref_kana,city_kana,town_kana,pref,city,town,is_business,office_name,address_raw,source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
        rows,
    )
    conn.commit()
    print(f'[ok] JIGYOSYO imported: {n}')
    return n


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    try:
        init_db(conn)
        c1 = import_ken_all(conn, KEN_ALL)
        c2 = import_jigyosyo(conn, JIGYOSYO)
        total = conn.execute('SELECT COUNT(*) FROM postal_master').fetchone()[0]
        print(f'[done] total rows: {total} (ken_all={c1}, jigyosyo={c2})')
        print(f'[db] {DB}')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
