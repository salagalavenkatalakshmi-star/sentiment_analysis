from flask import Flask, request, render_template_string
import pandas as pd
import os
from textblob import TextBlob

app = Flask(__name__)
os.makedirs('uploads', exist_ok=True)
app_data = {"total":0, "pos":0, "neg":0, "neu":0, "reviews_data":[], "filename":""}

HOME = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ReviewSense</title><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap" rel="stylesheet">
<style>*{font-family:'Poppins',sans-serif;margin:0;padding:0;box-sizing:border-box}body{background:linear-gradient(90deg,#ff7eb3,#7af0c0);min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:white;width:90%;max-width:800px;border-radius:30px;padding:40px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.15)}
.btn{background:linear-gradient(90deg,#ff6b9d,#00d09c);color:white;border:none;padding:14px 40px;border-radius:15px;font-size:18px;font-weight:700;cursor:pointer;margin-top:20px}
</style></head><body><div class="card"><h1 style="font-size:44px">REVIEW SENSE</h1><p style="letter-spacing:4px;color:#666">SENTIMENT ANALYSIS</p>
<div style="margin-top:30px;border:3px dashed #ff9ac1;background:#fff0f5;padding:30px;border-radius:20px">
<p>👋 Welcome to ReviewSense!</p><p style="color:#777">Upload 1000 Reviews Dataset</p>
<form method="POST" action="/upload" enctype="multipart/form-data">
<input type="file" name="file" required style="padding:12px;width:80%;border-radius:10px;border:1px solid #ddd"><br>
<button class="btn">Upload & Analyze 1000 Reviews</button></form></div></div></body></html>"""

ANALYZE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ReviewSense Analysis</title><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif}body{background:linear-gradient(90deg,#ff8ab8 0%,#a8f5d8 100%);min-height:100vh}
.header{text-align:center;padding:35px;color:white}.header h1{font-size:50px;text-shadow:2px 2px 0px #ff4d8a}
.main{background:#f7fffe;margin:0 15px 20px;border-radius:35px;padding:30px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:30px}
@media(max-width:700px){.stats{grid-template-columns:repeat(2,1fr)}}.stat{background:white;border-radius:20px;padding:20px;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,0.06);border-top:5px solid #ff6b9d}
.stat h2{font-size:34px;color:#0a7a5a}.stat p{font-size:12px;font-weight:700;color:#555}
.review-card{background:white;border-radius:18px;padding:16px 20px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 4px 12px rgba(0,0,0,0.05);border-left:6px solid #00d09c}
.review-card.negative{border-left-color:#ff6b9d}.review-card.neutral{border-left-color:#8b5cf6}
.badge{padding:5px 14px;border-radius:20px;font-size:11px;font-weight:700;color:white;min-width:70px;text-align:center}
.positive{background:#00d09c}.negative{background:#ff6b9d}.neutral{background:#8b5cf6}
</style></head><body>
<div class="header"><h1>ReviewSense</h1><p>✨ Smart Review Sentiment Analysis ✨</p></div>
<div class="main">
<div class="stats">
<div class="stat"><div>📝</div><h2>{{total}}</h2><p>TOTAL REVIEWS</p></div>
<div class="stat"><div>💚</div><h2>{{pos}}</h2><p>POSITIVE</p></div>
<div class="stat"><div>💗</div><h2>{{neg}}</h2><p>NEGATIVE</p></div>
<div class="stat"><div>💛</div><h2>{{neu}}</h2><p>NEUTRAL</p></div>
</div>
<h2 style="text-align:center;color:#0a7a5a;margin-bottom:20px">📝 ✨ Customer Reviews (1000) ✨ 📝</h2>
<div style="max-height:800px;overflow-y:auto;padding-right:5px">
{% for r in reviews_data %}
<div class="review-card {{r.sentiment}}">
<div style="width:80%">
<div style="font-weight:600;color:#222;font-size:14px">🌸 Review #{{r.id}} - {{r.text}}</div>
<div style="font-size:12px;color:#666;margin-top:5px">👤 <b>{{r.customer}}</b> | 🛒 {{r.app}} | ⭐ {{r.rating}} | 📦 {{r.product}} | 📅 {{r.date}}</div>
</div>
<div class="badge {{r.sentiment}}">{{r.sentiment.upper()}}</div>
</div>
{% endfor %}
</div>
<div style="text-align:center;margin-top:25px"><a href="/" style="background:linear-gradient(90deg,#ff6b9d,#00d09c);color:white;padding:12px 30px;border-radius:12px;text-decoration:none;font-weight:700">← Upload New</a></div>
</div></body></html>"""

@app.route('/')
def home(): return render_template_string(HOME)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file: return "No file"
    path = os.path.join('uploads', file.filename)
    file.save(path)

    try:
        if path.endswith('.csv'): df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
        else: df = pd.read_excel(path)
    except: df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip')

    text_col = None
    for c in df.columns:
        if any(x in c.lower() for x in ['review','comment','text','feedback']): text_col=c; break
    if not text_col: text_col = df.select_dtypes(include='object').columns[0]

    reviews_data=[]
    pos=neg=neu=0

    # 1000 REVIEWS MOTTHAM ANALYZE
    for i, row in df.iterrows():
        if i >= 1000: break
        text = str(row[text_col])
        if text == 'nan' or len(text)<3: continue

        pol = TextBlob(text).sentiment.polarity
        if pol > 0.1: sent='positive'; pos+=1
        elif pol < -0.1: sent='negative'; neg+=1
        else: sent='neutral'; neu+=1

        customer = str(row.get('Customer', row.get('customer', row.get('User', row.get('Name', f'User {i+1}')))))
        app_name = str(row.get('App', row.get('Platform', row.get('Shopping App', row.get('Store', 'Amazon')))))
        product = str(row.get('Product', row.get('Item', 'Product')))[0:20]
        rating = str(row.get('Rating', row.get('Stars', '4.5')))
        date = str(row.get('Date', '2024-09-29'))

        reviews_data.append({"id":i+1, "text":text[:90]+"...", "sentiment":sent, "customer":customer[:15], "app":app_name[:12], "product":product, "rating":rating[:3], "date":date[:12]})

    app_data.update({"total":len(reviews_data), "pos":pos, "neg":neg, "neu":neu, "reviews_data":reviews_data, "filename":file.filename})
    return render_template_string(ANALYZE, **app_data)

@app.route('/analyze')
def analyze_page():
    return render_template_string(ANALYZE, **app_data) if app_data['total']>0 else render_template_string(HOME)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
