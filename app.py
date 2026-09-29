from flask import Flask, render_template, request
import pandas as pd
import os
from analysis import analyze_sentiment

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_review_col(df):
    for c in df.columns:
        if 'review' in c.lower() or 'text' in c.lower() or 'comment' in c.lower():
            return c
    return df.columns[0]

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None

    if request.method == 'POST':
        # 1. FILE UPLOAD - Mobile lo 100% work
        file = request.files.get('file')
        text_input = request.form.get('review_text', '').strip()

        if file and file.filename!= '':
            try:
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)

                if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
                    df = pd.read_excel(filepath)
                else:
                    df = pd.read_csv(filepath)

                col = get_review_col(df)
                # AUTOMATIC ANALYSIS
                data = []
                for _, row in df.iterrows():
                    review = str(row[col])
                    sentiment, score = analyze_sentiment(review)
                    data.append({'review': review, 'Sentiment': sentiment, 'Score': score})

                results = data

            except Exception as e:
                error = f"File Error: {e}. CSV lo first column lo reviews undali"

        # 2. TEXT INPUT
        elif text_input:
            sentiment, score = analyze_sentiment(text_input)
            results = [{'review': text_input, 'Sentiment': sentiment, 'Score': score}]

    return render_template('index.html', results=results, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
