import feedparser
import json
import re
import time
from google import genai
from google.genai import errors

client = genai.Client()

# 各主要メディアの政治ニュースを横断収集するRSS
rss_url = "https://news.google.com/rss/search?q=%E6%94%BF%E6%B2%BB&hl=ja&gl=JP&ceid=JP:ja"
feed = feedparser.parse(rss_url)

articles = []
# 最新の政治ニュースを6件取得
for entry in feed.entries[:6]:
    articles.append({
        "title": entry.title,
        "link": entry.link
    })

titles = [a["title"] for a in articles]
print("取得した政治記事:", titles)

prompt = f"""
以下の日本の政治ニュース見出しを総合的に見て、現在の政治・社会的な論調の傾向を0〜100の数値で客観的に評価してください。
0 = 極めてリベラル・左派寄り
50 = 中道・中立・拮抗
100 = 極めて保守・右派寄り

見出し一覧:
{chr(10).join(titles)}

回答は数字1つ（例: 58）のみを出力してください。
"""

# 503エラー対策のリトライ処理
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
            time.sleep(5)
        else:
            print("安全のためスコア50で保存します。")

# 保存
data = {
    "score": score,
    "articles": articles
}

with open("score.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("政治ニュースで score.json を更新しました！")
