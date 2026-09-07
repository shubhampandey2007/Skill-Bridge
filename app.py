from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
CORS(app)


# =====================================================
# DATABASE
# =====================================================

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


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "message": "SkillSetu backend is running"
    })


# =====================================================
# SIGN UP
# =====================================================

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
        """, (
            name,
            email,
            hashed_password
        ))

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


# =====================================================
# LOGIN
# =====================================================

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
        SELECT *
        FROM users
        WHERE email = ?
    """, (
        email,
    )).fetchone()

    conn.close()

    if user is None:

        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(
        user["password"],
        password
    ):

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


# =====================================================
# SAVE PROFILE
# =====================================================

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
        SELECT id
        FROM users
        WHERE id = ?
    """, (
        user_id,
    )).fetchone()

    if user is None:

        conn.close()

        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # Insert or update profile

    conn.execute("""
        INSERT INTO profiles
        (
            user_id,
            education,
            interest,
            level,
            skills
        )
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


# =====================================================
# GET PROFILE
# =====================================================

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
    """, (
        user_id,
    )).fetchone()

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


# =====================================================
# QUESTION BANK
# =====================================================

QUESTION_BANK = {

    # =================================================
    # ARTIFICIAL INTELLIGENCE / ML
    # =================================================

    "artificial intelligence / ml": {

        "beginner": [

            {
                "question":
                    "What is Machine Learning, and how is it different from traditional programming?",

                "keywords": [
                    "data",
                    "learn",
                    "pattern",
                    "model",
                    "algorithm"
                ],

                "skill":
                    "Machine Learning Fundamentals",

                "topic":
                    "Introduction to Machine Learning",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "What is the purpose of a training dataset in Machine Learning?",

                "keywords": [
                    "train",
                    "model",
                    "data",
                    "learn",
                    "pattern"
                ],

                "skill":
                    "Machine Learning Fundamentals",

                "topic":
                    "Training Data",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "What is the difference between supervised and unsupervised learning?",

                "keywords": [
                    "label",
                    "supervised",
                    "unsupervised",
                    "data",
                    "classification"
                ],

                "skill":
                    "Machine Learning Fundamentals",

                "topic":
                    "Learning Types",

                "difficulty":
                    "beginner"
            }

        ],


        "intermediate": [

            {
                "question":
                    "What is overfitting in Machine Learning, and how can you reduce it?",

                "keywords": [
                    "overfitting",
                    "training",
                    "validation",
                    "regularization",
                    "data"
                ],

                "skill":
                    "Model Training",

                "topic":
                    "Overfitting and Regularization",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "Explain the difference between classification and regression.",

                "keywords": [
                    "classification",
                    "regression",
                    "class",
                    "continuous",
                    "prediction"
                ],

                "skill":
                    "Machine Learning Algorithms",

                "topic":
                    "Classification vs Regression",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "Why is feature scaling useful when training some Machine Learning models?",

                "keywords": [
                    "scaling",
                    "feature",
                    "normalization",
                    "standardization",
                    "range"
                ],

                "skill":
                    "Data Preprocessing",

                "topic":
                    "Feature Scaling",

                "difficulty":
                    "intermediate"
            }

        ],


        "advanced": [

            {
                "question":
                    "Explain the bias-variance tradeoff and how it affects model performance.",

                "keywords": [
                    "bias",
                    "variance",
                    "overfitting",
                    "underfitting",
                    "generalization"
                ],

                "skill":
                    "Model Evaluation",

                "topic":
                    "Bias-Variance Tradeoff",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "How would you handle a highly imbalanced classification dataset?",

                "keywords": [
                    "imbalance",
                    "class",
                    "oversampling",
                    "undersampling",
                    "smote"
                ],

                "skill":
                    "Data Preprocessing",

                "topic":
                    "Imbalanced Datasets",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "How would you determine whether a Machine Learning model is actually generalizing well?",

                "keywords": [
                    "validation",
                    "test",
                    "generalization",
                    "cross",
                    "performance"
                ],

                "skill":
                    "Model Evaluation",

                "topic":
                    "Model Generalization",

                "difficulty":
                    "advanced"
            }

        ]

    },


    # =================================================
    # SOFTWARE DEVELOPMENT
    # =================================================

    "software development": {

        "beginner": [

            {
                "question":
                    "What is the purpose of a function in programming?",

                "keywords": [
                    "function",
                    "code",
                    "reuse",
                    "task",
                    "parameter"
                ],

                "skill":
                    "Programming Fundamentals",

                "topic":
                    "Functions",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "What is the difference between a variable and a constant?",

                "keywords": [
                    "variable",
                    "constant",
                    "value",
                    "change",
                    "memory"
                ],

                "skill":
                    "Programming Fundamentals",

                "topic":
                    "Variables and Constants",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "What is an algorithm?",

                "keywords": [
                    "algorithm",
                    "steps",
                    "problem",
                    "solution",
                    "procedure"
                ],

                "skill":
                    "Problem Solving",

                "topic":
                    "Algorithms",

                "difficulty":
                    "beginner"
            }

        ],


        "intermediate": [

            {
                "question":
                    "What is Object-Oriented Programming and why is it useful?",

                "keywords": [
                    "object",
                    "class",
                    "encapsulation",
                    "inheritance",
                    "code"
                ],

                "skill":
                    "Object-Oriented Programming",

                "topic":
                    "OOP Fundamentals",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "What is the purpose of version control systems such as Git?",

                "keywords": [
                    "git",
                    "version",
                    "control",
                    "repository",
                    "changes"
                ],

                "skill":
                    "Software Development Practices",

                "topic":
                    "Version Control",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "What is the difference between an API and a database?",

                "keywords": [
                    "api",
                    "database",
                    "data",
                    "request",
                    "server"
                ],

                "skill":
                    "Backend Development",

                "topic":
                    "APIs and Databases",

                "difficulty":
                    "intermediate"
            }

        ],


        "advanced": [

            {
                "question":
                    "How would you design a scalable backend for an application with millions of users?",

                "keywords": [
                    "scaling",
                    "database",
                    "server",
                    "cache",
                    "load"
                ],

                "skill":
                    "System Design",

                "topic":
                    "Scalable Backend Architecture",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "What are the main benefits of using a modular software architecture?",

                "keywords": [
                    "modular",
                    "maintenance",
                    "component",
                    "coupling",
                    "reuse"
                ],

                "skill":
                    "Software Architecture",

                "topic":
                    "Modular Architecture",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "How would you identify and resolve a performance bottleneck in a production application?",

                "keywords": [
                    "profiling",
                    "performance",
                    "bottleneck",
                    "database",
                    "optimization"
                ],

                "skill":
                    "Performance Optimization",

                "topic":
                    "Performance Bottlenecks",

                "difficulty":
                    "advanced"
            }

        ]

    },


    # =================================================
    # DATA SCIENCE / ANALYTICS
    # =================================================

    "data science / analytics": {

        "beginner": [

            {
                "question":
                    "What is the difference between data and information?",

                "keywords": [
                    "data",
                    "information",
                    "meaning",
                    "context",
                    "processed"
                ],

                "skill":
                    "Data Fundamentals",

                "topic":
                    "Data vs Information",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "What is the purpose of data visualization?",

                "keywords": [
                    "visualization",
                    "data",
                    "graph",
                    "pattern",
                    "insight"
                ],

                "skill":
                    "Data Analysis",

                "topic":
                    "Data Visualization",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "What is an average, and when can it be misleading?",

                "keywords": [
                    "average",
                    "mean",
                    "outlier",
                    "data",
                    "distribution"
                ],

                "skill":
                    "Statistics",

                "topic":
                    "Mean and Outliers",

                "difficulty":
                    "beginner"
            }

        ],


        "intermediate": [

            {
                "question":
                    "What is the difference between correlation and causation?",

                "keywords": [
                    "correlation",
                    "causation",
                    "relationship",
                    "cause",
                    "variable"
                ],

                "skill":
                    "Statistics",

                "topic":
                    "Correlation vs Causation",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "How would you handle missing values in a dataset?",

                "keywords": [
                    "missing",
                    "values",
                    "remove",
                    "impute",
                    "data"
                ],

                "skill":
                    "Data Preprocessing",

                "topic":
                    "Missing Data",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "What is the purpose of exploratory data analysis?",

                "keywords":
                    [
                        "exploration",
                        "data",
                        "pattern",
                        "outlier",
                        "analysis"
                    ],

                "skill":
                    "Data Analysis",

                "topic":
                    "Exploratory Data Analysis",

                "difficulty":
                    "intermediate"
            }

        ],


        "advanced": [

            {
                "question":
                    "How would you detect and handle outliers in a large dataset?",

                "keywords": [
                    "outlier",
                    "iqr",
                    "z",
                    "distribution",
                    "data"
                ],

                "skill":
                    "Statistical Analysis",

                "topic":
                    "Outlier Detection",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "How would you determine whether a statistical result is significant?",

                "keywords": [
                    "significance",
                    "p-value",
                    "hypothesis",
                    "null",
                    "test"
                ],

                "skill":
                    "Statistics",

                "topic":
                    "Statistical Significance",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "How would you prevent data leakage when building a predictive model?",

                "keywords": [
                    "leakage",
                    "training",
                    "test",
                    "validation",
                    "data"
                ],

                "skill":
                    "Machine Learning for Data Science",

                "topic":
                    "Data Leakage",

                "difficulty":
                    "advanced"
            }

        ]

    },


    # =================================================
    # CYBERSECURITY
    # =================================================

    "cybersecurity": {

        "beginner": [

            {
                "question":
                    "What is phishing and how can a user identify a phishing attempt?",

                "keywords": [
                    "phishing",
                    "email",
                    "link",
                    "password",
                    "fake"
                ],

                "skill":
                    "Cybersecurity Fundamentals",

                "topic":
                    "Phishing",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "What is the purpose of a firewall?",

                "keywords": [
                    "firewall",
                    "network",
                    "traffic",
                    "security",
                    "block"
                ],

                "skill":
                    "Network Security",

                "topic":
                    "Firewalls",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "Why are strong passwords important?",

                "keywords": [
                    "password",
                    "security",
                    "attack",
                    "guess",
                    "authentication"
                ],

                "skill":
                    "Cybersecurity Fundamentals",

                "topic":
                    "Password Security",

                "difficulty":
                    "beginner"
            }

        ],


        "intermediate": [

            {
                "question":
                    "What is the difference between authentication and authorization?",

                "keywords": [
                    "authentication",
                    "authorization",
                    "identity",
                    "permission",
                    "access"
                ],

                "skill":
                    "Access Control",

                "topic":
                    "Authentication vs Authorization",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "What is SQL injection and how can applications prevent it?",

                "keywords": [
                    "sql",
                    "injection",
                    "query",
                    "parameter",
                    "database"
                ],

                "skill":
                    "Application Security",

                "topic":
                    "SQL Injection",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "What is encryption and why is it important for secure communication?",

                "keywords": [
                    "encryption",
                    "key",
                    "data",
                    "secure",
                    "communication"
                ],

                "skill":
                    "Cryptography",

                "topic":
                    "Encryption",

                "difficulty":
                    "intermediate"
            }

        ],


        "advanced": [

            {
                "question":
                    "How would you design a defense strategy for a large organization's network?",

                "keywords": [
                    "network",
                    "firewall",
                    "monitoring",
                    "authentication",
                    "security"
                ],

                "skill":
                    "Network Security",

                "topic":
                    "Enterprise Network Defense",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "What is a zero-day vulnerability and why is it difficult to defend against?",

                "keywords": [
                    "zero-day",
                    "vulnerability",
                    "patch",
                    "attack",
                    "security"
                ],

                "skill":
                    "Vulnerability Management",

                "topic":
                    "Zero-Day Vulnerabilities",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "How would you investigate a suspected security breach?",

                "keywords": [
                    "logs",
                    "incident",
                    "forensics",
                    "network",
                    "evidence"
                ],

                "skill":
                    "Incident Response",

                "topic":
                    "Security Breach Investigation",

                "difficulty":
                    "advanced"
            }

        ]

    },


    # =================================================
    # WEB DEVELOPMENT
    # =================================================

    "web development": {

        "beginner": [

            {
                "question":
                    "What is HTML and what is its role in a website?",

                "keywords": [
                    "html",
                    "structure",
                    "web",
                    "page",
                    "elements"
                ],

                "skill":
                    "Frontend Fundamentals",

                "topic":
                    "HTML",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "What is CSS used for?",

                "keywords": [
                    "css",
                    "style",
                    "design",
                    "layout",
                    "appearance"
                ],

                "skill":
                    "Frontend Fundamentals",

                "topic":
                    "CSS",

                "difficulty":
                    "beginner"
            },

            {
                "question":
                    "What is JavaScript used for in a website?",

                "keywords": [
                    "javascript",
                    "interactive",
                    "logic",
                    "browser",
                    "dynamic"
                ],

                "skill":
                    "Frontend Fundamentals",

                "topic":
                    "JavaScript",

                "difficulty":
                    "beginner"
            }

        ],


        "intermediate": [

            {
                "question":
                    "What is the difference between frontend and backend development?",

                "keywords": [
                    "frontend",
                    "backend",
                    "server",
                    "client",
                    "interface"
                ],

                "skill":
                    "Web Architecture",

                "topic":
                    "Frontend vs Backend",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "What is an HTTP request and response?",

                "keywords": [
                    "http",
                    "request",
                    "response",
                    "server",
                    "client"
                ],

                "skill":
                    "Web Fundamentals",

                "topic":
                    "HTTP",

                "difficulty":
                    "intermediate"
            },

            {
                "question":
                    "What is a REST API?",

                "keywords": [
                    "rest",
                    "api",
                    "http",
                    "request",
                    "endpoint"
                ],

                "skill":
                    "Backend Development",

                "topic":
                    "REST APIs",

                "difficulty":
                    "intermediate"
            }

        ],


        "advanced": [

            {
                "question":
                    "How would you improve the performance of a web application?",

                "keywords": [
                    "performance",
                    "cache",
                    "database",
                    "optimization",
                    "loading"
                ],

                "skill":
                    "Web Performance",

                "topic":
                    "Performance Optimization",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "How would you secure a web application against common attacks?",

                "keywords": [
                    "security",
                    "authentication",
                    "validation",
                    "xss",
                    "sql"
                ],

                "skill":
                    "Web Security",

                "topic":
                    "Web Application Security",

                "difficulty":
                    "advanced"
            },

            {
                "question":
                    "How would you design a web application that can handle a large number of concurrent users?",

                "keywords": [
                    "scaling",
                    "server",
                    "database",
                    "cache",
                    "load"
                ],

                "skill":
                    "Web Architecture",

                "topic":
                    "Scalable Web Applications",

                "difficulty":
                    "advanced"
            }

        ]

    }

}


# =====================================================
# GET PERSONALIZED QUESTIONS
# =====================================================

@app.route("/questions/<int:user_id>", methods=["GET"])
def get_questions(user_id):

    conn = get_db()

    profile = conn.execute("""
        SELECT interest, level, skills
        FROM profiles
        WHERE user_id = ?
    """, (
        user_id,
    )).fetchone()

    conn.close()

    if profile is None:

        return jsonify({
            "success": False,
            "message": "Profile not found"
        }), 404


    interest = (
        profile["interest"] or ""
    ).strip().lower()

    level = (
        profile["level"] or "beginner"
    ).strip().lower()


    # ---------------- NORMALIZE INTEREST ----------------

    if "ai" in interest or "machine learning" in interest:

        interest = "artificial intelligence / ml"

    elif "data" in interest:

        interest = "data science / analytics"

    elif "software" in interest:

        interest = "software development"

    elif "cyber" in interest:

        interest = "cybersecurity"

    elif "web" in interest:

        interest = "web development"


    # ---------------- FALLBACKS ----------------

    if interest not in QUESTION_BANK:

        interest = "software development"

    if level not in QUESTION_BANK[interest]:

        level = "beginner"


    selected_questions = QUESTION_BANK[
        interest
    ][
        level
    ]


    return jsonify({

        "success": True,

        "interest": interest,

        "level": level,

        "questions": [

            {
                "id": index + 1,

                "question": q["question"]

            }

            for index, q
            in enumerate(selected_questions)

        ]

    })


# =====================================================
# EVALUATION
# =====================================================

@app.route("/evaluate", methods=["POST"])
def evaluate():

    data = request.json

    answers = data.get(
        "answers",
        []
    )

    user_id = data.get(
        "user_id"
    )


    # ---------------- USER ID CHECK ----------------

    if not user_id:

        return jsonify({
            "success": False,
            "message": "User ID is required"
        }), 400


    # ---------------- GET PROFILE ----------------

    conn = get_db()

    profile = conn.execute("""
        SELECT interest, level
        FROM profiles
        WHERE user_id = ?
    """, (
        user_id,
    )).fetchone()

    conn.close()


    if profile is None:

        return jsonify({
            "success": False,
            "message": "Profile not found"
        }), 404


    interest = (
        profile["interest"] or ""
    ).strip().lower()

    level = (
        profile["level"] or "beginner"
    ).strip().lower()


    # ---------------- NORMALIZE INTEREST ----------------

    if "ai" in interest or "machine learning" in interest:

        interest = "artificial intelligence / ml"

    elif "data" in interest:

        interest = "data science / analytics"

    elif "software" in interest:

        interest = "software development"

    elif "cyber" in interest:

        interest = "cybersecurity"

    elif "web" in interest:

        interest = "web development"


    # ---------------- FALLBACKS ----------------

    if interest not in QUESTION_BANK:

        interest = "software development"

    if level not in QUESTION_BANK[interest]:

        level = "beginner"


    questions = QUESTION_BANK[
        interest
    ][
        level
    ]


    # =================================================
    # QUESTION SCORES
    # =================================================

    scores = []


    for i, question in enumerate(questions):

        # Missing answer

        if i >= len(answers):

            scores.append(0)

            continue


        answer = answers[i]


        # Make sure answer is a dictionary

        if not isinstance(answer, dict):

            answer_text = str(
                answer
            ).lower()

        else:

            answer_text = str(
                answer.get(
                    "answer",
                    ""
                )
            ).lower()


        matched = 0


        # Check expected keywords

        for word in question["keywords"]:

            if word.lower() in answer_text:

                matched += 1


        # Each keyword = 20 points

        score = min(
            matched * 20,
            100
        )


        # Detailed answer bonus

        if len(
            answer_text.strip()
        ) >= 30:

            score = min(
                score + 10,
                100
            )


        scores.append(score)


    # =================================================
    # OVERALL SCORE
    # =================================================

    if scores:

        overall_score = (
            sum(scores)
            // len(scores)
        )

    else:

        overall_score = 0


    # =================================================
    # READINESS
    # =================================================

    if overall_score >= 80:

        readiness = "HIGH"

    elif overall_score >= 60:

        readiness = "MODERATE"

    else:

        readiness = "DEVELOPING"


    # =================================================
    # SKILL PERFORMANCE
    # =================================================

    skill_scores = {}


    for i, question in enumerate(questions):

        skill = question["skill"]


        if skill not in skill_scores:

            skill_scores[skill] = []


        if i < len(scores):

            skill_scores[skill].append(
                scores[i]
            )


    skill_performance = {}


    for skill, skill_score_list in skill_scores.items():

        if skill_score_list:

            skill_performance[skill] = (
                sum(skill_score_list)
                // len(skill_score_list)
            )


    # =================================================
    # STRENGTHS
    # =================================================

    strengths = []


    for skill, score in skill_performance.items():

        if score >= 70:

            strengths.append(
                skill
            )


    # =================================================
    # KNOWLEDGE GAPS
    # =================================================

    knowledge_gaps = []


    for skill, score in skill_performance.items():

        if score < 60:

            knowledge_gaps.append(
                skill
            )


    # =================================================
    # TOPIC PERFORMANCE
    # =================================================

    topic_performance = {}


    for i, question in enumerate(questions):

        if i < len(scores):

            topic = question["topic"]

            topic_performance[topic] = scores[i]


    # =================================================
    # RESPONSE
    # =================================================

    return jsonify({

        "success": True,

        "scores": scores,

        "overall_score": overall_score,

        "readiness": readiness,

        "skill_performance": skill_performance,

        "strengths": strengths,

        "knowledge_gaps": knowledge_gaps,

        "topic_performance": topic_performance

    })


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )