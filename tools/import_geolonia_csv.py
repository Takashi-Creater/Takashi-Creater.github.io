#!/usr/bin/env python3
import csv
import sqlite3
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
CSV_PATH = DATA / 'geolonia_latest.csv'
DB_PATH = DATA / 'postal.db'
URL = 'https://geolonia.github.io/japanese-addresses/latest.csv'


def download_if_needed():
    DATA.mkdir(parents=True, exist_ok=True)
    if CSV_PATH.exists() and CSV_PATH.stat().st_size > 1000:
        print(f'[skip] already exists: {CSV_PATH.name} ({CSV_PATH.stat().st_size} bytes)')
        return
    print('[download] geolonia latest.csv ...')
    urllib.request.urlretrieve(URL, CSV_PATH)
    print(f'[ok] downloaded: {CSV_PATH} ({CSV_PATH.stat().st_size} bytes)')


def init_table(conn):
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS geolonia_addresses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      pref_code TEXT,
      pref TEXT,
      pref_kana TEXT,
      pref_romaji TEXT,
      city_code TEXT,
      city TEXT,
      city_kana TEXT,
      city_romaji TEXT,
      town TEXT,
      town_kana TEXT,
      town_romaji TEXT,
      koaza TEXT,
      lat REAL,
      lng REAL,
      source TEXT NOT NULL DEFAULT 'geolonia_latest_csv'
    );
    CREATE INDEX IF NOT EXISTS idx_geo_pref_city ON geolonia_addresses(pref, city);
    CREATE INDEX IF NOT EXISTS idx_geo_town ON geolonia_addresses(town);
    CREATE INDEX IF NOT EXISTS idx_geo_latlng ON geolonia_addresses(lat, lng);
    ''')
    conn.commit()


def import_csv(conn):
    # columns: 都道府県コード,都道府県名,都道府県名カナ,都道府県名ローマ字,市区町村コード,市区町村名,市区町村名カナ,市区町村名ローマ字,大字町丁目名,大字町丁目名カナ,大字町丁目名ローマ字,小字・通称名,緯度,経度
    with CSV_PATH.open('r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        rows = []
        n = 0
        for r in reader:
            if len(r) < 14:
                continue
            try:
                lat = float(r[12]) if r[12] else None
                lng = float(r[13]) if r[13] else None
            except ValueError:
                lat = None
                lng = None
            rows.append((
                r[0], r[1], r[2], r[3],
                r[4], r[5], r[6], r[7],
                r[8], r[9], r[10], r[11],
                lat, lng
            ))
            n += 1
            if len(rows) >= 5000:
                conn.executemany('''
                    INSERT INTO geolonia_addresses
                    (pref_code,pref,pref_kana,pref_romaji,city_code,city,city_kana,city_romaji,town,town_kana,town_romaji,koaza,lat,lng)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', rows)
                conn.commit()
                rows.clear()
        if rows:
            conn.executemany('''
                INSERT INTO geolonia_addresses
                (pref_code,pref,pref_kana,pref_romaji,city_code,city,city_kana,city_romaji,town,town_kana,town_romaji,koaza,lat,lng)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', rows)
            conn.commit()
    return n


def main():
    download_if_needed()
    conn = sqlite3.connect(DB_PATH)
    try:
        init_table(conn)
        conn.execute('DELETE FROM geolonia_addresses')
        conn.commit()
        n = import_csv(conn)
        total = conn.execute('SELECT COUNT(*) FROM geolonia_addresses').fetchone()[0]
        city_cnt = conn.execute('SELECT COUNT(DISTINCT pref||city) FROM geolonia_addresses').fetchone()[0]
        print(f'[ok] imported geolonia rows: {n}')
        print(f'[ok] geolonia total rows in DB: {total}')
        print(f'[ok] distinct cities: {city_cnt}')
        # quick sample
        print('[sample] 北海道 釧路市 top 5:')
        for row in conn.execute("SELECT pref,city,town,koaza,lat,lng FROM geolonia_addresses WHERE pref='北海道' AND city LIKE '釧路%' LIMIT 5"):
            print(' -', row)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
