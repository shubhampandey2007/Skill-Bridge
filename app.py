from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
CORS(app)


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("skillsetu.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Profiles table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            education TEXT,
            interest TEXT,
            level TEXT,
            skills TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():

    return jsonify({
        "message": "SkillSetu backend is running"
    })


# ---------------- SIGN UP ----------------

@app.route("/signup", methods=["POST"])
def signup():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:

        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    hashed_password = generate_password_hash(password)

    conn = get_db()

    try:

        conn.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, hashed_password))

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Email already registered"
        }), 409

    conn.close()

    return jsonify({
        "success": True,
        "message": "Account created successfully"
    })


# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    conn = get_db()

    user = conn.execute("""
        SELECT * FROM users
        WHERE email = ?
    """, (email,)).fetchone()

    conn.close()

    if user is None:

        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(user["password"], password):

        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    })


# ---------------- SAVE PROFILE ----------------

@app.route("/profile", methods=["POST"])
def save_profile():

    data = request.json

    user_id = data.get("user_id")
    education = data.get("education")
    interest = data.get("interest")
    level = data.get("level")
    skills = data.get("skills")

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User ID is required"
        }), 400

    conn = get_db()

    # Check that user exists
    user = conn.execute("""
        SELECT id FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    if user is None:

        conn.close()

        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # Insert or update profile
    conn.execute("""
        INSERT INTO profiles
        (user_id, education, interest, level, skills)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            education = excluded.education,
            interest = excluded.interest,
            level = excluded.level,
            skills = excluded.skills
    """, (
        user_id,
        education,
        interest,
        level,
        skills
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Profile saved successfully"
    })


# ---------------- GET PROFILE ----------------

@app.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):

    conn = get_db()

    profile = conn.execute("""
        SELECT
            users.name,
            users.email,
            profiles.education,
            profiles.interest,
            profiles.level,
            profiles.skills
        FROM users
        LEFT JOIN profiles
        ON users.id = profiles.user_id
        WHERE users.id = ?
    """, (user_id,)).fetchone()

    conn.close()

    if profile is None:

        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "profile": dict(profile)
    })


# ---------------- EVALUATION ----------------

# ---------------- EVALUATION ----------------

@app.route("/evaluate", methods=["POST"])
def evaluate():

    data = request.json
    answers = data.get("answers", [])

    keywords = [
        ["animal", "mammal", "feline", "pet", "domestic"],
        ["store", "value", "data", "memory", "change", "container"],
        ["raw", "processed", "meaning", "context", "data", "information"]
    ]

    scores = []

    for i, answer in enumerate(answers):

        answer_text = answer.get("answer", "").lower()

        matched = 0

        for word in keywords[i]:
            if word in answer_text:
                matched += 1

        score = min(matched * 20, 100)

        if len(answer_text) >= 30:
            score = min(score + 10, 100)

        scores.append(score)

    overall_score = sum(scores) // len(scores) if scores else 0

    if overall_score >= 80:
        readiness = "HIGH"
    elif overall_score >= 60:
        readiness = "MODERATE"
    else:
        readiness = "DEVELOPING"

    return jsonify({
        "success": True,
        "scores": scores,
        "overall_score": overall_score,
        "readiness": readiness
    })

# ---------------- START SERVER ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)