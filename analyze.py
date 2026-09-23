import json
import feedparser
from google import genai

# 1. Geminiクライアント初期化（GEMINI_API_KEYを環境変数に設定）
client = genai.Client()

# 2. ニュースRSSの取得（例：大手ニュース等のRSS URL）
rss_url = "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
feed = feedparser.parse(rss_url)

articles = [entry.title for entry in feed.entries[:5]]
print(f"取得した記事: {articles}")

# 3. Geminiに記事全体の傾向を分析させる
prompt = f"""
以下の最新ニュース記事群から、現在の日本の世論・政治的トピックの傾向を分析してください。
0（極めてリベラル・革新）〜 50（完全な中道）〜 100（極めて保守・伝統）の整数値1点のみを出力してください。
余計な解説は一切含めず、数値のみを返してください。

記事一覧:
{chr(10).join(articles)}
"""

response = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=prompt,
)

score = int(response.text.strip())
print(f"判定スコア: {score}")

# 4. HTMLが読み込めるようにJSON出力
with open("score.json", "w", encoding="utf-8") as f:
    json.dump({"score": score}, f)

print("score.json を更新しました！")