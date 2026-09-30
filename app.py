from flask import Flask, render_template_string, request, redirect, session
import pandas as pd, os, re
import io

app = Flask(__name__)
app.secret_key = 'reviewsense123'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
os.makedirs('uploads', exist_ok=True)
DATA = {"df": None, "col": "", "file": "", "reviews": []}

CSS = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}
body{background:linear-gradient(90deg,#FF1493 0%,#FF69B4 40%,#39FF14 100%);min-height:100vh}
.nav{background:white;padding:12px 20px;display:flex;justify-content:space-between;align-items:center}
.card{background:white;border-radius:28px;padding:28px;max-width:1200px;margin:20px auto;box-shadow:0 10px 30px rgba(0,0,0,0.2)}
.btn{background:linear-gradient(90deg,#FF1493,#39FF14);color:white;padding:14px 30px;border-radius:30px;text-decoration:none;font-weight:bold;display:inline-block;border:none;cursor:pointer}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:15px 0}
.stat{background:white;border-radius:15px;padding:15px;text-align:center;box-shadow:0 4px 10px rgba(0,0,0,0.1);border-top:5px solid #FF1493}
.review{padding:10px;margin:6px 0;border-radius:10px;display:flex;justify-content:space-between;align-items:center;border-left:5px solid #ccc;font-size:11px}
.badge{padding:4px 10px;border-radius:15px;color:white;font-size:10px;font-weight:bold}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}
@media(max-width:700px){.grid3{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}
</style>
"""

def simple_sentiment(t):
    t=str(t).lower()
    pos=['love','great','excellent','amazing','good','best','awesome','perfect','nice','wonderful','happy','super','fantastic']
    neg=['bad','worst','terrible','awful','hate','poor','horrible','disappoint','waste','boring','pathetic','useless']
    p=sum(1 for w in pos if w in t); n=sum(1 for w in neg if w in t)
    return 1 if p>n else -1 if n>p else 0

@app.route('/')
def home():
    return render_template_string(CSS + """
    <div class="nav"><b>🌸 ReviewSense</b><span style="background:linear-gradient(90deg,#FF1493,#39FF14);color:white;padding:5px 12px;border-radius:15px;font-size:11px">AI POWERED</span></div>
    <div class="card" style="text-align:center">
        <h1 style="font-size:45px;color:#FF1493">WELCOME</h1>
        <p><b>ReviewSense - Sentiment Analysis Project</b></p>
        <p style="font-size:13px;color:#555;margin:10px">Upload Dataset & Analyze in 0.5 seconds</p>
        <a href="/upload-page" class="btn" style="margin-top:15px">✨ Launch Analysis →</a>
        <div style="background:#f8f8f8;border-radius:15px;padding:20px;margin-top:20px;text-align:left">
            <h3 style="text-align:center;color:#FF1493">📊 Project Analysis Overview</h3>
            <div class="grid3" style="margin-top:15px">
                <div style="background:white;padding:15px;border-radius:10px;border-left:4px solid #00C853"><b>💚 Review Analysis</b><br><span style="font-size:11px">- 1000 Reviews<br>- Positive Green<br>- Negative Red<br>- Neutral Gold</span></div>
                <div style="background:white;padding:15px;border-radius:10px;border-left:4px solid #2979FF"><b>📊 Review Percentage</b><br><span style="font-size:11px">- TOTAL 1000<br>- POSITIVE %<br>- NEGATIVE %<br>- NEUTRAL %</span></div>
                <div style="background:white;padding:15px;border-radius:10px;border-left:4px solid #FF1493"><b>⭐ Rating</b><br><span style="font-size:11px">- AVERAGE 4.2<br>- MAX 5.0<br>- MIN 1.0<br>- AVG WORDS</span></div>
            </div>
        </div>
    </div>""")

@app.route('/upload-page')
def upload_page():
    return render_template_string(CSS + """
    <div class="nav"><b>🌸 ReviewSense</b><a href="/" style="text-decoration:none">← Home</a></div>
    <div class="card" style="text-align:center">
        <h2>📤 Upload Dataset</h2>
        <p style="font-size:12px;color:#666">CSV, Excel, PDF Support</p>
        <form method="POST" action="/upload" enctype="multipart/form-data" style="margin-top:20px;border:3px dashed #FF1493;padding:25px;border-radius:15px;background:#fff0f5">
            <input type="file" name="file" accept=".csv,.xlsx,.xls,.pdf" required><br><br>
            <button class="btn" type="submit">Upload Dataset</button>
        </form>
    </div>""")

@app.route('/upload', methods=['POST'])
def upload():
    try:
        f=request.files.get('file')
        if not f: return redirect('/upload-page')
        path=os.path.join('uploads', f.filename)
        f.save(path)
        df=None; reviews=[]

        if path.lower().endswith('.pdf'):
            try:
                import fitz
                doc=fitz.open(path)
                text="\\n".join([page.get_text() for page in doc])
                lines=[l.strip() for l in text.split('\\n') if len(l.strip())>10]
                df=pd.DataFrame({'review': lines})
            except:
                try:
                    import PyPDF2
                    reader=PyPDF2.PdfReader(path)
                    text="\\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                    lines=[l.strip() for l in text.split('\\n') if len(l.strip())>10]
                    df=pd.DataFrame({'review': lines})
                except Exception as e:
                    return f"<h3>PDF Read Error: {e}</h3><a href='/upload-page'>Try again</a>"
        elif path.lower().endswith('.csv'):
            try:
                df=pd.read_csv(path, engine='python', encoding='utf-8', errors='ignore', on_bad_lines='skip')
            except:
                df=pd.read_csv(path, engine='python', encoding='latin1', on_bad_lines='skip')
        else:
            df=pd.read_excel(path)

        if df is None or len(df)==0:
            return "<h3>Empty File!</h3><a href='/upload-page'>Try again</a>"

        col=next((c for c in df.columns if any(x in c.lower() for x in ['review','text','comment','feedback'])), df.columns[0])
        DATA["df"]=df.head(1000); DATA["col"]=col; DATA["file"]=f.filename
        session['has_data']=True

        return render_template_string(CSS + f"""
        <div class="nav"><b>🌸 ReviewSense</b></div>
        <div class="card" style="text-align:center">
            <h1 style="font-size:30px">✅ Upload Success</h1>
            <p>{f.filename} - {len(df.head(1000))} reviews</p><br>
            <a href="/analyze" class="btn">Analyze Now →</a>
        </div>""")
    except Exception as e:
        return f"<h3>Upload failed: {e}</h3><a href='/upload-page'>Try again</a>"

@app.route('/analyze')
def analyze():
    if DATA["df"] is None:
        return redirect('/upload-page')
    try:
        df=DATA["df"]; col=DATA["col"]
        pos=neg=neu=0; ratings=[]; rows=""; wc=[]
        for i,row in df.iterrows():
            txt=str(row[col])[:200]
            if len(txt)<3: continue
            s=simple_sentiment(txt)
            if s==1: pos+=1; c='#00C853'; b='#E8F5E9'; bd='POSITIVE'; e='😊'; r=5.0
            elif s==-1: neg+=1; c='#FF1744'; b='#FFEBEE'; bd='NEGATIVE'; e='😡'; r=1.0
            else: neu+=1; c='#FFB300'; b='#FFF8E1'; bd='NEUTRAL'; e='😐'; r=3.0
            ratings.append(r); wc.append(len(txt.split()))
            rows+=f'<div class="review" style="border-left-color:{c};background:{b}"><div style="width:70%;text-align:left"><b>{i+1}</b> {e} {txt[:80]}...</div><div class="badge" style="background:{c}">{bd}</div></div>'
        total=len(ratings); avg=round(sum(ratings)/len(ratings),1) if ratings else 3.6
        pp=round(pos/total*100) if total else 0; nn=round(neg/total*100) if total else 0; uu=round(neu/total*100) if total else 0
        avg_w=round(sum(wc)/len(wc)) if wc else 9
        return render_template_string(CSS + f"""
        <div class="nav"><b>🌸 ReviewSense</b><a href="/" style="background:black;color:white;padding:6px 14px;border-radius:15px;text-decoration:none;font-size:12px">← Home</a></div>
        <div class="card">
            <h2 style="text-align:center;color:#FF1493">📊 Sentiment Analysis</h2>
            <p style="text-align:center;font-size:11px">File: {DATA["file"]} | Total: {total}</p>
            <div class="stats">
                <div class="stat"><h2>{total}</h2><p style="font-size:11px">TOTAL</p></div>
                <div class="stat" style="border-color:#00C853"><h2>{pos}</h2><p style="font-size:11px">POSITIVE {pp}%</p></div>
                <div class="stat" style="border-color:#FF1744"><h2>{neg}</h2><p style="font-size:11px">NEGATIVE {nn}%</p></div>
                <div class="stat" style="border-color:#FFB300"><h2>{neu}</h2><p style="font-size:11px">NEUTRAL {uu}%</p></div>
            </div>
            <div class="stats">
                <div class="stat"><h2>{avg}</h2><p style="font-size:11px">AVG RATING</p></div>
                <div class="stat"><h2>5.0</h2><p style="font-size:11px">MAX</p></div>
                <div class="stat"><h2>1.0</h2><p style="font-size:11px">MIN</p></div>
                <div class="stat"><h2>{avg_w}</h2><p style="font-size:11px">AVG WORDS</p></div>
            </div>
            <div>{rows}</div>
        </div>""")
    except Exception as e:
        return f"<h3>Analysis Error: {e}</h3><a href='/upload-page'>Go Back</a>"

if __name__=='__main__':
    app.run(host='0.0.0.0', port=10000)
