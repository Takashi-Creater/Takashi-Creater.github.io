import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import time

# 画像保存ディレクトリを作成
images_dir = Path('images')
images_dir.mkdir(exist_ok=True)

# スポットデータを読み込む
with open('spots.json', 'r', encoding='utf-8') as f:
    spots = json.load(f)

# 各スポットの検索キーワード
search_keywords = {
    1: '富士山',
    2: 'タージマハル',
    3: 'グレートバリアリーフ サンゴ礁',
    4: 'パリ エッフェル塔',
    5: 'イグアスの滝',
    6: 'エジプト ピラミッド',
    7: 'バンコク 寺院',
    8: 'マチュピチュ',
    9: 'ハワイ ビーチ',
    10: 'キューバ カラフル 街'
}

def download_image_from_google(keyword, output_path):
    """Google画像検索から画像をダウンロード"""
    try:
        # Google画像検索のURL
        search_url = f"https://www.google.com/search?q={keyword}&tbm=isch"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 画像URLを抽出
        img_tags = soup.find_all('img')
        
        for img in img_tags[1:]:  # 最初の画像（Googleロゴ）をスキップ
            img_url = img.get('src') or img.get('data-src')
            
            if img_url and img_url.startswith('http'):
                try:
                    # 画像をダウンロード
                    img_response = requests.get(img_url, headers=headers, timeout=10)
                    
                    if img_response.status_code == 200 and len(img_response.content) > 5000:  # 5KB以上
                        with open(output_path, 'wb') as f:
                            f.write(img_response.content)
                        return True
                except:
                    continue
        
        return False
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

print("Google画像検索から観光スポット画像をダウンロード中...\n")

for spot in spots:
    spot_id = spot['id']
    keyword = search_keywords.get(spot_id, spot['title'])
    output_path = images_dir / f"spot_{spot_id}.jpg"
    
    print(f"{spot['title']} を検索中...", end=' ')
    
    if download_image_from_google(keyword, output_path):
        spot['image'] = f"images/spot_{spot_id}.jpg"
        print("✓ ダウンロード完了")
    else:
        print("✗ 失敗（既存の画像を使用）")
    
    # サーバーに負荷をかけないように待機
    time.sleep(1)

# 更新されたspots.jsonを保存
with open('spots.json', 'w', encoding='utf-8') as f:
    json.dump(spots, f, ensure_ascii=False, indent=2)

print("\n完了！")
