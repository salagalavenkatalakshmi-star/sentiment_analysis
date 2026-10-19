
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA = {"df": None, "col": "", "file": ""}


def find_review_column(df):
    for col in df.columns:
        if any(word in str(col).lower()
               for word in ["review", "feedback", "comment", "text"]):
            return col
    return df.columns[0]


def simple_sentiment(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    words = text.split()

    positive = {
        "love", "great", "excellent", "amazing", "good",
        "best", "awesome", "perfect", "nice", "wonderful",
        "happy", "fantastic", "satisfied", "recommend",
        "beautiful", "useful", "comfortable", "fast", "helpful"
    }

    negative = {
        "bad", "worst", "terrible", "awful", "hate", "poor",
        "horrible", "disappointed", "waste", "boring", "useless",
        "broken", "slow", "expensive", "problem", "defective",
        "dirty", "damage", "damaged"
    }

    negations = {
        "not", "never", "no", "hardly", "isn't", "wasn't",
        "don't", "doesn't", "didn't"
    }

    p = n = 0

    for i, word in enumerate(words):
        negated = any(
            w in negations for w in words[max(0, i - 3):i]
        )

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


@app.route("/")
def home():
    return render_template(
        "index.html", uploaded=False, analyzed=False
    )


@app.route("/upload-page")
def upload_page():
    return redirect(url_for("home"))


@app.route("/upload", methods=["POST"])
def upload():
    try:
        f = request.files.get("file")

        if not f or not f.filename:
            return "Please select a dataset. <a href='/'>Go back</a>", 400

        filename = secure_filename(f.filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in {".csv", ".xlsx", ".xls", ".pdf"}:
            return "Upload a CSV, Excel or PDF file. <a href='/'>Go back</a>", 400

        path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path)

        if ext == ".csv":
            try:
                df = pd.read_csv(path, encoding="utf-8-sig",
                                 on_bad_lines="skip")
            except (UnicodeDecodeError, ValueError):
                df = pd.read_csv(path, encoding="latin1",
                                 on_bad_lines="skip")

        elif ext in {".xlsx", ".xls"}:
            df = pd.read_excel(path)

        else:
            try:
                import fitz
                with fitz.open(path) as doc:
                    text = "\n".join(page.get_text() for page in doc)
            except ImportError:
                from pypdf import PdfReader
                reader = PdfReader(path)
                text = "\n".join(
                    page.extract_text() or "" for page in reader.pages
                )

            lines = [
                line.strip().strip('"').strip("'")
                for line in text.splitlines()
                if line.strip() and len(line.strip()) > 5
            ]
            df = pd.DataFrame({"review": lines})

        if df.empty or len(df.columns) == 0:
            return "No readable data found. <a href='/'>Try again</a>", 400

        df.columns = [str(c).strip() for c in df.columns]
        col = find_review_column(df)

        df = df.head(1000).dropna(subset=[col]).copy()
        df[col] = df[col].astype(str).str.strip()
        df = df[df[col] != ""].reset_index(drop=True)

        if df.empty:
            return "No reviews found. <a href='/'>Upload another file</a>", 400

        DATA.update({"df": df, "col": col, "file": filename})

        return render_template(
            "index.html",
            uploaded=True,
            analyzed=False,
            filename=filename,
            count=len(df),
            col=col
        )

    except Exception:
        return (
            "Unable to read this file. Check its format and try again. "
            "<a href='/'>Back to Welcome</a>",
            400
        )


@app.route("/analyze")
def analyze():
    df = DATA["df"]
    col = DATA["col"]

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

    return render_template(
        "index.html",
        uploaded=True,
        analyzed=True,
        filename=DATA["file"],
        total=len(reviews),
        positive=counts["POSITIVE"],
        negative=counts["NEGATIVE"],
        neutral=counts["NEUTRAL"],
        reviews=reviews
    )


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 10000)))
