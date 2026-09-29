print("================================")
print("       REVIEW SENSE")
print("   SENTIMENT ANALYSIS")
print("================================")

feedback = input("Enter your review: ").strip()
text = feedback.lower()

# Negative phrases
negative_phrases = [
    "not good",
    "not nice",
    "not useful",
    "not worth",
    "not satisfied",
    "very bad",
    "worst",
    "poor quality",
    "terrible",
    "disappointed",
    "useless"
]

# Positive phrases
positive_phrases = [
    "very good",
    "really good",
    "excellent",
    "amazing",
    "awesome",
    "very nice",
    "good quality",
    "high quality",
    "best",
    "wonderful",
    "satisfied"
]

negative_count = 0
positive_count = 0

# Check negative phrases first
for phrase in negative_phrases:
    if phrase in text:
        negative_count += 1

# Check positive phrases
for phrase in positive_phrases:
    if phrase in text:
        positive_count += 1

print("\nYour Review:", feedback)

if negative_count > positive_count:
    print("Sentiment: NEGATIVE")
elif positive_count > negative_count:
    print("Sentiment: POSITIVE")
else:
    print("Sentiment: NEUTRAL")

print("================================")