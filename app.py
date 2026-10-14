
from flask import Flask, render_template_string, request, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import os
import re
import html

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA = {"df": None, "col": "", "file": ""}

CSS = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}
body{min-height:100vh;padding:15px;background:linear-gradient(120deg,#ff1493,#ff85c1,#8be6ac,#25c976)}
.nav{background:white;padding:16px 22px;border-radius:18px;max-width:1100px;margin:0 auto 18px;display:flex;justify-content:space-between;align-items:center;gap:10px;box-shadow:0 5px 18px #0002}
.brand{color:#e91e8c;font-weight:bold;font-size:clamp(15px,3vw,22px)}
.tag{background:linear-gradient(90deg,#ff1493,#20bf6b);color:white;padding:7px 12px;border-radius:20px;font-size:10px;white-space:nowrap}
.card{max-width:1100px;margin:auto;background:rgba(255,255,255,.97);padding:28px;border-radius:25px;box-shadow:0 12px 35px #0002}
h1{text-align:center;color:#e91e8c;font-size:clamp(25px,5vw,38px);margin:12px 0}
.subtitle{text-align:center;color:#555;line-height:1.7;margin-bottom:20px}
.upload{background:#fff0f7;border:2px dashed #ff1493;border-radius:18px;padding:28px 15px;text-align:center;margin:22px 0}
input[type=file]{width:100%;max-width:400px;padding:12px;background:white;border:1px solid #ddd;border-radius:10px;margin:18px 0}
.btn{display:inline-block;background:linear-gradient(90deg,#ff1493,#20bf6b);color:white;padding:13px 22px;border:0;border-radius:25px;font-weight:bold;text-decoration:none;cursor:pointer;margin:5px}
.success{background:#e8f8ee;color:#16763b;padding:15px;border-radius:12px;margin:18px 0;overflow-wrap:anywhere}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:22px 0}
.stat{padding:20px 8px;border-radius:15px;text-align:center;background:white;box-shadow:0 4px 12px #0001;border-top:5px solid #ff1493}
.stat h2{font-size:28px;margin-bottom:8px}
.stat p{font-size:12px;font-weight:bold}
.total{background:#f4efff;border-color:#8b5cf6}
.pos{background:#e9fff1;border-color:#20bf6b}
.neg{background:#fff0f1;border-color:#ff3547}
.neu{background:#fff9e5;border-color:#ffb300}
.section-title{color:#e91e8c;margin:25px 0 12px}
.table-wrap{width:100%;overflow-x:auto;border-radius:12px}
table{width:100%;min-width:440px;border-collapse:collapse;background:white}
th,td{border:1px solid #eee;padding:12px;text-align:left;overflow-wrap:anywhere}
th{background:linear-gradient(90deg,#ff1493,#20bf6b);color:white}
tr:nth-child(even){background:#fff5fa}
.footer{text-align:center;font-size:12px;color:#777;margin-top:25px}
.center{text-align:center}
@media(max-width:650px){
body{padding:9px}.card{padding:18px 12px;border-radius:18px}
.nav{padding:13px}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}
.stat h2{font-size:23px}
}
</style>
"""

def find_review_column(df):
    keys = ["review", "feedback", "comment", "text"]
    for col in df.columns:
        if any(k in str(col).lower() for k in keys):
            return col
    return df.columns[0]

def simple_sentiment(text):
    t = str(text).lower()
    t = re.sub(r"[^a-z0-9\s']", " ", t)
    words = t.split()

    positive = {
        "love", "great", "excellent", "amazing", "good",
        "best", "awesome", "perfect", "nice", "wonderful",
        "happy", "super", "fantastic", "outstanding",
        "satisfied", "recommend", "beautiful", "useful",
        "comfortable", "fast", "helpful"
    }
    negative = {
        "bad", "worst", "terrible", "awful", "hate",
        "poor", "horrible", "disappoint", "disappointed",
        "waste", "boring", "pathetic", "useless",
        "broken", "slow", "expensive", "problem",
        "defective", "dirty", "damage", "damaged"
    }
    negations = {
        "not", "never", "no", "hardly", "isn't",
        "wasn't", "don't", "doesn't", "didn't"
    }

    p = 0
    n = 0

    for i, word in enumerate(words):
        # Check for negation near the sentiment word
        start = max(0, i - 3)
        negated = any(w in negations for w in words[start:i])

        if word in positive:
            if negated:
                n += 1
            else:
                p += 1

        if word in negative:
            if negated:
                p += 1
            else:
                n += 1

    if p > n:
        return "POSITIVE"
    if n > p:
        return "NEGATIVE"
    return "NEUTRAL"


def page(content, **kwargs):
    return render_template_string(
        CSS + """
        <div class="nav">
            <span class="brand">🌸 Customer Feedback Analysis</span>
            <span class="tag">AI POWERED</span>
        </div>
        """ + content,
        **kwargs
    )


@app.route("/")
def home():
    return page("""
    <div class="card">
        <h1>Customer Feedback Analysis</h1>
        <p class="subtitle">
            <b>Welcome to Customer Feedback Analysis System</b><br>
            Understand Customer Opinions Through Sentiment Analysis
        </p>

        <div class="upload">
            <h3 style="color:#e91e8c;margin-bottom:12px">
                📂 Upload Your Dataset
            </h3>
            <p style="color:#666">
                Select a CSV or Excel dataset containing customer reviews.
                Text-based PDFs are also supported.
            </p>

            <form action="/upload" method="post"
                  enctype="multipart/form-data">
                <input type="file" name="file"
                       accept=".csv,.xlsx,.xls,.pdf" required>
                <br>
                <button class="btn" type="submit">
                    📤 Upload Dataset
                </button>
            </form>
        </div>

        <p class="subtitle">
            😊 Positive &nbsp; | &nbsp; 😡 Negative
            &nbsp; | &nbsp; 😐 Neutral
        </p>
        <div class="footer">
            Customer Feedback Analysis | Sentiment Analysis System
        </div>
    </div>
    """)


@app.route("/upload", methods=["POST"])
def upload():
    try:
        f = request.files.get("file")

        if not f or not f.filename:
            return "Please select a dataset.", 400

        filename = secure_filename(f.filename)

        if not filename:
            return "Invalid filename.", 400

        ext = os.path.splitext(filename)[1].lower()

        if ext not in {".csv", ".xlsx", ".xls", ".pdf"}:
            return "Unsupported file type. Upload CSV, Excel or PDF.", 400

        path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path)

        if ext == ".csv":
            try:
                df = pd.read_csv(
                    path, encoding="utf-8-sig",
                    on_bad_lines="skip"
                )
            except (UnicodeDecodeError, ValueError):
                df = pd.read_csv(
                    path, encoding="latin1",
                    on_bad_lines="skip"
                )

        elif ext in {".xlsx", ".xls"}:
            df = pd.read_excel(path)

        else:
            try:
                import fitz
                doc = fitz.open(path)
                text = "\n".join(p.get_text() for p in doc)
                doc.close()
            except ImportError:
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(path)
                    text = "\n".join(
                        p.extract_text() or "" for p in reader.pages
                    )
                except ImportError:
                    return (
                        "PDF support requires PyMuPDF or pypdf. "
                        "Install with: pip install pymupdf"
                    ), 500

            lines = [
                line.strip().strip('"').strip("'")
                for line in text.splitlines()
                if line.strip()
            ]
            lines = [
                line for line in lines
                if line.lower() != "review" and len(line) > 5
            ]
            df = pd.DataFrame({"review": lines})

        if df.empty or len(df.columns) == 0:
            return """
            <h3>Dataset is empty or could not be read.</h3>
            <a href="/">Try again</a>
            """, 400

        df.columns = [str(c).strip() for c in df.columns]
        col = find_review_column(df)

        df = df.head(1000).copy()
        df = df.dropna(subset=[col])
        df[col] = df[col].astype(str).str.strip()
        df = df[df[col].str.len() > 0].reset_index(drop=True)

        if df.empty:
            return """
            <h3>No customer reviews found in the selected file.</h3>
            <a href="/">Upload another dataset</a>
            """, 400

        DATA["df"] = df
        DATA["col"] = col
        DATA["file"] = filename

        return page("""
        <div class="card">
            <h1>Customer Feedback Analysis</h1>
            <p class="subtitle">✅ Dataset Uploaded Successfully!</p>

            <div class="success">
                <b>File:</b> {{ filename }}<br>
                <b>Total reviews found:</b> {{ count }}<br>
                <b>Review column:</b> {{ col }}
            </div>

            <p class="subtitle">
                Your dataset is ready. Click below to analyze customer
                feedback.
            </p>

            <div class="center">
                <a href="/analyze" class="btn">📊 Analyze Feedback</a>
                <a href="/" class="btn">Upload Another Dataset</a>
            </div>
        </div>
        """, filename=filename, count=len(df), col=col)

    except Exception as e:
        return page("""
        <div class="card">
            <h1>Upload Error</h1>
            <p class="subtitle">{{ error }}</p>
            <div class="center"><a href="/" class="btn">Try Again</a></div>
        </div>
        """, error=str(e)), 400


@app.route("/analyze")
def analyze():
    df = DATA["df"]
    col = DATA["col"]
    filename = DATA["file"]

    if df is None:
        return redirect(url_for("home"))

    reviews = []
    counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}

    for i, value in enumerate(df[col], start=1):
        review = str(value).strip()
        if not review:
            continue

        sentiment = simple_sentiment(review)
        counts[sentiment] += 1

        reviews.append({
            "number": i,
            "review": review,
            "sentiment": sentiment
        })

    total = len(reviews)

    return page("""
    <div class="card">
        <h1>Customer Feedback Analysis</h1>
        <p class="subtitle">
            Sentiment Analysis Results of Your Uploaded Dataset<br>
            File: {{ filename }}
        </p>

        <div class="stats">
            <div class="stat total">
                <h2>{{ total }}</h2><p>TOTAL REVIEWS</p>
            </div>
            <div class="stat pos">
                <h2>{{ positive }}</h2><p>😊 POSITIVE</p>
            </div>
            <div class="stat neg">
                <h2>{{ negative }}</h2><p>😡 NEGATIVE</p>
            </div>
            <div class="stat neu">
                <h2>{{ neutral }}</h2><p>😐 NEUTRAL</p>
            </div>
        </div>

        <h3 class="section-title">📝 Customer Reviews</h3>

        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>No.</th>
                        <th>Customer Review</th>
                        <th>Sentiment</th>
                    </tr>
                </thead>
                <tbody>
                    {% for r in reviews %}
                    <tr>
                        <td>{{ r.number }}</td>
                        <td>{{ r.review }}</td>
                        <td>
                            {% if r.sentiment == 'POSITIVE' %}
                                <span style="color:#168844;font-weight:bold">
                                    😊 POSITIVE
                                </span>
                            {% elif r.sentiment == 'NEGATIVE' %}
                                <span style="color:#e32636;font-weight:bold">
                                    😡 NEGATIVE
                                </span>
                            {% else %}
                                <span style="color:#b88600;font-weight:bold">
                                    😐 NEUTRAL
                                </span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="center" style="margin-top:22px">
            <a href="/" class="btn">⬆ Upload New Dataset</a>
        </div>

        <div class="footer">
            Customer Feedback Analysis | Sentiment Analysis System
        </div>
    </div>
    """,
    filename=filename,
    total=total,
    positive=counts["POSITIVE"],
    negative=counts["NEGATIVE"],
    neutral=counts["NEUTRAL"],
    reviews=reviews)


if __name__ == "__main__":
    app.run(debug=True, port=10000)
