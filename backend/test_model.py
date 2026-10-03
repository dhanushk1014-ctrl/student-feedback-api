import joblib


# Load model
model = joblib.load("sentiment_model.pkl")

# Load vectorizer
vectorizer = joblib.load("vectorizer.pkl")


# Test sentence
text = ["This application is very bad"]


# Convert text to numbers
text_vector = vectorizer.transform(text)


# Predict
prediction = model.predict(text_vector)


print("Prediction:", prediction[0])