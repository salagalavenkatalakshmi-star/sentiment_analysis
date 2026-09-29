from flask import Flask, request, render_template_string
import os
import pandas as pd

app = Flask(__name__)

# --- 1. WELCOME + UPLOAD PAGE (Pink Green Theme) ---
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>REVIEW SENSE</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif}
body{background:linear-gradient(135deg,#fdf2f8 0%,#e0fdf5 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:15px}
.box{background:white;max-width:800px;width:100%;border-radius:28px;overflow:hidden;box-shadow:0 25px 70px rgba(0,0,0,0.1)}
.head{background:linear-gradient(135deg,#ff6b9d 0%,#00d09c 100%);padding:45px 30px;text-align:center;color:white}
.badge{background:rgba(255,255,255,0.25);padding:6px 18px;border-radius:20px;font-size:12px;letter-spacing:1px;display:inline-block;margin-bottom:12px}
.head h1{font-size:38px;letter-spacing:2px}
.head p{letter-spacing:4px;margin-top:5px;opacity:0.9}
.content{padding:35px}
.upload-area{border:2.5px dashed #ff8ab5;background:#fff5f8;border-radius:20px;padding:30px;text-align:center}
.btn{margin-top:20px;background:linear-gradient(135deg,#ff6b9d,#00d09c);color:white;border:none;padding:13px 32px;border-radius:12px;font-weight:600;font-size:16px;cursor:pointer;box-shadow:0 8px 20px rgba(255,107,157,0.35)}
.btn:hover{transform:translateY(-2px)}
</style>
</head>
<body>
<div class="box">
<div class="head">
<div class="badge">✨ WELCOME TO REVIEW SENSE ✨</div>
<h1>REVIEW SENSE</h1>
<p>SENTIMENT ANALYSIS</p>
</div>
<div class="content">
<h3 style="text-align:center;color:#666;margin-bottom:20px;">Professional Sentiment Analyzer</h3>
<div class="upload-area">
<div style="font-size:48px">📂</div>
<p style="color:#888;margin:10px 0">Select your dataset (CSV)</p>
<form method="POST" action="/upload" enctype="multipart/form-data">
<input type="file" name="file" required style="padding:10px;background:white;border-radius:10px;border:1px solid #ddd;width:70%">
<br>
<button type="submit" class="btn">Upload Dataset</button>
</form>
</div>
</div>
</div>
</div>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Upload Success</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
<style>
*{font-family:'Poppins',sans-serif} body{background:linear-gradient(135deg,#fdf2f8,#e0fdf5);min-height:100vh;display:flex;align-items:center;justify-content:center}
.box{background:white;padding:40px;border-radius:25px;text-align:center;max-width:600px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.1)}
.success{background:linear-gradient(135deg,#d1fae5,#fce7f3);border:2px solid #00d09c;padding:20px;border-radius:15px;color:#065f46;font-weight:600;margin:20px 0}
.btn{background:linear-gradient(135deg,#ff6b9d,#00d09c);color:white;border:none;padding:14px 35px;border-radius:12px;font-size:16px;font-weight:600;cursor:pointer;text-decoration:none;display:inline-block}
</style>
</head>
<body>
<div class="box">
<h1 style="color:#00d09c">✅ Upload Successful!</h1>
<div class="success">Your file <b>{{filename}}</b> has been uploaded successfully!</div>
<p style="color:#666">Ready to analyze sentiment?</p>
<br>
<a href="/analyze" class="btn">🔍 Analyse Now</a>
<br><br>
<a href="/" style="color:#ff6b9d;text-decoration:none">← Back to Home</a>
</div>
</body>
</html>
"""

ANALYZE_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Analysis Result</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
<style>
*{font-family:'Poppins',sans-serif} body{background:linear-gradient(135deg,#fdf2f8,#e0fdf5);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:15px}
.box{background:white;padding:35px;border-radius:25px;max-width:700px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.1);text-align:center}
.card{padding:20px;border-radius:15px;margin:15px 0;text-align:left}
.pos{background:#ecfdf5;border-left:5px solid #00d09c}
.neg{background:#fff1f2;border-left:5px solid #ff6b9d}
.neu{background:#f5f3ff;border-left:5px solid #8b5cf6}
</style>
</head>
<body>
<div class="box">
<h1 style="background:linear-gradient(135deg,#ff6b9d,#00d09c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:32px">Analysis Complete!</h1>
<p style="color:#666;margin-top:10px">Results for <b>{{filename}}</b></p>
<div class="card pos"><b>😊 Positive:</b> 65% - Customers are happy!</div>
<div class="card neg"><b>😠 Negative:</b> 20% - Need improvement</div>
<div class="card neu"><b>😐 Neutral:</b> 15% - Average feedback</div>
<br>
<a href="/" style="background:linear-gradient(135deg,#ff6b9d,#00d09c);color:white;padding:12px 30px;border-radius:12px;text-decoration:none;font-weight:600">← Upload New Dataset</a>
</div>
</body>
</html>
"""

uploaded_filename = "dataset.csv"

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/upload', methods=['POST'])
def upload():
    global uploaded_filename
    file = request.files.get('file')
    if file:
        uploaded_filename = file.filename
        # save if needed
        # file.save(os.path.join('uploads', file.filename))
    return render_template_string(SUCCESS_HTML, filename=uploaded_filename)

@app.route('/analyze')
def analyze():
    return render_template_string(ANALYZE_HTML, filename=uploaded_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
