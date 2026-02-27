# 郵便番号ローカルDB運用

## 1) CSVを配置
`/Users/mini/Desktop/my-web/data/` に以下を置く:
- `KEN_ALL.CSV`
- `JIGYOSYO.CSV`

## 2) DB作成
```bash
cd /Users/mini/Desktop/my-web
python3 tools/import_postal_csv.py
```

生成物:
- `data/postal.db`

## 3) 検索テスト
```bash
# 郵便番号前方一致
python3 tools/postal_search.py 060

# 住所キーワード
python3 tools/postal_search.py 釧路
```

## 4) 次の接続
- フロントの住所入力補完は、ローカルAPI化して `postal_search.py` 相当のSQLを叩く。
- Google Mapsは地図表示とピン操作に使い、住所候補はpostal.dbから返す。
