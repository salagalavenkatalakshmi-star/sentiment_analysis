
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Current uploaded dataset
DATA = {"df": None, "col": "", "file": ""}


def find_review_column(df):
    for col in df.columns:
        name = str(col).lower()
        if any(word in name for word in
               ["review", "feedback", "comment", "text"]):
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
    return render_template("index.html", page="home")


@app.route("/upload-page")
def upload_page():
    return render_template("index.html", page="upload")


@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")

        if not file or not file.filename:
            return redirect(url_for("upload_page"))

        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in {".csv", ".xlsx", ".xls", ".pdf"}:
            return "Unsupported file. Please upload CSV, Excel or PDF."

        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        if ext == ".csv":
            try:
                df = pd.read_csv(
                    path, encoding="utf-8-sig", on_bad_lines="skip"
                )
            except (UnicodeDecodeError, ValueError):
                df = pd.read_csv(
                    path, encoding="latin1", on_bad_lines="skip"
                )

        elif ext in {".xlsx", ".xls"}:
            df = pd.read_excel(path)

        else:
            try:
                import fitz
                with fitz.open(path) as doc:
                    text = "\n".join(p.get_text() for p in doc)
            except ImportError:
                from pypdf import PdfReader
                reader = PdfReader(path)
                text = "\n".join(
                    p.extract_text() or "" for p in reader.pages
                )

            lines = [
                line.strip().strip('"').strip("'")
                for line in text.splitlines()
                if len(line.strip()) > 5
                and line.strip().lower() not in {
                    "review", "customer review", "feedback"
                }
            ]
            df = pd.DataFrame({"review": lines})

        if df.empty or len(df.columns) == 0:
            return "No readable data found. Please try another file."

        df.columns = [str(c).strip() for c in df.columns]
        col = find_review_column(df)

        df = df.head(1000).dropna(subset=[col]).copy()
        df[col] = df[col].astype(str).str.strip()
        df = df[df[col] != ""].reset_index(drop=True)

        if df.empty:
            return "No customer reviews found. Please upload another dataset."

        DATA.update({
            "df": df,
            "col": col,
            "file": filename
        })

        return redirect(url_for("analyze"))

    except Exception:
        return (
            "Could not read this file. Check the file format and try again. "
            "<a href='/upload-page'>Back</a>"
        ), 400


@app.route("/analyze")
def analyze():
    df = DATA["df"]
    col = DATA["col"]

    if df is None:
        return redirect(url_for("upload_page"))

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

    def percentage(count):
        return round(count * 100 / total, 2) if total else 0

    return render_template(
        "index.html",
        page="results",
        filename=DATA["file"],
        total=total,
        positive=counts["POSITIVE"],
        negative=counts["NEGATIVE"],
        neutral=counts["NEUTRAL"],
        pp=percentage(counts["POSITIVE"]),
        np=percentage(counts["NEGATIVE"]),
        up=percentage(counts["NEUTRAL"]),
        reviews=reviews
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
