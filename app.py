from flask import Flask, render_template, request, session
import pandas as pd
import os
from analysis import analyze_sentiment

app = Flask(__name__)
app.secret_key = "reviewsense_secret_123"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_review_column(df):
    for col in df.columns:
        if any(x in col.lower() for x in ['review','text','comment','feedback','message','content']):
            return col
    return df.columns[0]

@app.route('/')
def index():
    return render_template('index.html', uploaded=False, analyzed=False)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('dataset')
    if not file:
        return render_template('index.html', uploaded=False, analyzed=False)
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    session['filepath'] = filepath
    session['filename'] = file.filename
    return render_template('index.html', uploaded=True, analyzed=False, filename=file.filename)

@app.route('/analyze', methods=['POST'])
def analyze():
    filepath = session.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return render_template('index.html', uploaded=False, analyzed=False)
    if filepath.endswith(('.xlsx','.xls')):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath, encoding='utf-8', errors='ignore', on_bad_lines='skip')

    review_col = get_review_column(df)
    reviews_data = []
    pos=neg=neu=0

    for i,row in df.iterrows():
        text = str(row[review_col]).strip()
        if not text or text.lower()=='nan': continue
        sentiment,score = analyze_sentiment(text)
        if sentiment.upper()=="POSITIVE": pos+=1
        elif sentiment.upper()=="NEGATIVE": neg+=1
        else: neu+=1
        reviews_data.append({'number':len(reviews_data)+1,'review':text,'sentiment':sentiment.upper(),'customer':"",'app':""})

    return render_template('index.html', uploaded=False, analyzed=True, reviews=reviews_data, total=len(reviews_data), positive=pos, negative=neg, neutral=neu)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
