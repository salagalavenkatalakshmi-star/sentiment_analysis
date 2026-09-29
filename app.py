from flask import Flask, request, render_template_string
import pandas as pd
import os
from textblob import TextBlob

app = Flask(__name__)
os.makedirs('uploads', exist_ok=True)

# STORAGE
app_data = {"filename": "", "total": 0, "pos":0, "neg":0, "neu":0, "reviews_data":[]}

HOME = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ReviewSense</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif}
body{background:linear-gradient(90deg,#ff7eb3 0%,#7af0c0 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:white;width:100%;max-width:900px;border-radius:30px;padding:50px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.15)}
h1{font-size:48px;letter-spacing:2px}.sub{letter-spacing:4px;color:#555;margin-top:5px}
.upload{margin-top:30px;border:3px dashed #ff9ac1;background:#fff0f5;padding:30px;border-radius:20px}
.btn{background:linear-gradient(90deg,#ff6b9d,#00d09c);color:white;border:none;padding:14px 40px;border-radius:15px;font-size:18px;font-weight:700;cursor:pointer;margin-top:20px}
</style></head>
<body>
<div class="card">
<h1>REVIEW SENSE</h1><p class="sub">SENTIMENT ANALYSIS</p>
<div class="upload">
<p style="font-size:20px">👋 Welcome to ReviewSense!</p>
<p style="color:#777;margin:10px 0">Upload your dataset to get automatic analysis</p>
<form method="POST" action="/upload" enctype="multipart/form-data">
<input type="file" name="file" required style="padding:12px;background:white;border-radius:10px;border:1px solid #ddd;width:80%">
<br><button class="btn">Upload Dataset</button>
</form>
</div>
</div></body></html>
"""

ANALYZE = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ReviewSense - Analysis</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif}
body{background:linear-gradient(90deg,#ff8ab8 0%,#a8f5d8 100%);min-height:100vh;padding:0}
.header{text-align:center;padding:40px 20px;color:white}
.header h1{font-size:52px;text-shadow:2px 2px 0px #ff4d8a, 4px 4px 0px rgba(0,0,0,0.1);letter-spacing:1px}
.header p{margin-top:8px;font-size:18px;letter-spacing:2px;font-weight:600}
.main{background:#f7fffe;margin:0 20px 20px;border-radius:35px;padding:35px;box-shadow:0 15px 50px rgba(0,0,0,0.1)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-bottom:35px}
@media(max-width:768px){.stats{grid-template-columns:repeat(2,1fr)}}
.stat{background:white;border-radius:20px;padding:22px;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,0.06);border-top:5px solid #ff6b9d}
.stat:nth-child(1){border-color:#ff6b9d}.stat:nth-child(2){border-color:#00d09c}.stat:nth-child(3){border-color:#ff6b9d}.stat:nth-child(4){border-color:#ffbe0b}
.stat h2{font-size:36px;color:#0a7a5a}.stat p{font-size:13px;font-weight:700;color:#555;margin-top:5px;letter-spacing:0.5px}
.review-title{text-align:center;color:#0a7a5a;font-size:28px;font-weight:800;margin-bottom:20px}
.review-card{background:white;border-radius:18px;padding:18px 22px;margin-bottom:15px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 4px 12px rgba(0,0,0,0.05);border-left:5px solid #00d09c}
.review-card.negative{border-left-color:#ff6b9d}.review-card.neutral{border-left-color:#8b5cf6}
.badge{padding:5px 14px;border-radius:20px;font-size:12px;font-weight:700;color:white}
.badge.positive{background:#00d09c}.badge.negative{background:#ff6b9d}.badge.neutral{background:#8b5cf6}
.customer{font-size:13px;color:#666;margin-top:4px}
.flower{position:fixed;bottom:0;font-size:80px;pointer-events:none}.f1{left:10px}.f2{right:10px}
</style></head>
<body>
<div class="header">
<h1>ReviewSense</h1>
<p>✨ Smart Review Sentiment Analysis ✨</p>
</div>
<div class="main">
<h2 style="text-align:center;color:#0a7a5a;font-size:26px;margin-bottom:20px">💚 Review Analysis 💗</h2>
<div class="stats">
<div class="stat"><div>📝</div><h2>{{total}}</h2><p>TOTAL REVIEWS</p></div>
<div class="stat"><div>💚</div><h2>{{pos}}</h2><p>POSITIVE</p></div>
<div class="stat"><div>💗</div><h2>{{neg}}</h2><p>NEGATIVE</p></div>
<div class="stat"><div>💛</div><h2>{{neu}}</h2><p>NEUTRAL</p></div>
</div>

<h2 class="review-title">📝 ✨ Customer Reviews ✨ 📝</h2>
{% for r in reviews_data %}
<div class="review-card {{r.sentiment}}">
<div>
<div style="font-weight:700;color:#333">🌸 Review #{{loop.index}} <span style="color:#888;font-weight:400">- {{r.text[:80]}}...</span></div>
<div class="customer">👤 {{r.customer}} | 🛒 {{r.app}} | ⭐ {{r.rating}} | 📅 {{r.date}}</div>
</div>
<div class="badge {{r.sentiment}}">{{r.sentiment.upper()}}</div>
</div>
{% endfor %}

<div style="text-align:center;margin-top:30px">
<a href="/" style="background:linear-gradient(90deg,#ff6b9d,#00d09c);color:white;padding:12px 30px;border-radius:12px;text-decoration:none;font-weight:700">← Upload New Dataset</a>
</div>
</div>
<div class="flower f1">🌷</div><div class="flower f2">🌷</div>
</body></html>
"""

@app.route('/')
def home(): return render_template_string(HOME)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file: return "No file"
    path = os.path.join('uploads', file.filename)
    file.save(path)
    app_data['filename'] = file.filename

    # ---- AUTO ANALYSIS ----
    try:
        df = pd.read_csv(path, encoding='utf-8', encoding_errors='ignore')
        if df.shape[0]==0: df = pd.read_csv(path, encoding='latin1')
    except:
        try: df = pd.read_excel(path)
        except: df = pd.DataFrame()

    # Auto detect columns
    text_col = None
    for c in df.columns:
        if any(x in c.lower() for x in ['review','comment','text','feedback']): text_col=c; break
    if not text_col: text_col = df.select_dtypes(include='object').columns[0] if len(df.select_dtypes(include='object').columns)>0 else df.columns[0]

    reviews_data=[]
    pos=neg=neu=0
    for i, row in df.iterrows():
        text = str(row[text_col])[:300]
        # Sentiment
        pol = TextBlob(text).sentiment.polarity
        if pol > 0.1: sent='positive'; pos+=1
        elif pol < -0.1: sent='negative'; neg+=1
        else: sent='neutral'; neu+=1

        # Customer details - auto find
        customer = str(row.get('Customer', row.get('customer', row.get('Name', row.get('User', f'Customer {i+1}')))))[:25]
        app_name = str(row.get('App', row.get('Product', row.get('Platform', row.get('Shopping App', 'Amazon')))))[:20]
        rating = str(row.get('Rating', row.get('Stars', '5')))[0:3]
        date = str(row.get('Date', '2024'))

        reviews_data.append({"text":text, "sentiment":sent, "customer":customer, "app":app_name, "rating":rating, "date":date})
        if len(reviews_data) >= 100: break

    app_data.update({"total":len(df), "pos":pos, "neg":neg, "neu":neu, "reviews_data":reviews_data})
    return render_template_string(ANALYZE, **app_data)

@app.route('/analyze')
def analyze_page():
    if app_data['total']==0: return render_template_string(HOME)
    return render_template_string(ANALYZE, **app_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
