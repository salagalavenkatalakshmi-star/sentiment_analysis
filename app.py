from flask import Flask, render_template, request
import pandas as pd
import os
import re

app = Flask(__name__)

# -------------------------------------------------
# UPLOAD FOLDER
# -------------------------------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -------------------------------------------------
# FIND COLUMN
# -------------------------------------------------
def find_column(df, names):

    for column in df.columns:

        column_name = str(column).strip().lower()

        for name in names:

            if name in column_name:
                return column

    return None


# -------------------------------------------------
# CLEAN TEXT
# -------------------------------------------------
def clean_text(text):

    text = str(text).lower()

    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -------------------------------------------------
# SENTIMENT WORDS
# -------------------------------------------------
positive_words = {
    "good",
    "great",
    "excellent",
    "amazing",
    "awesome",
    "love",
    "loved",
    "nice",
    "best",
    "perfect",
    "happy",
    "satisfied",
    "fast",
    "beautiful",
    "fantastic",
    "wonderful",
    "quality",
    "worth"
}

negative_words = {
    "bad",
    "worst",
    "poor",
    "terrible",
    "awful",
    "hate",
    "hated",
    "late",
    "broken",
    "damage",
    "damaged",
    "waste",
    "disappointed",
    "problem",
    "slow",
    "useless",
    "poorly",
    "stopped",
    "refund",
    "defective",
    "overheats",
    "crashes"
}


# -------------------------------------------------
# SENTIMENT ANALYSIS
# -------------------------------------------------
def analyze_sentiment(review):

    text = clean_text(review)

    words = text.split()

    positive_score = 0
    negative_score = 0

    for word in words:

        if word in positive_words:
            positive_score += 1

        if word in negative_words:
            negative_score += 1

    if positive_score > negative_score:

        return "POSITIVE"

    elif negative_score > positive_score:

        return "NEGATIVE"

    return "NEUTRAL"


# -------------------------------------------------
# HOME
# -------------------------------------------------
@app.route("/")
def home():

    return render_template(
        "index.html",
        uploaded=False,
        analyzed=False,
        reviews=[],
        total=0,
        positive=0,
        negative=0,
        neutral=0,
        accuracy=0,
        filename=""
    )


# -------------------------------------------------
# UPLOAD DATASET
# -------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("dataset")

    if not file or file.filename == "":

        return render_template(
            "index.html",
            uploaded=False,
            analyzed=False,
            reviews=[],
            total=0,
            positive=0,
            negative=0,
            neutral=0,
            accuracy=0,
            filename="",
            error="Please select a CSV dataset."
        )

    if not file.filename.lower().endswith(".csv"):

        return render_template(
            "index.html",
            uploaded=False,
            analyzed=False,
            reviews=[],
            total=0,
            positive=0,
            negative=0,
            neutral=0,
            accuracy=0,
            filename="",
            error="Please upload only CSV files."
        )

    # Remove old CSV files
    for filename in os.listdir(UPLOAD_FOLDER):

        if filename.lower().endswith(".csv"):

            os.remove(
                os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )
            )

    # Save new CSV
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(file_path)

    return render_template(
        "index.html",
        uploaded=True,
        analyzed=False,
        filename=file.filename,
        reviews=[],
        total=0,
        positive=0,
        negative=0,
        neutral=0,
        accuracy=0
    )


