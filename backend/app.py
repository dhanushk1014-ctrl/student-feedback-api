from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import joblib


app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "my-secret-key"

jwt = JWTManager(app)
# Load ML model
model = joblib.load("sentiment_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")


# ================= DATABASE =================

def get_db():

    conn = sqlite3.connect("feedback.db")
    conn.row_factory = sqlite3.Row

    return conn


def create_tables():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ================= REGISTER =================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    # Check request body
    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    username = data.get("username")
    password = data.get("password")


    # Check empty values
    if not username or not password:

        return jsonify({
            "error": "Username and password are required"
        }), 400


    # Remove extra spaces
    username = username.strip()


    # Username validation
    if len(username) < 3:

        return jsonify({
            "error": "Username must be at least 3 characters"
        }), 400


    if len(username) > 20:

        return jsonify({
            "error": "Username must be less than 20 characters"
        }), 400


    # Password validation
    if len(password) < 4:

        return jsonify({
            "error": "Password must be at least 4 characters"
        }), 400


    # Hash password
    hashed_password = generate_password_hash(password)


    conn = get_db()


    try:

        conn.execute(
            """
            INSERT INTO users (username, password)
            VALUES (?, ?)
            """,
            (username, hashed_password)
        )

        conn.commit()


    except sqlite3.IntegrityError:

        conn.close()

        return jsonify({
            "error": "Username already exists"
        }), 409


    conn.close()


    return jsonify({
        "message": "Registration successful!"
    }), 201


# ================= LOGIN =================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()


    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    username = data.get("username")
    password = data.get("password")


    if not username or not password:

        return jsonify({
            "error": "Username and password are required"
        }), 400


    username = username.strip()


    conn = get_db()

    user = conn.execute(
        """
        SELECT * FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()


    # User doesn't exist
    if not user:

        return jsonify({
            "error": "Invalid username or password"
        }), 401


    # Wrong password
    if not check_password_hash(
        user["password"],
        password
    ):

        return jsonify({
            "error": "Invalid username or password"
        }), 401


    # Create JWT
    token = create_access_token(
        identity=username
    )


    return jsonify({
        "message": "Login successful!",
        "token": token
    }), 200


# ================= ADD FEEDBACK =================

@app.route("/api/feedback", methods=["POST"])
@jwt_required()
def add_feedback():

    data = request.get_json()


    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    name = data.get("name")
    message = data.get("message")


    # Empty validation
    if not name or not message:

        return jsonify({
            "error": "Name and message are required"
        }), 400


    name = name.strip()
    message = message.strip()


    # Name validation
    if len(name) < 2:

        return jsonify({
            "error": "Name must be at least 2 characters"
        }), 400


    if len(name) > 50:

        return jsonify({
            "error": "Name must be less than 50 characters"
        }), 400


    # Feedback validation
    if len(message) < 5:

        return jsonify({
            "error": "Feedback must be at least 5 characters"
        }), 400


    if len(message) > 500:

        return jsonify({
            "error": "Feedback must be less than 500 characters"
        }), 400


    conn = get_db()


    conn.execute(
        """
        INSERT INTO feedback (name, message)
        VALUES (?, ?)
        """,
        (name, message)
    )


    conn.commit()
    conn.close()


    return jsonify({
        "message": "Feedback created successfully!"
    }), 201


# ================= GET FEEDBACK =================

@app.route("/api/feedback", methods=["GET"])
@jwt_required()
def get_feedback():

    username = get_jwt_identity()


    conn = get_db()


    rows = conn.execute(
        """
        SELECT * FROM feedback
        """
    ).fetchall()


    conn.close()


    feedback_list = []


    for row in rows:

        feedback_list.append({

            "id": row["id"],

            "name": row["name"],

            "message": row["message"]

        })


    return jsonify({

        "user": username,

        "feedback": feedback_list

    }), 200


# ================= UPDATE FEEDBACK =================

@app.route("/api/feedback/<int:id>", methods=["PUT"])
@jwt_required()
def update_feedback(id):

    data = request.get_json()


    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    name = data.get("name")
    message = data.get("message")


    if not name or not message:

        return jsonify({
            "error": "Name and message are required"
        }), 400


    name = name.strip()
    message = message.strip()


    if len(name) < 2:

        return jsonify({
            "error": "Name must be at least 2 characters"
        }), 400


    if len(name) > 50:

        return jsonify({
            "error": "Name must be less than 50 characters"
        }), 400


    if len(message) < 5:

        return jsonify({
            "error": "Feedback must be at least 5 characters"
        }), 400


    if len(message) > 500:

        return jsonify({
            "error": "Feedback must be less than 500 characters"
        }), 400


    conn = get_db()


    existing = conn.execute(
        """
        SELECT * FROM feedback
        WHERE id = ?
        """,
        (id,)
    ).fetchone()


    if not existing:

        conn.close()

        return jsonify({
            "error": "Feedback not found"
        }), 404


    conn.execute(
        """
        UPDATE feedback
        SET name = ?, message = ?
        WHERE id = ?
        """,
        (name, message, id)
    )


    conn.commit()
    conn.close()


    return jsonify({
        "message": "Feedback updated successfully!"
    }), 200


# ================= DELETE FEEDBACK =================

@app.route("/api/feedback/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_feedback(id):

    conn = get_db()


    existing = conn.execute(
        """
        SELECT * FROM feedback
        WHERE id = ?
        """,
        (id,)
    ).fetchone()


    if not existing:

        conn.close()

        return jsonify({
            "error": "Feedback not found"
        }), 404


    conn.execute(
        """
        DELETE FROM feedback
        WHERE id = ?
        """,
        (id,)
    )


    conn.commit()
    conn.close()


    return jsonify({
        "message": "Feedback deleted successfully!"
    }), 200


# ================= START SERVER =================
# ================= ML PREDICTION =================

@app.route("/api/predict", methods=["POST"])
@jwt_required()
def predict():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    text = data.get("text")

    if not text:
        return jsonify({
            "error": "Text is required"
        }), 400

    text = text.strip()

    if len(text) < 2:
        return jsonify({
            "error": "Text must contain at least 2 characters"
        }), 400

    # Convert text into numbers
    text_vector = vectorizer.transform([text])

    # Make prediction
    prediction = model.predict(text_vector)[0]

    return jsonify({
        "text": text,
        "prediction": prediction
    }), 200
if __name__ == "__main__":

    create_tables()

    app.run(debug=True)