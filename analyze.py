import feedparser
import json
import re
import time
from google import genai
from google.genai import errors

client = genai.Client()

# RSSから記事を取得
rss_url = "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
feed = feedparser.parse(rss_url)

articles = []
for entry in feed.entries[:5]:
    articles.append({
        "title": entry.title,
        "link": entry.link
    })

titles = [a["title"] for a in articles]
print("取得した記事:", titles)

prompt = f"""
以下のニュース見出しを総合的に見て、現在の政治・社会的な論調の傾向を0〜100の数値で評価してください。
0 = 極めてリベラル・左派寄り
50 = 中道・中立・拮抗
100 = 極めて保守・右派寄り

見出し一覧:
{chr(10).join(titles)}

回答は数字1つ（例: 65）のみを出力してください。
"""

# 503エラー対策：最大5回自動で再試行する
score = 50
max_retries = 5

for attempt in range(1, max_retries + 1):
    try:
        print(f"Gemini API呼び出し中... (試行 {attempt}/{max_retries})")
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        try:
            score = int(response.text.strip())
        except Exception:
            match = re.search(r"\d+", response.text)
            score = int(match.group()) if match else 50
        print(f"判定成功！スコア: {score}")
        break
    except errors.APIError as e:
        print(f"APIエラー発生 ({e.code}): {e.message}")
        if attempt < max_retries:
            print("サーバー混雑のため、5秒待って再試行します...")
            time.sleep(5)
        else:
            print("再試行上限に達しました。安全のためスコア50で保存します。")

# 保存
data = {
    "score": score,
    "articles": articles
}

with open("score.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("score.json を更新しました！")
