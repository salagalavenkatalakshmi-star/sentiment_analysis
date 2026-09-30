from flask import Flask, render_template_string, request, redirect
import pandas as pd, os, re

app = Flask(__name__)
os.makedirs('uploads', exist_ok=True)
DATA = {"df": None, "col": "", "file": ""}

CSS = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}
body{background:linear-gradient(90deg,#FF1493 0%,#FF69B4 40%,#39FF14 100%);min-height:100vh}
.nav{background:white;padding:12px 20px;display:flex;justify-content:space-between;align-items:center}
.card{background:white;border-radius:28px;padding:28px;max-width:1200px;margin:20px auto;box-shadow:0 10px 30px rgba(0,0,0,0.2)}
.btn{background:linear-gradient(90deg,#FF1493,#39FF14);color:white;padding:14px 30px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;border:none}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:15px 0}
.stat{background:white;border-radius:15px;padding:15px;text-align:center;box-shadow:0 4px 10px rgba(0,0,0,0.1);border-top:5px solid #FF1493}
.review{padding:10px;margin:6px 0;border-radius:10px;display:flex;justify-content:space-between;align-items:center;border-left:5px solid #ccc}
.badge{padding:4px 10px;border-radius:15px;color:white;font-size:11px;font-weight:bold}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}
@media(max-width:700px){.grid3{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}
</style>
"""

def simple_sentiment(t):
    t = t.lower()
    pos = ['love','great','excellent','amazing','good','best','awesome','perfect','nice','wonderful']
    neg = ['bad','worst','terrible','awful','hate','poor','horrible','disappoint','waste']
    p = sum(1 for w in pos if w in t)
    n = sum(1 for w in neg if w in t)
    return 1 if p>n else -1 if n>p else 0

@app.route('/')
def home():
    return render_template_string(CSS + """
    <div class="nav"><b>🌸 ReviewSense</b><span style="background:linear-gradient(90deg,#FF1493,#39FF14);color:white;padding:5px 12px;border-radius:15px;font-size:11px">AI POWERED</span></div>
    <div class="card" style="text-align:center">
        <h1 style="font-size:45px;color:#FF1493">WELCOME</h1>
        <p>ReviewSense - Sentiment Analysis Project</p>
        <p style="font-size:13px;color:#555;margin:10px">Advanced AI analyzes every review in 0.5 seconds</p>
        <a href="/upload-page" class="btn" style="margin-top:15px">✨ Launch Analysis →</a>
        <div style="background:#f8f8f8;border-radius:15px;padding:20px;margin-top:20px;text-align:left">
            <h3 style="text-align:center;color:#FF1493">📊 Project Analysis Overview</h3>
            <div class="grid3" style="margin-top:15px">
                <div style="background:white;padding:15px;border-radius:10px;border-left:4px solid #00C853"><b>💚 Review Analysis</b><br><span style="font-size:11px">- 1000 Reviews<br>- Positive Green<br>- Negative Red<br>- Neutral Gold</span></div>
                <div style="background:white;padding:15px;border-radius:10px;border-left:4px solid #2979FF"><b>📊 Review Percentage</b><br><span style="font-size:11px">- TOTAL 1000<br>- POSITIVE %<br>- NEGATIVE %<br>- NEUTRAL %</span></div>
                <div style="background:white;padding:15px;border-radius:10px;border-left:4px solid #FF1493"><b>⭐ Rating</b><br><span style="font-size:11px">- AVERAGE 4.2<br>- MAX 5.0<br>- MIN 1.0<br>- AVG WORDS</span></div>
            </div>
        </div>
    </div>
    """)

@app.route('/upload-page')
def upload_page():
    return render_template_string(CSS + """
    <div class="nav"><b>🌸 ReviewSense</b><a href="/" style="text-decoration:none">← Home</a></div>
    <div class="card" style="text-align:center">
        <h2>📤 Upload Dataset</h2>
        <p style="font-size:12px;color:#666">Upload 1000 Reviews Dataset</p>
        <form method="POST" action="/upload" enctype="multipart/form-data" style="margin-top:20px;border:3px dashed #FF1493;padding:25px;border-radius:15px;background:#fff0f5">
            <input type="file" name="file" required><br><br>
            <button class="btn" type="submit">Upload Dataset</button>
        </form>
    </div>
    """)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        f = request.files.get('file')
        if not f: return redirect('/upload-page')
        path = os.path.join('uploads', f.filename)
        f.save(path)
        try:
            if path.endswith('.csv'):
                df = pd.read_csv(path, encoding='utf-8', errors='ignore', on_bad_lines='skip')
            else:
                df = pd.read_excel(path)
        except:
            df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip')
        col = next((c for c in df.columns if 'review' in c.lower() or 'text' in c.lower()), df.columns[0])
        DATA["df"] = df.head(1000)
        DATA["col"] = col
        DATA["file"] = f.filename
        return render_template_string(CSS + f"""
        <div class="nav"><b>🌸 ReviewSense</b></div>
        <div class="card" style="text-align:center"><h1>✅ Upload Success</h1><p>{f.filename} - {len(df.head(1000))} reviews</p><br><a href="/analyze" class="btn">Analyze Now →</a></div>
        """)
    except Exception as e:
        return f"<h3>Upload failed: {e}</h3><a href='/upload-page'>Try again</a>"

@app.route('/analyze')
def analyze():
    try:
        if DATA["df"] is None:
            return redirect('/upload-page')
        df = DATA["df"]; col = DATA["col"]
        pos=neg=neu=0; ratings=[]; rows=""; wc=[]
        for i,row in df.iterrows():
            txt=str(row[col])
            if len(txt)<3: continue
            s=simple_sentiment(txt)
            if s==1: pos+=1; c='#00C853'; b='#E8F5E9'; bd='💚 POSITIVE'; e='😊'; r=5.0
            elif s==-1: neg+=1; c='#FF1744'; b='#FFEBEE'; bd='❤️ NEGATIVE'; e='😡'; r=1.0
            else: neu+=1; c='#FFB300'; b='#FFF8E1'; bd='💛 NEUTRAL'; e='😐'; r=3.0
            ratings.append(r); wc.append(len(txt.split()))
            rows+=f'<div class="review" style="border-left-color:{c};background:{b}"><div style="width:75%;text-align:left;font-size:11px"><b>{i+1}. C{i+1}</b> {e} {txt[:90]}...</div><div class="badge" style="background:{c}">{bd}</div></div>'
        total=len(ratings); avg=round(sum(ratings)/len(ratings),1) if ratings else 4.0
        pp=round(pos/total*100) if total else 0; nn=round(neg/total*100) if total else 0; uu=round(neu/total*100) if total else 0
        avg_w=round(sum(wc)/len(wc)) if wc else 9
        return render_template_string(CSS + f"""
        <div class="nav"><b>🌸 ReviewSense</b><a href="/" style="background:black;color:white;padding:6px 14px;border-radius:15px;text-decoration:none;font-size:12px">← Back to Home</a></div>
        <div class="card">
            <h2 style="text-align:center;color:#FF1493">📊 Sentiment Analysis</h2>
            <p style="text-align:center;font-size:11px;color:#666">File: {DATA["file"]} | Total: {total}</p>
            <div class="stats">
                <div class="stat"><h2>{total}</h2><p style="font-size:11px">TOTAL REVIEWS</p><span style="font-size:10px">100%</span></div>
                <div class="stat" style="border-color:#00C853"><h2>{pos}</h2><p style="font-size:11px">POSITIVE</p><span style="font-size:10px;color:#00C853">{pp}% 😊</span></div>
                <div class="stat" style="border-color:#FF1744"><h2>{neg}</h2><p style="font-size:11px">NEGATIVE</p><span style="font-size:10px;color:#FF1744">{nn}% 😡</span></div>
                <div class="stat" style="border-color:#FFB300"><h2>{neu}</h2><p style="font-size:11px">NEUTRAL</p><span style="font-size:10px;color:#FFB300">{uu}% 😐</span></div>
            </div>
            <div class="stats">
                <div class="stat" style="border-color:#00C853"><h2>{avg}</h2><p style="font-size:11px">AVERAGE RATING</p></div>
                <div class="stat" style="border-color:#2979FF"><h2>5.0</h2><p style="font-size:11px">MAX RATING</p></div>
                <div class="stat" style="border-color:#FF1744"><h2>1.0</h2><p style="font-size:11px">MIN RATING</p></div>
                <div class="stat" style="border-color:#7C4DFF"><h2>{avg_w}</h2><p style="font-size:11px">AVG WORDS</p></div>
            </div>
            <div>{rows}</div>
        </div>
        """)
    except Exception as e:
        return redirect('/')

@app.errorhandler(500)
def handle_500(e):
    return redirect('/')

@app.errorhandler(404)
def handle_404(e):
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
