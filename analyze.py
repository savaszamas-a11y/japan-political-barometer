import feedparser
import json
import re
from google import genai

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

# Geminiに政治傾向を判定させる
prompt = f"""
以下のニュース見出しを総合的に見て、現在の政治・社会的な論調の傾向を0〜100の数値で評価してください。
0 = 極めてリベラル・左派寄り
50 = 中道・中立・拮抗
100 = 極めて保守・右派寄り

見出し一覧:
{chr(10).join(titles)}

回答は数字1つ（例: 65）のみを出力してください。
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
)

# スコアの抽出
try:
    score = int(response.text.strip())
except Exception:
    match = re.search(r"\d+", response.text)
    score = int(match.group()) if match else 50

print(f"判定スコア: {score}")

# スコアと記事一覧をまとめて保存
data = {
    "score": score,
    "articles": articles
}

with open("score.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("score.json を更新しました！")
