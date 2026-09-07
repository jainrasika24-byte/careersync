from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "careersync_secret_key_tgpcet_nagpur"

DB_NAME = "careersync.db"

# ---------- DATABASE HELPERS ----------

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS profiles (
        user_id INTEGER PRIMARY KEY,
        branch TEXT,
        year TEXT,
        phone TEXT,
        bio TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        proficiency TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        issuer TEXT,
        year TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS goals (
        user_id INTEGER PRIMARY KEY,
        goal_title TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    
    # Seed rich demo student data if empty database
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    if user_count == 0:
        demo_pass = generate_password_hash("password123")
        c.execute("INSERT INTO users (id, name, email, password) VALUES (1, ?, ?, ?)",
                  ("Rasika Chinchalkar", "rasika@tgpcet.ac.in", demo_pass))
        c.execute("INSERT INTO profiles (user_id, branch, year, phone, bio) VALUES (1, ?, ?, ?, ?)",
                  ("B.Tech Computer Science & Engineering", "Final Year", "+91 98765 43210",
                   "Computer Science student at TGPCET Nagpur. Passionate about Full-Stack Web Development, Data Structures, and AI-powered software tools."))
        
        sample_skills = [
            ("HTML", "Advanced (75%)"),
            ("CSS", "Advanced (75%)"),
            ("JavaScript", "Intermediate (50%)"),
            ("Python", "Advanced (75%)"),
            ("Flask", "Intermediate (50%)"),
            ("SQL", "Advanced (75%)"),
            ("Git", "Intermediate (50%)"),
            ("Data Structures", "Intermediate (50%)")
        ]
        for sk, prof in sample_skills:
            c.execute("INSERT INTO skills (user_id, skill_name, proficiency) VALUES (1, ?, ?)", (sk, prof))
            
        sample_certs = [
            ("AWS Certified Cloud Practitioner", "Amazon Web Services", "2025"),
            ("Full Stack Web Development", "Coursera / Meta", "2024"),
            ("Python for Data Science", "NPTEL", "2024")
        ]
        for title, issuer, year in sample_certs:
            c.execute("INSERT INTO certificates (user_id, title, issuer, year) VALUES (1, ?, ?, ?)", (title, issuer, year))
            
        c.execute("INSERT INTO goals (user_id, goal_title) VALUES (1, 'Web Developer')")
        conn.commit()
        
    conn.close()

# Context processor helper for checking endpoints in Jinja templates
@app.context_processor
def utility_processor():
    def endpoint_exists(endpoint):
        return endpoint in app.view_functions
    return dict(endpoint_exists=endpoint_exists)

# ---------- EXPANDED CAREER GOALS DATA ----------
CAREER_GOALS = {
    "Web Developer": ["HTML", "CSS", "JavaScript", "Python", "Flask", "SQL", "Git", "REST APIs"],
    "AI/ML Engineer": ["Python", "Machine Learning", "Data Structures", "Statistics", "NumPy", "Pandas", "SQL"],
    "Data Analyst": ["Python", "SQL", "Excel", "Statistics", "Data Visualization"],
    "Software Engineer": ["Data Structures", "Algorithms", "Python", "Java", "Git", "OOP", "SQL"],
    "Cloud & DevOps Engineer": ["Linux", "Git", "Docker", "AWS", "CI/CD Pipelines", "Python"],
    "Mobile App Developer": ["Java", "Kotlin", "Flutter", "UI/UX", "Firebase"],
}

# ---------- AUTH DECORATOR ----------

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

# ---------- ROUTES ----------

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("overview"))
    # Auto-login demo user for convenience if user opens site directly
    session["user_id"] = 1
    session["user_name"] = "Rasika Chinchalkar"
    return redirect(url_for("overview"))

@app.route("/overview")
def overview():
    return render_template("overview.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        hashed = generate_password_hash(password)
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                         (name, email, hashed))
            user_id = cursor.lastrowid
            
            # Default profile for new user
            cursor.execute("INSERT INTO profiles (user_id, branch, year, phone, bio) VALUES (?, ?, ?, ?, ?)",
                         (user_id, "B.Tech Computer Science & Engineering", "Final Year", "", "TGPCET Student"))
            cursor.execute("INSERT INTO goals (user_id, goal_title) VALUES (?, ?)", (user_id, "Web Developer"))
            
            conn.commit()
            session["user_id"] = user_id
            session["user_name"] = name
            flash("Registration successful! Welcome to CareerSync.", "success")
            return redirect(url_for("overview"))
        except sqlite3.IntegrityError:
            flash("That email is already registered.", "error")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("overview"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    conn = get_db()
    skills = conn.execute("SELECT * FROM skills WHERE user_id=?", (uid,)).fetchall()
    certs = conn.execute("SELECT * FROM certificates WHERE user_id=?", (uid,)).fetchall()
    goal_row = conn.execute("SELECT * FROM goals WHERE user_id=?", (uid,)).fetchone()
    conn.close()

    goal_title = goal_row["goal_title"] if goal_row else "Web Developer"
    match_pct = 0
    missing = []
    if goal_title and goal_title in CAREER_GOALS:
        required = CAREER_GOALS[goal_title]
        have = [s["skill_name"] for s in skills]
        matched = [r for r in required if any(r.lower() == h.lower() for h in have)]
        missing = [r for r in required if not any(r.lower() == h.lower() for h in have)]
        match_pct = round((len(matched) / len(required)) * 100) if required else 0

    return render_template("dashboard.html", skills=skills, certs=certs,
                           goal_title=goal_title, match_pct=match_pct, missing=missing)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    uid = session["user_id"]
    conn = get_db()
    if request.method == "POST":
        branch = request.form["branch"]
        year = request.form["year"]
        phone = request.form["phone"]
        bio = request.form["bio"]
        existing = conn.execute("SELECT * FROM profiles WHERE user_id=?", (uid,)).fetchone()
        if existing:
            conn.execute("UPDATE profiles SET branch=?, year=?, phone=?, bio=? WHERE user_id=?",
                         (branch, year, phone, bio, uid))
        else:
            conn.execute("INSERT INTO profiles (user_id, branch, year, phone, bio) VALUES (?, ?, ?, ?, ?)",
                         (uid, branch, year, phone, bio))
        conn.commit()
        flash("Profile updated successfully.", "success")
    profile_data = conn.execute("SELECT * FROM profiles WHERE user_id=?", (uid,)).fetchone()
    conn.close()
    return render_template("profile.html", profile=profile_data)

@app.route("/skills", methods=["GET", "POST"])
@login_required
def skills():
    uid = session["user_id"]
    conn = get_db()
    if request.method == "POST":
        skill_name = request.form["skill_name"].strip()
        proficiency = request.form["proficiency"]
        if skill_name:
            conn.execute("INSERT INTO skills (user_id, skill_name, proficiency) VALUES (?, ?, ?)",
                         (uid, skill_name, proficiency))
            conn.commit()
            flash(f"Added skill: '{skill_name}'", "success")
    skill_list = conn.execute("SELECT * FROM skills WHERE user_id=?", (uid,)).fetchall()
    conn.close()
    return render_template("skills.html", skills=skill_list)

@app.route("/skills/delete/<int:skill_id>")
@login_required
def delete_skill(skill_id):
    conn = get_db()
    conn.execute("DELETE FROM skills WHERE id=? AND user_id=?", (skill_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("Skill removed.", "success")
    return redirect(url_for("skills"))

@app.route("/certificates", methods=["GET", "POST"])
@login_required
def certificates():
    uid = session["user_id"]
    conn = get_db()
    if request.method == "POST":
        title = request.form["title"].strip()
        issuer = request.form["issuer"]
        year = request.form["year"]
        if title:
            conn.execute("INSERT INTO certificates (user_id, title, issuer, year) VALUES (?, ?, ?, ?)",
                         (uid, title, issuer, year))
            conn.commit()
            flash(f"Added certificate: '{title}'", "success")
    cert_list = conn.execute("SELECT * FROM certificates WHERE user_id=?", (uid,)).fetchall()
    conn.close()
    return render_template("certificates.html", certificates=cert_list)

@app.route("/certificates/delete/<int:cert_id>")
@login_required
def delete_certificate(cert_id):
    conn = get_db()
    conn.execute("DELETE FROM certificates WHERE id=? AND user_id=?", (cert_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("Certificate removed.", "success")
    return redirect(url_for("certificates"))

@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    uid = session["user_id"]
    conn = get_db()
    if request.method == "POST":
        goal_title = request.form["goal_title"]
        existing = conn.execute("SELECT * FROM goals WHERE user_id=?", (uid,)).fetchone()
        if existing:
            conn.execute("UPDATE goals SET goal_title=? WHERE user_id=?", (goal_title, uid))
        else:
            conn.execute("INSERT INTO goals (user_id, goal_title) VALUES (?, ?)", (goal_title, uid))
        conn.commit()
        flash(f"Target Career Goal updated to '{goal_title}'.", "success")
    current_goal = conn.execute("SELECT * FROM goals WHERE user_id=?", (uid,)).fetchone()
    conn.close()
    return render_template("goals.html", career_goals=CAREER_GOALS.keys(),
                           current_goal=current_goal["goal_title"] if current_goal else "Web Developer")

@app.route("/resume")
@login_required
def resume():
    uid = session["user_id"]
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    profile_data = conn.execute("SELECT * FROM profiles WHERE user_id=?", (uid,)).fetchone()
    skill_list = conn.execute("SELECT * FROM skills WHERE user_id=?", (uid,)).fetchall()
    cert_list = conn.execute("SELECT * FROM certificates WHERE user_id=?", (uid,)).fetchall()
    goal_row = conn.execute("SELECT * FROM goals WHERE user_id=?", (uid,)).fetchone()
    conn.close()
    return render_template("resume.html", user=user, profile=profile_data,
                           skills=skill_list, certificates=cert_list,
                           goal=goal_row["goal_title"] if goal_row else "Web Developer")

if __name__ == "__main__":
    init_db()
    print("CareerSync Server starting on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
