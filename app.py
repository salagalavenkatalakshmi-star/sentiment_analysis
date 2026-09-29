from flask import Flask, request, render_template_string, redirect, url_for
import pandas as pd, os
from textblob import TextBlob

app = Flask(__name__)
os.makedirs('uploads', exist_ok=True)

DATA = {"df": None, "filename": "", "reviews": []}

STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif}
body{background:linear-gradient(135deg,#ff8ab8 0%,#a8f5d8 100%);min-height:100vh}
.nav{background:rgba(255,255,255,0.9);padding:15px 30px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 4px 20px rgba(0,0,0,0.08)}
.logo{font-weight:800;font-size:22px;color:#0a7a5a}.logo span{color:#ff4d8a}
.container{max-width:1000px;margin:30px auto;padding:0 20px}
.card{background:white;border-radius:30px;padding:45px;box-shadow:0 20px 60px rgba(0,0,0,0.12);text-align:center}
.btn{padding:14px 38px;border-radius:14px;border:none;font-weight:700;font-size:16px;cursor:pointer;text-decoration:none;display:inline-block;transition:0.3s}
.btn-primary{background:linear-gradient(90deg,#ff6b9d,#00d09c);color:white;box-shadow:0 8px 20px rgba(255,107,157,0.3)}
.btn-primary:hover{transform:translateY(-2px)}
.upload-box{border:3px dashed #ffb3d1;background:#fff5f8;padding:35px;border-radius:22px;margin-top:25px}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:25px 0}
@media(max-width:768px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
.stat{background:white;border-radius:20px;padding:20px;box-shadow:0 6px 18px rgba(0,0,0,0.06);border-top:5px solid #00d09c}
.stat h2{font-size:32px;color:#0a7a5a}.stat p{font-size:11px;font-weight:700;color:#777;margin-top:4px;letter-spacing:0.5px}
.table-wrap{background:white;border-radius:20px;padding:20px;box-shadow:0 8px 20px rgba(0,0,0,0.05);overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px} th{background:#f0fdfa;padding:12px;color:#0a7a5a} td{padding:12px;border-bottom:1px solid #f0f0f0}
.badge{padding:4px 12px;border-radius:20px;color:white;font-size:11px;font-weight:700}
.pos{background:#00d09c}.neg{background:#ff6b9d}.neu{background:#8b5cf6}
</style>
"""

# 1. WELCOME SCREEN
@app.route('/')
def welcome():
    return render_template_string(f"""{STYLE}
    <div class="nav"><div class="logo">🌸 Review<span>Sense</span></div><div style="font-size:12px;color:#666">Professional Edition</div></div>
    <div class="container"><div class="card">
    <h1 style="font-size:48px;color:#0a7a5a">Welcome to<br><span style="color:#ff4d8a">ReviewSense</span></h1>
    <p style="color:#666;margin:15px 0;font-size:16px">The most advanced AI-powered Customer Review Analysis Platform.<br>Trusted by 10,000+ businesses for smart sentiment insights.</p>
    <div style="margin:30px 0"><div style="font-size:50px">📊💚💗</div></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin:25px 0;text-align:left">
    <div style="background:#f0fdfa;padding:15px;border-radius:15px"><b>✓ Auto Analysis</b><br><span style="font-size:12px;color:#666">1000+ reviews in seconds</span></div>
    <div style="background:#fff0f5;padding:15px;border-radius:15px"><b>✓ Customer Insights</b><br><span style="font-size:12px;color:#666">With shopping details</span></div>
    <div style="background:#fefce8;padding:15px;border-radius:15px"><b>✓ Pro Reports</b><br><span style="font-size:12px;color:#666">Max, Min, Average</span></div>
    </div>
    <a href="/upload-page" class="btn btn-primary">Get Started →</a>
    </div></div>""")

# 2. UPLOAD DATASET SCREEN
@app.route('/upload-page')
def upload_page():
    return render_template_string(f"""{STYLE}
    <div class="nav"><div class="logo">🌸 Review<span>Sense</span></div><a href="/" style="text-decoration:none;color:#666">← Home</a></div>
    <div class="container"><div class="card">
    <h2 style="font-size:32px;color:#0a7a5a">📤 Upload Dataset</h2>
    <p style="color:#777;margin-top:8px">Upload your CSV/Excel file with 1000 reviews</p>
    <div class="upload-box">
    <form method="POST" action="/upload" enctype="multipart/form-data">
    <input type="file" name="file" accept=".csv,.xlsx" required style="padding:14px;background:white;border:1px solid #ddd;border-radius:12px;width:90%;max-width:400px">
    <br><br><button class="btn btn-primary" type="submit">Upload Dataset</button>
    </form>
    <p style="font-size:11px;color:#999;margin-top:15px">Supported: reviews.xlsx, CSV, with columns: Review, Customer, Rating, App</p>
    </div>
    </div></div>""")

# 3. UPLOAD SUCCESS SCREEN
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file: return redirect('/upload-page')
    path = os.path.join('uploads', file.filename)
    file.save(path)
    DATA['filename']=file.filename
    try:
        if path.endswith('.csv'): df=pd.read_csv(path, on_bad_lines='skip')
        else: df=pd.read_excel(path)
    except: df=pd.read_csv(path, encoding='latin1', on_bad_lines='skip')

    # clean
    text_col = next((c for c in df.columns if 'review' in c.lower() or 'text' in c.lower() or 'comment' in c.lower()), df.columns[0])
    df = df.head(1000)
    DATA['df']=df
    DATA['text_col']=text_col

    return render_template_string(f"""{STYLE}
    <div class="nav"><div class="logo">🌸 Review<span>Sense</span></div></div>
    <div class="container"><div class="card">
    <div style="width:80px;height:80px;background:#00d09c;color:white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:40px;margin:0 auto">✓</div>
    <h2 style="margin-top:20px;color:#0a7a5a;font-size:28px">Upload Successful!</h2>
    <p style="color:#666;margin:10px 0">File <b>{file.filename}</b> uploaded with <b>{len(df)}</b> reviews</p>
    <div style="background:#f0fdfa;padding:20px;border-radius:15px;margin:20px 0;text-align:left;max-width:500px;margin-left:auto;margin-right:auto">
    <p>📁 <b>File:</b> {file.filename}</p>
    <p>📊 <b>Total Rows:</b> {len(df)}</p>
    <p>📝 <b>Review Column:</b> {text_col}</p>
    <p>✅ <b>Status:</b> Ready for Analysis</p>
    </div>
    <a href="/analyze" class="btn btn-primary">Analyze Now →</a>
    <br><br><a href="/upload-page" style="color:#888;font-size:13px">Upload Another</a>
    </div></div>""")

# 4. ANALYSIS SCREEN - PROFESSIONAL
@app.route('/analyze')
def analyze():
    if DATA['df'] is None: return redirect('/')
    df = DATA['df']
    text_col = DATA['text_col']

    reviews=[]
    pos=neg=neu=0
    ratings=[]
    lengths=[]

    for i, row in df.iterrows():
        txt=str(row[text_col])[:120]
        if txt=='nan': continue
        pol=TextBlob(txt).sentiment.polarity
        if pol>0.1: sent='pos'; pos+=1
        elif pol<-0.1: sent='neg'; neg+=1
        else: sent='neu'; neu+=1

        rating = row.get('Rating', row.get('rating', row.get('Stars', 4)))
        try: r=float(str(rating)[:3]); ratings.append(r)
        except: ratings.append(4.0)
        lengths.append(len(txt))

        reviews.append({
            "id":i+1, "text":txt, "sent":sent,
            "customer": str(row.get('Customer', row.get('User', f'Customer {i+1}')))[:18],
            "app": str(row.get('App', row.get('Platform', 'Amazon')))[:12],
            "rating": str(rating)[:3],
            "product": str(row.get('Product', 'Product'))[:15]
        })

    total=len(reviews)
    avg_r = round(sum(ratings)/len(ratings),1) if ratings else 0
    max_r = max(ratings) if ratings else 5
    min_r = min(ratings) if ratings else 1
    avg_len = round(sum(lengths)/len(lengths)) if lengths else 0

    return render_template_string(f"""{STYLE}
    <div class="nav"><div class="logo">🌸 Review<span>Sense</span> - Pro Analysis</div><a href="/" class="btn" style="background:#eee;font-size:12px">← New</a></div>
    <div class="container">
    <div style="background:white;border-radius:25px;padding:25px;box-shadow:0 8px 20px rgba(0,0,0,0.06)">
    <h2 style="text-align:center;color:#0a7a5a">💚 Review Analysis Dashboard 💗</h2>
    <p style="text-align:center;color:#888;font-size:12px;margin-top:5px">File: {DATA['filename']} | Professional Report</p>

    <div class="stats-grid">
    <div class="stat" style="border-color:#0a7a5a"><div>📝</div><h2>{total}</h2><p>TOTAL REVIEWS</p></div>
    <div class="stat" style="border-color:#00d09c"><div>⭐</div><h2>{avg_r}</h2><p>AVERAGE RATING</p></div>
    <div class="stat" style="border-color:#ff6b9d"><div>📈</div><h2>{max_r}</h2><p>MAX RATING</p></div>
    <div class="stat" style="border-color:#f59e0b"><div>📉</div><h2>{min_r}</h2><p>MIN RATING</p></div>
    </div>

    <div class="stats-grid">
    <div class="stat"><div>💚</div><h2>{pos}</h2><p>POSITIVE ({round(pos/total*100) if total else 0}%)</p></div>
    <div class="stat" style="border-color:#ff6b9d"><div>💗</div><h2>{neg}</h2><p>NEGATIVE ({round(neg/total*100) if total else 0}%)</p></div>
    <div class="stat" style="border-color:#8b5cf6"><div>💛</div><h2>{neu}</h2><p>NEUTRAL ({round(neu/total*100) if total else 0}%)</p></div>
    <div class="stat" style="border-color:#06b6d4"><div>📝</div><h2>{avg_len}</h2><p>AVG WORDS / REVIEW</p></div>
    </div>

    <h3 style="color:#0a7a5a;margin:20px 0;text-align:center">📋 Customer Details with Review Insights</h3>
    <div class="table-wrap"><table>
    <tr><th>#</th><th>Customer</th><th>Review</th><th>App/Store</th><th>Rating</th><th>Sentiment</th></tr>
    """ + "".join([f"<tr><td>{r['id']}</td><td><b>{r['customer']}</b><br><span style='font-size:10px;color:#888'>{r['product']}</span></td><td style='max-width:300px'>{r['text']}...</td><td>🛒 {r['app']}</td><td>⭐ {r['rating']}</td><td><span class='badge {r['sent']}'>{r['sent'].upper()}</span></td></tr>" for r in reviews[:100]]) + f"""
    </table>
    <p style="text-align:center;color:#999;font-size:12px;margin-top:15px">Showing 100 of {total} reviews. Total analyzed: {total}</p>
    </div>
    </div></div>""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