# -------------------------------------------------
# ANALYZE DATASET
# -------------------------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    csv_files = [
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith(".csv")
    ]

    if not csv_files:

        return render_template(
            "index.html",
            uploaded=False,
            analyzed=False,
            reviews=[],
            total=0,
            positive=0,
            negative=0,
            neutral=0,
            accuracy=0,
            error="Please upload a CSV dataset first."
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        csv_files[0]
    )

    # Read CSV
    try:

        df = pd.read_csv(file_path)

    except Exception as e:

        return render_template(
            "index.html",
            uploaded=True,
            analyzed=False,
            reviews=[],
            total=0,
            positive=0,
            negative=0,
            neutral=0,
            accuracy=0,
            filename=csv_files[0],
            error="Unable to read the CSV file."
        )

    # -------------------------------------------------
    # FIND COLUMNS
    # -------------------------------------------------

    review_column = find_column(
        df,
        [
            "review",
            "reviews",
            "feedback",
            "comment",
            "text"
        ]
    )

    customer_column = find_column(
        df,
        [
            "customer",
            "customer_name",
            "user",
            "username",
            "name"
        ]
    )

    app_column = find_column(
        df,
        [
            "shopping_app",
            "app",
            "platform",
            "website",
            "source",
            "window"
        ]
    )

    # IMPORTANT:
    # Find actual Sentiment column
    sentiment_column = find_column(
        df,
        [
            "sentiment",
            "label",
            "target",
            "class"
        ]
    )

    # -------------------------------------------------
    # CHECK REVIEW COLUMN
    # -------------------------------------------------

    if review_column is None:

        return render_template(
            "index.html",
            uploaded=True,
            analyzed=False,
            reviews=[],
            total=0,
            positive=0,
            negative=0,
            neutral=0,
            accuracy=0,
            filename=csv_files[0],
            error=(
                "Review column not found. "
                "Your CSV should contain Review, "
                "Feedback, Comment or Text column."
            )
        )

    # Remove empty reviews
    df = df.dropna(
        subset=[review_column]
    )

    reviews = []

    positive_count = 0
    negative_count = 0
    neutral_count = 0

    # -------------------------------------------------
    # ACCURACY VARIABLES
    # -------------------------------------------------

    correct_predictions = 0
    labeled_reviews = 0

    # -------------------------------------------------
    # ANALYZE ALL REVIEWS
    # -------------------------------------------------

    for index, row in df.iterrows():

        review_text = str(
            row[review_column]
        ).strip()

        if not review_text:

            continue

        # Predict sentiment
        predicted_sentiment = analyze_sentiment(
            review_text
        )

        # Count sentiment
        if predicted_sentiment == "POSITIVE":

            positive_count += 1

        elif predicted_sentiment == "NEGATIVE":

            negative_count += 1

        else:

            neutral_count += 1

        # -------------------------------------------------
        # ACCURACY CALCULATION
        # -------------------------------------------------

        if sentiment_column is not None:

            actual_sentiment = str(
                row[sentiment_column]
            ).strip().upper()

            # Convert possible variations
            if actual_sentiment in [
                "POSITIVE",
                "POS",
                "1"
            ]:

                actual_sentiment = "POSITIVE"

            elif actual_sentiment in [
                "NEGATIVE",
                "NEG",
                "0"
            ]:

                actual_sentiment = "NEGATIVE"

            elif actual_sentiment in [
                "NEUTRAL",
                "NEU"
            ]:

                actual_sentiment = "NEUTRAL"

            # Compare prediction with actual label
            if actual_sentiment in [
                "POSITIVE",
                "NEGATIVE",
                "NEUTRAL"
            ]:

                labeled_reviews += 1

                if predicted_sentiment == actual_sentiment:

                    correct_predictions += 1

        # -------------------------------------------------
        # CUSTOMER
        # -------------------------------------------------

        customer = ""

        if customer_column:

            customer = str(
                row[customer_column]
            )

        # -------------------------------------------------
        # SHOPPING APP
        # -------------------------------------------------

        shopping_app = ""

        if app_column:

            shopping_app = str(
                row[app_column]
            )

        # -------------------------------------------------
        # ADD REVIEW
        # -------------------------------------------------

        reviews.append({

            "number": len(reviews) + 1,

            "customer": customer,

            "app": shopping_app,

            "review": review_text,

            "sentiment": predicted_sentiment

        })

    # -------------------------------------------------
    # CALCULATE ACCURACY
    # -------------------------------------------------

    if labeled_reviews > 0:

        accuracy = round(
            (correct_predictions / labeled_reviews) * 100,
            2
        )

    else:

        accuracy = 0

    # -------------------------------------------------
    # PRINT ACCURACY IN TERMINAL
    # -------------------------------------------------

    print("-----------------------------------")

    print(
        "Total Reviews:",
        len(reviews)
    )

    print(
        "Positive:",
        positive_count
    )

    print(
        "Negative:",
        negative_count
    )

    print(
        "Neutral:",
        neutral_count
    )

    print(
        "Correct Predictions:",
        correct_predictions
    )

    print(
        "Labeled Reviews:",
        labeled_reviews
    )

    print(
        "Accuracy:",
        str(accuracy) + "%"
    )

    print("-----------------------------------")

    # -------------------------------------------------
    # SHOW RESULT
    # -------------------------------------------------

    return render_template(
        "index.html",

        uploaded=True,

        analyzed=True,

        filename=csv_files[0],

        reviews=reviews,

        total=len(reviews),

        positive=positive_count,

        negative=negative_count,

        neutral=neutral_count,

        accuracy=accuracy
    )


# -------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------
if __name__ == "__main__":

    app.run(debug=True)