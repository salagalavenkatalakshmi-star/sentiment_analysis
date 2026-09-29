from flask import Flask, request, render_template_string, redirect
import pandas as pd, os
from textblob import TextBlob

app = Flask(__name__)
os.makedirs('uploads', exist_ok=True)
DATA = {"df":None, "text_col":"", "filename":""}

# --- BRIGHT PINK + PARROT GREEN THEME ---
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif}
body{background:linear-gradient(90deg,#FF1493 0%, #FF69B4 25%, #39FF14 100%);min-height:100vh}
.nav{background:white;padding:15px 30px;display:flex;justify-content:space-between;box-shadow:0 4px 20px rgba(0,0,0,0.1)}
.card{background:white;border-radius:30px;padding:35px;box-shadow:0 20px 60px rgba(0,0,0,0.2);text-align:center;max-width:1100px;margin:30px auto}
.btn{background:linear-gradient(90deg,#FF1493,#39FF14);color:white;padding:14px 40px;border-radius:15px;border:none;font-weight:800;font-size:16px;cursor:pointer;text-decoration:none;display:inline-block}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:20px 0}
.stat{background:white;border-radius:20px;padding:20px;box-shadow:0 8px 20px rgba(0,0,0,0.08);border-top:6px solid #FF1493}
.stat:nth-child(2){border-color:#39FF14}.stat:nth-child(3){border-color:#FF1493}.stat:nth-child(4){border-color:#FFD700}
.stat h2{font-size:36px;color:#111}
.review-row{background:white;border-radius:16px;padding:14px 18px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 4px 12px rgba(0,0,0,0.06);border-left:6px solid #39FF14}
.review-row.neg{border-left-color:#FF1493}.review-row.neu{border-left-color:#8A2BE2}
.badge{padding:6px 14px;border-radius:20px;color:white;font-weight:800;font-size:12px}
.pos{background:#00C853}.neg{background:#FF1744}.neu{background:#7C4DFF}
</style>
"""

@app.route('/')
def home():
    return render_template_string(f"""{CSS}
    <div class="nav"><b>🌸 ReviewSense</b> <span>Bright Edition</span></div>
    <div class="card"><h1 style="font-size:50px;color:#FF1493">WELCOME</h1><p>To ReviewSense - Pink & Parrot Green</p>
    <div style="margin:20px 0;font-size:40px">💖🦜✨</div>
    <a href="/upload-page" class="btn">Get Started →</a></div>""")

@app.route('/upload-page')
def upload_page():
    return render_template_string(f"""{CSS}
    <div class="nav"><b>🌸 ReviewSense</b><a href="/">Home</a></div>
    <div class="card"><h2>📤 Upload Dataset (1000 Reviews)</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data" style="margin-top:20px;border:3px dashed #FF1493;padding:30px;border-radius:20px;background:#FFF0F5">
    <input type="file" name="file" required style="padding:12px;border-radius:10px;border:1px solid #ddd;width:80%"><br><br>
    <button class="btn" type="submit">Upload</button></form></div>""")

@app.route('/upload', methods=['POST'])
def upload():
    file=request.files.get('file')
    if not file: return redirect('/upload-page')
    path=os.path.join('uploads', file.filename); file.save(path)
    try:
        df = pd.read_csv(path, on_bad_lines='skip') if path.endswith('.csv') else pd.read_excel(path)
    except: df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip')
    text_col = next((c for c in df.columns if 'review' in c.lower() or 'comment' in c.lower() or 'text' in c.lower()), df.columns[0])
    DATA.update({"df":df.head(1000), "text_col":text_col, "filename":file.filename})
    return render_template_string(f"""{CSS}
    <div class="nav"><b>🌸 ReviewSense</b></div>
    <div class="card"><div style="font-size:60px">✅</div><h2>Upload Successful!</h2>
    <p>File: {file.filename} | Total: {len(df)} Reviews</p><br>
    <a href="/analyze" class="btn">Analyze 1000 Reviews →</a></div>""")

@app.route('/analyze')
def analyze():
    if DATA['df'] is None: return redirect('/')
    df=DATA['df']; text_col=DATA['text_col']
    reviews=[]; pos=neg=neu=0
    for i,row in df.iterrows():
        txt=str(row[text_col])
        if txt=='nan': continue
        pol=TextBlob(txt).sentiment.polarity
        if pol>0.1: sent='pos'; pos+=1
        elif pol<-0.1: sent='neg'; neg+=1
        else: sent='neu'; neu+=1
        reviews.append({
            "id":i+1, "text":txt[:100], "sent":sent,
            "cust":str(row.get('Customer', row.get('customer', row.get('Name', f'Customer {i+1}'))))[:20],
            "app":str(row.get('App', row.get('Platform', 'Amazon')))[:12],
            "rate":str(row.get('Rating', '4'))[:1]
        })

    total=len(reviews)
    rows_html="".join([f'<div class="review-row {r["sent"]}"><div style="width:75%;text-align:left"><b>{r["id"]}. {r["cust"]}</b> <span style="color:#666;font-size:12px">| {r["text"]}...</span><br><span style="font-size:11px;color:#888">🛒 {r["app"]} | ⭐ {r["rate"]}</span></div><div class="badge {r["sent"]}">{r["sent"].upper()}</div></div>' for r in reviews])

    return render_template_string(f"""{CSS}
    <div class="nav"><b>🌸 ReviewSense - 1000 Analysis</b><a href="/" style="text-decoration:none">← New</a></div>
    <div class="card" style="max-width:1200px">
    <h2 style="color:#FF1493">💖 Review Analysis - Bright Edition 🦜</h2>
    <div class="stats">
    <div class="stat"><h2>{total}</h2><p>TOTAL REVIEWS</p></div>
    <div class="stat"><h2>{pos}</h2><p>POSITIVE</p></div>
    <div class="stat"><h2>{neg}</h2><p>NEGATIVE</p></div>
    <div class="stat"><h2>{neu}</h2><p>NEUTRAL</p></div>
    </div>
    <h3 style="margin:15px 0">📋 All {total} Customer Reviews (Your Dataset)</h3>
    <div style="max-height:2000px;overflow-y:auto;text-align:left">{rows_html}</div>
    <p style="margin-top:15px;color:#FF1493;font-weight:700">✅ Showing ALL {total} of {total} Reviews - Total Analyzed: {total}</p>
    </div>""")

if __name__=='__main__': app.run(host='0.0.0.0', port=10000)
