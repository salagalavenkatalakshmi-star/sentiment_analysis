def analyze_sentiment(feedback):
    if not feedback:
        return "NEUTRAL", 0.0

    text = str(feedback).lower().strip()

    negative_phrases = [
        "not good", "not nice", "not useful", "not worth",
        "not satisfied", "very bad", "worst", "poor quality",
        "terrible", "disappointed", "useless", "bad", "poor",
        "hate", "awful", "horrible", "waste", "boring"
    ]

    positive_phrases = [
        "very good", "really good", "excellent", "amazing",
        "awesome", "very nice", "good quality", "high quality",
        "best", "wonderful", "satisfied", "good", "great",
        "love", "perfect", "nice", "fantastic", "outstanding"
    ]

    negative_count = 0
    positive_count = 0

    for phrase in negative_phrases:
        if phrase in text:
            negative_count += 1

    for phrase in positive_phrases:
        if phrase in text:
            positive_count += 1

    if negative_count > positive_count:
        return "NEGATIVE", -0.6
    elif positive_count > negative_count:
        return "POSITIVE", 0.8
    else:
        return "NEUTRAL", 0.0
