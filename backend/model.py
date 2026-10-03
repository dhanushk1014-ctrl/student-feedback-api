from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib


# ---------------- TRAINING DATA ----------------

texts = [
    "This application is very good",
    "I really like this application",
    "Excellent application",
    "Very useful and easy to use",
    "I am happy with this application",
    "The application works perfectly",
    "Very nice experience",

    "This application is bad",
    "I don't like this application",
    "Very poor application",
    "This is difficult to use",
    "I am disappointed",
    "The application is not useful",
    "Very bad experience"
]


labels = [
    "positive",
    "positive",
    "positive",
    "positive",
    "positive",
    "positive",
    "positive",

    "negative",
    "negative",
    "negative",
    "negative",
    "negative",
    "negative",
    "negative"
]


# ---------------- CONVERT TEXT TO NUMBERS ----------------

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(texts)


# ---------------- TRAIN ML MODEL ----------------

model = LogisticRegression()

model.fit(X, labels)


# ---------------- SAVE MODEL ----------------

joblib.dump(model, "sentiment_model.pkl")

joblib.dump(vectorizer, "vectorizer.pkl")


print("ML model trained successfully!")
print("Model saved as sentiment_model.pkl")
print("Vectorizer saved as vectorizer.pkl")