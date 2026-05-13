import streamlit as st
from datetime import datetime, date
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import os
import copy

# ── PERSISTENT DATABASE ───────────────────────────
DB_PATH   = "fitmat.db"
NOTES_DIR = "uploaded_notes"
os.makedirs(NOTES_DIR, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    # Notes
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            title    TEXT NOT NULL,
            subject  TEXT NOT NULL,
            desc     TEXT,
            filename TEXT,
            path     TEXT,
            uploader TEXT,
            date     TEXT
        )
    """)

    # Students
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            class      TEXT,
            roll       TEXT,
            attendance TEXT,
            score      INTEGER,
            contact    TEXT,
            joined     TEXT,
            img        TEXT
        )
    """)

    # Attendance records
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            date    TEXT NOT NULL,
            student TEXT NOT NULL,
            status  TEXT NOT NULL,
            UNIQUE(date, student)
        )
    """)

    # Grades
    conn.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            student TEXT NOT NULL,
            subject TEXT NOT NULL,
            term    TEXT NOT NULL,
            score   INTEGER,
            UNIQUE(student, subject, term)
        )
    """)

    # Announcements
    conn.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            title  TEXT NOT NULL,
            body   TEXT NOT NULL,
            author TEXT,
            date   TEXT,
            pinned INTEGER DEFAULT 0,
            tag    TEXT DEFAULT 'General'
        )
    """)

    # Remarks / Feedback
    conn.execute("""
        CREATE TABLE IF NOT EXISTS remarks (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            student TEXT NOT NULL,
            teacher TEXT,
            subject TEXT,
            type    TEXT,
            text    TEXT,
            date    TEXT
        )
    """)

    # Timetable
    conn.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            day     TEXT NOT NULL,
            hour    TEXT NOT NULL,
            subject TEXT,
            UNIQUE(day, hour)
        )
    """)

    conn.commit()

    # ── Seed default students if empty ──
    if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        DEFAULT_STUDENTS = [
            ("Rahul Patil",    "10-A", "01", "92%", 82,  "98201 11111", "Jun 2024", "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&q=80"),
            ("Sneha Kulkarni", "10-A", "02", "88%", 79,  "98201 22222", "Jun 2024", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&q=80"),
            ("Aditya Joshi",   "10-B", "03", "95%", 91,  "98201 33333", "Jun 2024", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&q=80"),
            ("Meera Nair",     "10-B", "04", "70%", 65,  "98201 44444", "Jun 2024", "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&q=80"),
            ("Ravi Deshmukh",  "10-A", "05", "85%", 74,  "98201 55555", "Jun 2024", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80"),
        ]
        conn.executemany(
            "INSERT INTO students (name,class,roll,attendance,score,contact,joined,img) VALUES (?,?,?,?,?,?,?,?)",
            DEFAULT_STUDENTS
        )

    # ── Seed default announcements if empty ──
    if conn.execute("SELECT COUNT(*) FROM announcements").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO announcements (title,body,author,date,pinned,tag) VALUES (?,?,?,?,?,?)",
            [
                ("Annual Sports Day",
                 "Annual Sports Day is scheduled for 20th June. All students must participate.",
                 "Mrs. Priya Sharma", "08 May 2025", 1, "Event"),
                ("Exam Schedule Released",
                 "Mid-term exams begin 2nd June. Timetable pinned on the notice board.",
                 "Mr. Arjun Mehta", "05 May 2025", 0, "Exam"),
            ]
        )

    # ── Seed default timetable if empty ──
    if conn.execute("SELECT COUNT(*) FROM timetable").fetchone()[0] == 0:
        DEFAULT_TT = {
            "Monday":    {"08:00":"Math","09:00":"Science","10:00":"English","11:00":"History","12:00":"—","13:00":"Math","14:00":"Science"},
            "Tuesday":   {"08:00":"English","09:00":"Math","10:00":"History","11:00":"Science","12:00":"—","13:00":"English","14:00":"Math"},
            "Wednesday": {"08:00":"Science","09:00":"History","10:00":"Math","11:00":"English","12:00":"—","13:00":"Science","14:00":"History"},
            "Thursday":  {"08:00":"Math","09:00":"English","10:00":"Science","11:00":"Math","12:00":"—","13:00":"History","14:00":"English"},
            "Friday":    {"08:00":"History","09:00":"Science","10:00":"Math","11:00":"English","12:00":"—","13:00":"Science","14:00":"Math"},
            "Saturday":  {"08:00":"Math","09:00":"Science","10:00":"—","11:00":"—","12:00":"—","13:00":"—","14:00":"—"},
        }
        rows = [(d, h, s) for d, slots in DEFAULT_TT.items() for h, s in slots.items()]
        conn.executemany("INSERT INTO timetable (day,hour,subject) VALUES (?,?,?)", rows)

    conn.commit()
    conn.close()

# ── DB HELPERS ────────────────────────────────────

# Notes
def save_note_db(title, subject, desc, filename, path, uploader):
    conn = get_db()
    conn.execute(
        "INSERT INTO notes (title,subject,desc,filename,path,uploader,date) VALUES (?,?,?,?,?,?,?)",
        (title, subject, desc, filename, path, uploader, datetime.now().strftime("%d %b %Y"))
    )
    conn.commit(); conn.close()

def load_notes_db(uploader=None):
    conn = get_db()
    q = "SELECT * FROM notes WHERE 1=1"
    p = []
    if uploader: q += " AND uploader=?"; p.append(uploader)
    rows = conn.execute(q, p).fetchall(); conn.close()
    return [dict(r) for r in rows]

def delete_note_db(note_id):
    conn = get_db()
    row = conn.execute("SELECT path FROM notes WHERE id=?", (note_id,)).fetchone()
    if row and row["path"] and os.path.exists(row["path"]): os.remove(row["path"])
    conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit(); conn.close()

# Students
def load_students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM students ORDER BY roll").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_student(name, cls, roll, attendance, score, contact, joined, img):
    conn = get_db()
    conn.execute(
        "INSERT INTO students (name,class,roll,attendance,score,contact,joined,img) VALUES (?,?,?,?,?,?,?,?)",
        (name, cls, roll, attendance, score, contact, joined, img)
    )
    conn.commit(); conn.close()

def delete_student(name):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE name=?", (name,))
    conn.execute("DELETE FROM attendance WHERE student=?", (name,))
    conn.execute("DELETE FROM grades WHERE student=?", (name,))
    conn.execute("DELETE FROM remarks WHERE student=?", (name,))
    conn.commit(); conn.close()

# Attendance
def save_attendance(date_str, records):
    conn = get_db()
    for student, status in records.items():
        conn.execute(
            "INSERT INTO attendance (date,student,status) VALUES (?,?,?) ON CONFLICT(date,student) DO UPDATE SET status=excluded.status",
            (date_str, student, status)
        )
    conn.commit(); conn.close()

def load_attendance(date_str):
    conn = get_db()
    rows = conn.execute("SELECT student, status FROM attendance WHERE date=?", (date_str,)).fetchall()
    conn.close()
    return {r["student"]: r["status"] for r in rows}

def load_all_attendance_dates():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT date FROM attendance ORDER BY date").fetchall()
    conn.close()
    return [r["date"] for r in rows]

# Grades
def save_grade(student, subject, term, score):
    conn = get_db()
    conn.execute(
        "INSERT INTO grades (student,subject,term,score) VALUES (?,?,?,?) ON CONFLICT(student,subject,term) DO UPDATE SET score=excluded.score",
        (student, subject, term, score)
    )
    conn.commit(); conn.close()

def load_grades(student):
    conn = get_db()
    rows = conn.execute("SELECT subject, term, score FROM grades WHERE student=?", (student,)).fetchall()
    conn.close()
    result = {}
    for r in rows:
        if r["subject"] not in result: result[r["subject"]] = {}
        result[r["subject"]][r["term"]] = r["score"]
    return result

def load_all_grades():
    conn = get_db()
    rows = conn.execute("SELECT student, subject, term, score FROM grades").fetchall()
    conn.close()
    result = {}
    for r in rows:
        if r["student"] not in result: result[r["student"]] = {}
        if r["subject"] not in result[r["student"]]: result[r["student"]][r["subject"]] = {}
        result[r["student"]][r["subject"]][r["term"]] = r["score"]
    return result

# Announcements
def load_announcements():
    conn = get_db()
    rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_announcement(title, body, author, pinned, tag):
    conn = get_db()
    conn.execute(
        "INSERT INTO announcements (title,body,author,date,pinned,tag) VALUES (?,?,?,?,?,?)",
        (title, body, author, datetime.now().strftime("%d %b %Y"), 1 if pinned else 0, tag)
    )
    conn.commit(); conn.close()

def delete_announcement(ann_id):
    conn = get_db()
    conn.execute("DELETE FROM announcements WHERE id=?", (ann_id,))
    conn.commit(); conn.close()

# Remarks
def add_remark(student, teacher, subject, rtype, text):
    conn = get_db()
    conn.execute(
        "INSERT INTO remarks (student,teacher,subject,type,text,date) VALUES (?,?,?,?,?,?)",
        (student, teacher, subject, rtype, text, datetime.now().strftime("%d %b %Y"))
    )
    conn.commit(); conn.close()

def load_remarks(student=None):
    conn = get_db()
    if student and student != "All":
        rows = conn.execute("SELECT * FROM remarks WHERE student=? ORDER BY id DESC", (student,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM remarks ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Timetable
def load_timetable():
    conn = get_db()
    rows = conn.execute("SELECT day, hour, subject FROM timetable").fetchall()
    conn.close()
    tt = {}
    for r in rows:
        if r["day"] not in tt: tt[r["day"]] = {}
        tt[r["day"]][r["hour"]] = r["subject"]
    return tt

def update_timetable_slot(day, hour, subject):
    conn = get_db()
    conn.execute(
        "INSERT INTO timetable (day,hour,subject) VALUES (?,?,?) ON CONFLICT(day,hour) DO UPDATE SET subject=excluded.subject",
        (day, hour, subject)
    )
    conn.commit(); conn.close()

# ── INIT ──────────────────────────────────────────
init_db()

# ── PAGE CONFIG ───────────────────────────────────
st.set_page_config(
    page_title="Fitmat Class Portal",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stVerticalBlock"],
section.main,
.main, .block-container {
    background-color: #0d0d0d !important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }

html, body, p, div, span, label, li, a, h1, h2, h3,
[data-testid="stMarkdown"],
[data-testid="stText"],
[data-testid="stVerticalBlock"] * {
    color: #e8e8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] section {
    background-color: #141414 !important;
    border-right: 1px solid #222 !important;
    min-width: 210px !important;
    max-width: 210px !important;
}
[data-testid="stSidebar"] * { color: #e8e8e8 !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 0 !important; }
[data-testid="stSidebar"] .stRadio label {
    display: block !important;
    padding: 13px 20px !important;
    margin: 0 !important;
    border-radius: 0 !important;
    font-size: 0.88rem !important;
    cursor: pointer !important;
    border-left: 3px solid transparent !important;
    color: #777 !important;
    background: transparent !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(34,197,94,0.08) !important;
    color: #22c55e !important;
    border-left-color: #22c55e !important;
}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }

input, textarea, select,
.stTextInput input,
.stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background-color: #1e1e1e !important;
    color: #e8e8e8 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
}
input::placeholder, textarea::placeholder { color: #555 !important; }
input:focus, textarea:focus { border-color: #22c55e !important; outline: none !important; }

[data-baseweb="select"] > div {
    background-color: #1e1e1e !important;
    border: 1px solid #333 !important;
    color: #e8e8e8 !important;
}
[data-baseweb="popover"] > div, [role="listbox"] { background-color: #1e1e1e !important; }
[role="option"] { color: #e8e8e8 !important; background-color: #1e1e1e !important; }
[role="option"]:hover { background-color: #252525 !important; }

.stButton > button {
    background: #22c55e !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button:hover { background: #16a34a !important; }
.stDownloadButton > button {
    background: transparent !important;
    color: #22c55e !important;
    border: 1px solid #22c55e !important;
    border-radius: 8px !important;
}

[data-testid="metric-container"] {
    background: #1a1a1a !important;
    border: 1px solid #22c55e !important;
    border-radius: 12px !important;
    padding: 1.1rem !important;
}
[data-testid="metric-container"] label { color: #888 !important; font-size: 0.72rem !important; text-transform: uppercase !important; letter-spacing: 1px !important; }
[data-testid="stMetricValue"] { font-family: 'Bebas Neue', sans-serif !important; font-size: 2.2rem !important; color: #22c55e !important; line-height: 1 !important; }

[data-testid="stForm"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
}

.streamlit-expanderHeader {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #e8e8e8 !important;
}
.streamlit-expanderContent { background: #1a1a1a !important; }

[data-baseweb="checkbox"] span { border-color: #22c55e !important; }

[data-testid="stFileUploader"] { background: #1a1a1a !important; border-radius: 8px !important; }
[data-testid="stFileUploaderDropzone"] {
    background: #1a1a1a !important;
    border: 1px dashed #333 !important;
    border-radius: 8px !important;
}
[data-testid="stAlert"] { border-radius: 8px !important; }

[data-testid="stMarkdownContainer"] button,
[data-testid="stCopyButton"],
button[title="Copy to clipboard"],
.stMarkdown button { display: none !important; }
[data-testid="stDataFrame"] { border: 1px solid #2a2a2a !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── STATIC DATA ───────────────────────────────────
TEACHERS = {
    "teacher1": {
        "password": "teach123",
        "name": "Mrs. Priya Sharma",
        "subjects": ["Math", "Science"],
        "img": "https://images.unsplash.com/photo-1607990281513-2c110a25bd8c?w=200&q=80"
    },
    "teacher2": {
        "password": "teach456",
        "name": "Mr. Arjun Mehta",
        "subjects": ["English", "History"],
        "img": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=200&q=80"
    },
}

NOTES = [
    ("Algebra Basics",     "Math",    "Chapter 1–3: Linear equations",
     "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&q=80"),
    ("Trigonometry",       "Math",    "Chapter 4–5: Sine, cosine, unit circle",
     "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&q=80"),
    ("Newton's Laws",      "Science", "Chapter 2: Force, mass, acceleration",
     "https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?w=400&q=80"),
    ("Cell Biology",       "Science", "Chapter 7: Cell structure and function",
     "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&q=80"),
    ("Grammar Essentials", "English", "Parts of speech and sentence formation",
     "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&q=80"),
    ("Modern History",     "History", "Chapter 3: World War II overview",
     "https://images.unsplash.com/photo-1461360228754-6e81c478b882?w=400&q=80"),
]

SUBJ_COLOR = {"Math":"#22c55e","Science":"#3b82f6","English":"#f59e0b","History":"#ef4444"}
PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#888", family="DM Sans"),
    margin=dict(l=10,r=10,t=36,b=10),
    xaxis=dict(gridcolor="#222",linecolor="#333",tickfont=dict(size=11,color="#666")),
    yaxis=dict(gridcolor="#222",linecolor="#333",tickfont=dict(size=11,color="#666")),
)

# ── SESSION STATE ─────────────────────────────────
if "teacher" not in st.session_state:
    st.session_state.teacher = None

# ── SIDEBAR ───────────────────────────────────────
t = st.session_state.teacher

st.sidebar.markdown(f"""
<div style="padding:1.8rem 1.2rem 1rem;">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#22c55e;letter-spacing:2px;line-height:1;">FITMAT</div>
    <div style="font-size:0.65rem;color:#555;letter-spacing:2px;text-transform:uppercase;margin-top:2px;">Class Portal</div>
</div>
<hr style="border:none;border-top:1px solid #222;margin:0 0 0.5rem 0;">
""", unsafe_allow_html=True)

if t:
    st.sidebar.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:0.6rem 1.2rem 0.8rem;">
        <img src="{t['img']}" style="width:34px;height:34px;border-radius:50%;object-fit:cover;border:2px solid #22c55e;flex-shrink:0;">
        <div>
            <div style="font-size:0.78rem;font-weight:500;color:#ddd;">{t['name'].split()[-1]}</div>
            <div style="font-size:0.65rem;color:#22c55e;">● Active</div>
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #222;margin:0 0 0.3rem 0;">
    """, unsafe_allow_html=True)

pages = ["About Us","Teacher Login","Attendance","Notes","Students",
         "Report Cards","Timetable","Announcements","Feedback","Leaderboard"]
icons = ["🏫","👩‍🏫","📋","📝","🎒","📊","📅","📢","💬","🏆"]
menu  = st.sidebar.radio("", [f"{icons[i]}  {p}" for i,p in enumerate(pages)], label_visibility="collapsed")
selected = menu.split("  ",1)[1]

if t:
    st.sidebar.markdown("<hr style='border:none;border-top:1px solid #222;margin:0.5rem 0;'>", unsafe_allow_html=True)
    if st.sidebar.button("Sign out", use_container_width=True):
        st.session_state.teacher = None
        st.rerun()

# ── HELPERS ───────────────────────────────────────
def G(html):
    st.markdown(f'<div style="color:#e8e8e8;font-family:DM Sans,sans-serif;">{html}</div>', unsafe_allow_html=True)

def header(title, subtitle="", badge=None):
    badge_html = f'<span style="background:rgba(34,197,94,0.12);border:1px solid #22c55e;border-radius:20px;padding:5px 14px;font-size:0.78rem;font-weight:500;color:#22c55e;">● {badge}</span>' if badge else ""
    col_title, col_badge = st.columns([8, 2])
    with col_title:
        st.markdown(
            f'<div style="padding-bottom:0.6rem;">'
            f'<div style="font-family:Bebas Neue,sans-serif;font-size:2.4rem;color:#e8e8e8;letter-spacing:1px;line-height:1;">{title}</div>'
            f'<div style="font-size:0.82rem;color:#555;margin-top:4px;">{subtitle}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col_badge:
        if badge:
            st.markdown(f'<div style="text-align:right;padding-top:0.5rem;">{badge_html}</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #222;margin:0 0 1.5rem 0;">', unsafe_allow_html=True)

def lock_gate(section):
    G(f"""
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;padding:3rem 2rem;text-align:center;max-width:400px;">
        <div style="font-size:2.5rem;margin-bottom:1rem;">🔒</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:#e8e8e8;letter-spacing:1px;margin-bottom:0.5rem;">Teacher Login Required</div>
        <div style="font-size:0.85rem;color:#666;line-height:1.6;">Sign in via <b style="color:#22c55e;">Teacher Login</b> to access {section}.</div>
    </div>""")

def sec(text):
    G(f'<div style="font-size:0.72rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#444;margin:1rem 0 0.5rem;">{text}</div>')

def pad(px=12):
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)

def grade_letter(score):
    if score>=90: return "A+"
    if score>=80: return "A"
    if score>=70: return "B"
    if score>=60: return "C"
    if score>=50: return "D"
    return "F"

# ── MAIN ──────────────────────────────────────────
pad(32)
left, content, right = st.columns([0.05,11,0.05])
with content:

    # ════════════════ ABOUT US ════════════════
    if selected == "About Us":
        header("ABOUT US","Welcome to Fitmat Coaching Classes","ACTIVE")
        G("""
        <div style="position:relative;border-radius:12px;overflow:hidden;margin-bottom:1.2rem;">
            <img src="https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=1200&q=80"
                 style="width:100%;height:190px;object-fit:cover;display:block;filter:brightness(0.35);">
            <div style="position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 2rem;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2.4rem;color:#22c55e;letter-spacing:2px;line-height:1;">SHAPING BRIGHT FUTURES</div>
                <div style="font-size:0.9rem;color:#ccc;margin-top:6px;">Academic excellence meets physical discipline — since 2010.</div>
            </div>
        </div>""")
        c1,c2 = st.columns(2)
        with c1:
            G("""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-top:2px solid #22c55e;border-radius:12px;overflow:hidden;margin-bottom:1rem;">
                <img src="https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600&q=80" style="width:100%;height:120px;object-fit:cover;display:block;filter:brightness(0.45);">
                <div style="padding:1.1rem 1.3rem;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:#22c55e;letter-spacing:1px;margin-bottom:0.5rem;">OUR MISSION</div>
                    <div style="font-size:0.85rem;color:#999;line-height:1.8;">Fitmat is dedicated to building a thriving, energetic learning environment where every student is empowered to grow physically and mentally.</div>
                </div></div>""")
        with c2:
            G("""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-top:2px solid #22c55e;border-radius:12px;overflow:hidden;margin-bottom:1rem;">
                <img src="https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=600&q=80" style="width:100%;height:120px;object-fit:cover;display:block;filter:brightness(0.45);">
                <div style="padding:1.1rem 1.3rem;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:#22c55e;letter-spacing:1px;margin-bottom:0.5rem;">OUR VISION</div>
                    <div style="font-size:0.85rem;color:#999;line-height:1.8;">To cultivate disciplined, healthy, and well-rounded individuals ready to contribute positively through consistent learning.</div>
                </div></div>""")
        students_all = load_students()
        total_s = len(students_all)
        G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;overflow:hidden;margin-bottom:1rem;">
            <img src="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=1200&q=80" style="width:100%;height:150px;object-fit:cover;display:block;filter:brightness(0.35);">
            <div style="padding:1.5rem 1.8rem;">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:#e8e8e8;letter-spacing:1px;margin-bottom:0.8rem;">WHO WE ARE</div>
                <div style="font-size:0.87rem;color:#999;line-height:1.9;margin-bottom:0.7rem;">Fitmat is a specialized class designed around holistic student development combining academic rigor with physical fitness programs.</div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.8rem;">
                    <div style="background:#111;border:1px solid #22c55e;border-radius:10px;padding:1rem;text-align:center;">
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#22c55e;">{total_s}</div>
                        <div style="font-size:0.65rem;color:#555;letter-spacing:1.5px;text-transform:uppercase;margin-top:3px;">Students</div>
                    </div>
                    <div style="background:#111;border:1px solid #22c55e;border-radius:10px;padding:1rem;text-align:center;">
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#22c55e;">2</div>
                        <div style="font-size:0.65rem;color:#555;letter-spacing:1.5px;text-transform:uppercase;margin-top:3px;">Teachers</div>
                    </div>
                    <div style="background:#111;border:1px solid #22c55e;border-radius:10px;padding:1rem;text-align:center;">
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#22c55e;">95%</div>
                        <div style="font-size:0.65rem;color:#555;letter-spacing:1.5px;text-transform:uppercase;margin-top:3px;">Attendance Rate</div>
                    </div>
                </div>
            </div></div>""")
        sec("Meet Our Teachers")
        tc1,tc2 = st.columns(2)
        for col,td in zip([tc1,tc2],TEACHERS.values()):
            tags = " ".join(f'<span style="background:rgba(34,197,94,0.1);color:#22c55e;border:1px solid rgba(34,197,94,0.3);border-radius:20px;padding:2px 8px;font-size:0.68rem;">{s}</span>' for s in td["subjects"])
            with col:
                G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:1rem 1.2rem;display:flex;align-items:center;gap:12px;margin-bottom:0.5rem;">
                    <img src="{td['img']}" style="width:50px;height:50px;border-radius:50%;object-fit:cover;border:2px solid #22c55e;flex-shrink:0;">
                    <div><div style="font-weight:600;font-size:0.9rem;color:#e8e8e8;margin-bottom:4px;">{td['name']}</div><div>{tags}</div></div>
                </div>""")

    # ════════════════ TEACHER LOGIN ════════════════
    elif selected == "Teacher Login":
        t = st.session_state.teacher
        if t:
            header("TEACHER PANEL",f"Logged in as {t['name']}","ACTIVE")
            tags = " ".join(f'<span style="background:rgba(34,197,94,0.1);color:#22c55e;border:1px solid rgba(34,197,94,0.3);border-radius:20px;padding:2px 10px;font-size:0.72rem;">{s}</span>' for s in t.get("subjects",[]))
            G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-top:2px solid #22c55e;border-radius:12px;overflow:hidden;max-width:500px;margin-bottom:1.5rem;">
                <img src="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=800&q=80" style="width:100%;height:80px;object-fit:cover;display:block;filter:brightness(0.3);">
                <div style="padding:1rem 1.2rem;display:flex;align-items:center;gap:12px;">
                    <img src="{t['img']}" style="width:50px;height:50px;border-radius:50%;object-fit:cover;border:2px solid #22c55e;flex-shrink:0;margin-top:-24px;">
                    <div>
                        <div style="font-weight:600;font-size:0.95rem;color:#e8e8e8;">{t['name']}</div>
                        <div style="font-size:0.76rem;color:#555;margin-bottom:5px;">Teacher · Fitmat Class Portal</div>
                        <div>{tags}</div>
                    </div>
                </div></div>""")

            sec("Upload Study Material")
            with st.form("upload"):
                note_title   = st.text_input("Note Title", placeholder="e.g. Chapter 5: Quadratic Equations")
                note_subject = st.selectbox("Subject", t.get("subjects",["General"]))
                note_desc    = st.text_area("Description", placeholder="Brief summary…")
                note_file    = st.file_uploader("Attach file (PDF/DOCX/Image)", type=["pdf","docx","png","jpg","jpeg"])
                submitted    = st.form_submit_button("Upload Material")

            if submitted:
                if not note_title:
                    st.error("Please enter a note title.")
                elif not note_file:
                    st.error("Please attach a file.")
                else:
                    file_path = os.path.join(NOTES_DIR, note_file.name)
                    with open(file_path,"wb") as fh:
                        fh.write(note_file.getbuffer())
                    save_note_db(note_title, note_subject, note_desc or "No description.",
                                 note_file.name, file_path, t["name"])
                    st.success(f"✅ '{note_title}' saved permanently!")
                    st.rerun()

            my_uploads = load_notes_db(uploader=t["name"])
            if my_uploads:
                sec("Your Uploaded Notes")
                for n in my_uploads:
                    ext       = n["filename"].rsplit(".",1)[-1].upper() if n["filename"] else "FILE"
                    ext_color = {"PDF":"#ef4444","DOCX":"#3b82f6","PNG":"#22c55e","JPG":"#f59e0b","JPEG":"#f59e0b"}.get(ext,"#888")
                    col_a, col_b = st.columns([7,1])
                    with col_a:
                        G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-left:3px solid #22c55e;
                                    border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.4rem;
                                    display:flex;align-items:center;gap:14px;">
                            <div style="width:42px;height:42px;border-radius:8px;background:{ext_color}20;
                                        border:1px solid {ext_color}40;display:flex;align-items:center;
                                        justify-content:center;font-size:0.65rem;font-weight:700;color:{ext_color};flex-shrink:0;">{ext}</div>
                            <div style="flex:1;">
                                <div style="font-weight:600;font-size:0.9rem;color:#e8e8e8;">{n["title"]}</div>
                                <div style="font-size:0.76rem;color:#555;margin-top:2px;">{n["subject"]} · {n["date"]} · {n["filename"]}</div>
                                <div style="font-size:0.78rem;color:#777;margin-top:2px;">{n["desc"]}</div>
                            </div></div>""")
                    with col_b:
                        if n["path"] and os.path.exists(n["path"]):
                            with open(n["path"],"rb") as fh:
                                st.download_button("⬇", data=fh.read(), file_name=n["filename"], key=f"up_dl_{n['id']}")
                        if st.button("🗑", key=f"del_{n['id']}", help="Delete"):
                            delete_note_db(n["id"])
                            st.success("Note deleted.")
                            st.rerun()
        else:
            header("TEACHER LOGIN","Sign in to access your panel")
            G("""<div style="border-radius:12px;overflow:hidden;margin-bottom:1.2rem;">
                <img src="https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=1200&q=80"
                     style="width:100%;height:130px;object-fit:cover;display:block;filter:brightness(0.28);">
            </div>""")
            _,col,_ = st.columns([1,1.1,1])
            with col:
                sec("Teacher Credentials")
                username = st.text_input("Username", placeholder="teacher1 or teacher2")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                pad(4)
                if st.button("Sign In →", use_container_width=True):
                    u,p = username.strip(), password.strip()
                    if u in TEACHERS and TEACHERS[u]["password"]==p:
                        st.session_state.teacher = TEACHERS[u]
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Try: teacher1 / teach123  or  teacher2 / teach456")
                with st.expander("Demo credentials"):
                    st.markdown("| Username | Password |\n|---|---|\n| `teacher1` | `teach123` |\n| `teacher2` | `teach456` |")

    # ════════════════ ATTENDANCE ════════════════
    elif selected == "Attendance":
        t = st.session_state.teacher
        header("ATTENDANCE","Mark daily attendance")
        if not t:
            lock_gate("Attendance")
        else:
            students = load_students()
            G("""<div style="border-radius:12px;overflow:hidden;margin-bottom:1rem;">
                <img src="https://images.unsplash.com/photo-1588072432836-e10032774350?w=1200&q=80"
                     style="width:100%;height:110px;object-fit:cover;display:block;filter:brightness(0.28);">
            </div>""")
            c1,c2 = st.columns([1,2])
            with c1: date_sel    = st.date_input("Date", value=datetime.today())
            with c2: subject_sel = st.selectbox("Subject", t.get("subjects",[]))
            date_key = str(date_sel)

            # Load existing attendance for this date from DB
            existing = load_attendance(date_key)
            # Default to Present for students not yet marked
            current_records = {s["name"]: existing.get(s["name"], "Present") for s in students}

            sec(f"Student List — {date_sel.strftime('%d %b %Y')} · {subject_sel}")
            STATUS_OPTIONS = ["Present","Absent","Late"]
            updated_records = {}
            for s in students:
                name = s["name"]
                c1,c2 = st.columns([5,2])
                with c1:
                    G(f"""<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #1a1a1a;">
                        <img src="{s.get('img','')}" style="width:34px;height:34px;border-radius:50%;object-fit:cover;border:1px solid #333;flex-shrink:0;">
                        <span style="font-weight:500;color:#ddd;font-size:0.88rem;">{name}</span>
                        <span style="font-size:0.74rem;color:#444;">{s.get('class','—')} · Roll {s.get('roll','—')}</span>
                    </div>""")
                with c2:
                    current = current_records.get(name, "Present")
                    choice  = st.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current),
                                           key=f"att_{date_key}_{name}", label_visibility="collapsed")
                    updated_records[name] = choice

            pad(10)
            if st.button("Save Attendance"):
                save_attendance(date_key, updated_records)
                p_cnt = sum(1 for v in updated_records.values() if v=="Present")
                a_cnt = sum(1 for v in updated_records.values() if v=="Absent")
                l_cnt = sum(1 for v in updated_records.values() if v=="Late")
                st.success(f"✅ Saved for {date_sel.strftime('%d %b %Y')} — {p_cnt} Present · {a_cnt} Absent · {l_cnt} Late")

            pad(8)
            rec   = updated_records
            p_cnt = sum(1 for v in rec.values() if v=="Present")
            a_cnt = sum(1 for v in rec.values() if v=="Absent")
            l_cnt = sum(1 for v in rec.values() if v=="Late")
            m1,m2,m3 = st.columns(3)
            m1.metric("Present",p_cnt); m2.metric("Absent",a_cnt); m3.metric("Late",l_cnt)
            total = len(students)
            if total > 0:
                fig = go.Figure(go.Pie(values=[p_cnt,a_cnt,l_cnt],labels=["Present","Absent","Late"],
                                       hole=0.65,marker_colors=["#22c55e","#ef4444","#f59e0b"]))
                fig.update_traces(textinfo="none")
                fig.update_layout(height=220,
                                  annotations=[dict(text=f"<b>{int(p_cnt/total*100)}%</b>",x=0.5,y=0.5,
                                                    font_size=18,showarrow=False,font_color="#22c55e")],**PLOT)
                st.plotly_chart(fig,use_container_width=True)

            all_dates = load_all_attendance_dates()
            if len(all_dates) > 1:
                sec("Weekly Attendance Overview")
                dates_sorted = sorted(all_dates)[-7:]
                rows=[]
                for s in students:
                    row={"Student":s["name"],"Roll":s.get("roll","—"),"Class":s.get("class","—")}
                    for d in dates_sorted:
                        short = datetime.strptime(d,"%Y-%m-%d").strftime("%d %b")
                        day_rec = load_attendance(d)
                        row[short] = day_rec.get(s["name"],"—")
                    rows.append(row)
                st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    # ════════════════ NOTES ════════════════
    elif selected == "Notes":
        t = st.session_state.teacher
        header("NOTES","Study material library")
        if not t:
            lock_gate("Notes")
        else:
            G("""<div style="border-radius:12px;overflow:hidden;margin-bottom:1rem;">
                <img src="https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1200&q=80"
                     style="width:100%;height:100px;object-fit:cover;display:block;filter:brightness(0.28);">
            </div>""")
            search = st.text_input("Search…", placeholder="Algebra, Newton…")
            subj_f = st.selectbox("Filter", ["My Subjects"]+t.get("subjects",[])+["All"])
            notes  = list(NOTES)
            if search: notes=[n for n in notes if search.lower() in n[0].lower()]
            if subj_f=="My Subjects": notes=[n for n in notes if n[1] in t.get("subjects",[])]
            elif subj_f!="All":       notes=[n for n in notes if n[1]==subj_f]

            all_db_notes = load_notes_db()
            for un in all_db_notes:
                if subj_f=="All" or (subj_f=="My Subjects" and un["subject"] in t.get("subjects",[])) or subj_f==un["subject"]:
                    if not search or search.lower() in un["title"].lower():
                        notes = notes + [(un["title"],un["subject"],un["desc"],
                                          "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&q=80",un)]

            if not notes:
                st.info("No notes found.")
            else:
                cols = st.columns(3)
                for i,entry in enumerate(notes):
                    title,subj,desc,img = entry[0],entry[1],entry[2],entry[3]
                    uploaded_meta = entry[4] if len(entry)>4 else None
                    c    = SUBJ_COLOR.get(subj,"#22c55e")
                    mine = subj in t.get("subjects",[])
                    with cols[i%3]:
                        badge = ('<span style="font-size:0.68rem;color:#f59e0b;font-weight:600;">⬆ Uploaded</span>' if uploaded_meta
                                 else ('<span style="font-size:0.68rem;color:#22c55e;font-weight:600;">✓ Yours</span>' if mine else ''))
                        G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;
                                    border-top:2px solid {c if (mine or uploaded_meta) else '#2a2a2a'};
                                    border-radius:12px;overflow:hidden;margin-bottom:0.8rem;
                                    opacity:{'1' if (mine or uploaded_meta) else '0.4'};">
                            <img src="{img}" style="width:100%;height:100px;object-fit:cover;display:block;filter:brightness(0.5);">
                            <div style="padding:0.9rem 1rem;">
                                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
                                    <span style="background:{c}20;color:{c};font-size:0.68rem;font-weight:600;padding:2px 8px;border-radius:20px;border:1px solid {c}40;">{subj}</span>
                                    {badge}
                                </div>
                                <div style="font-size:0.92rem;font-weight:600;color:#e8e8e8;margin-bottom:3px;">{title}</div>
                                <div style="font-size:0.78rem;color:#666;margin-bottom:6px;">{desc}</div>
                            </div></div>""")
                        if uploaded_meta and uploaded_meta["path"] and os.path.exists(uploaded_meta["path"]):
                            with open(uploaded_meta["path"],"rb") as fh:
                                st.download_button("⬇ Download",data=fh.read(),file_name=uploaded_meta["filename"],key=f"ndl_{i}")
                        elif mine:
                            st.download_button("⬇ Download",data=f"# {title}\n{desc}",file_name=f"{title.replace(' ','_')}.txt",key=f"dl_{i}")

    # ════════════════ STUDENTS ════════════════
    elif selected == "Students":
        t = st.session_state.teacher
        header("STUDENTS","Enrolled students overview")
        if not t:
            lock_gate("Students")
        else:
            students = load_students()
            G("""<div style="border-radius:12px;overflow:hidden;margin-bottom:1rem;">
                <img src="https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=1200&q=80"
                     style="width:100%;height:110px;object-fit:cover;display:block;filter:brightness(0.28);">
            </div>""")
            avg_att   = round(sum(int(s["attendance"].replace("%","")) for s in students)/len(students)) if students else 0
            avg_score = round(sum(s["score"] for s in students)/len(students)) if students else 0
            c1,c2,c3 = st.columns(3)
            c1.metric("Total Students",len(students)); c2.metric("Avg Attendance",f"{avg_att}%"); c3.metric("Avg Score",avg_score)
            pad(12)

            with st.expander("➕  Add New Student",expanded=False):
                with st.form("add_student_form",clear_on_submit=True):
                    sec("Student Details")
                    fa,fb = st.columns(2)
                    with fa:
                        new_name    = st.text_input("Full Name *",placeholder="e.g. Riya Mehta")
                        new_roll    = st.text_input("Roll No. *",placeholder="e.g. 06")
                        new_cls     = st.text_input("Class",placeholder="e.g. 10-A")
                        new_contact = st.text_input("Parent Contact",placeholder="e.g. 98200 12345")
                    with fb:
                        new_score = st.number_input("Score (0–100)",min_value=0,max_value=100,value=75)
                        new_att   = st.number_input("Attendance %",min_value=0,max_value=100,value=90)
                        new_img   = st.text_input("Photo URL (optional)",value="https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&q=80")
                    add_btn = st.form_submit_button("Add Student")
                if add_btn:
                    if not new_name.strip() or not new_roll.strip():
                        st.error("Name and Roll No. are required.")
                    else:
                        add_student(
                            new_name.strip(), new_cls.strip() or "—", new_roll.strip(),
                            f"{int(new_att)}%", int(new_score),
                            new_contact.strip() or "—",
                            datetime.now().strftime("%b %Y"),
                            new_img.strip() or "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&q=80"
                        )
                        st.success(f"✅ {new_name} added!")
                        st.rerun()

            search_s = st.text_input("🔍  Search students",placeholder="Name or Roll No…")
            filter_s = st.selectbox("Filter by Class",["All"]+sorted({s.get("class","—") for s in students}))
            filtered = [s for s in students if
                        (not search_s or search_s.lower() in s["name"].lower() or search_s in s.get("roll","")) and
                        (filter_s=="All" or s.get("class","—")==filter_s)]

            sec(f"Student Roster ({len(filtered)} shown)")
            for s in filtered:
                score     = s["score"]
                bar_color = "#22c55e" if score>=80 else "#f59e0b" if score>=70 else "#ef4444"
                G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:0.9rem 1.2rem;margin-bottom:0.6rem;display:flex;align-items:center;gap:14px;">
                    <img src="{s.get('img','')}" style="width:44px;height:44px;border-radius:50%;object-fit:cover;border:2px solid #2a2a2a;flex-shrink:0;">
                    <div style="flex:1;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                            <span style="font-weight:600;font-size:0.9rem;color:#e8e8e8;">{s['name']}</span>
                            <span style="font-size:0.72rem;color:#444;">Roll {s.get('roll','—')} · {s.get('class','—')}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                            <div style="flex:1;background:#222;border-radius:4px;height:4px;">
                                <div style="width:{score}%;background:{bar_color};height:4px;border-radius:4px;"></div>
                            </div>
                            <span style="font-size:0.75rem;font-weight:600;color:{bar_color};">{score}/100</span>
                        </div>
                        <span style="font-size:0.72rem;color:#444;">Attendance: <b style="color:#aaa;">{s['attendance']}</b></span>
                    </div></div>""")

            if students:
                pad(8); sec("Remove a Student")
                del_name = st.selectbox("Select student to remove",["— select —"]+[s["name"] for s in students])
                if del_name!="— select —":
                    if st.button(f"🗑  Remove {del_name}",type="primary"):
                        delete_student(del_name)
                        st.success(f"Removed {del_name}."); st.rerun()

            if filtered:
                sec("Score Chart")
                fig=go.Figure(go.Bar(
                    x=[s["name"].split()[0] for s in filtered],
                    y=[s["score"] for s in filtered],
                    marker=dict(color=[s["score"] for s in filtered],
                                colorscale=[[0,"#ef4444"],[0.5,"#f59e0b"],[1,"#22c55e"]],
                                showscale=False)
                ))
                fig.update_layout(height=260,**PLOT); st.plotly_chart(fig,use_container_width=True)

    # ════════════════ REPORT CARDS ════════════════
    elif selected == "Report Cards":
        t = st.session_state.teacher
        header("REPORT CARDS","Grade tracker & student report cards")
        if not t:
            lock_gate("Report Cards")
        else:
            students    = load_students()
            ALL_SUBJECTS= ["Math","Science","English","History"]
            TERMS       = ["Term 1","Term 2","Term 3","Final"]
            G("""<div style="border-radius:12px;overflow:hidden;margin-bottom:1rem;">
                <img src="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200&q=80"
                     style="width:100%;height:100px;object-fit:cover;display:block;filter:brightness(0.28);">
            </div>""")
            with st.expander("✏️  Enter / Update Grades",expanded=False):
                with st.form("grade_form"):
                    g_student=st.selectbox("Student",[s["name"] for s in students])
                    g_subject=st.selectbox("Subject",ALL_SUBJECTS)
                    g_term=st.selectbox("Term",TERMS)
                    g_score=st.number_input("Score (0–100)",0,100,75)
                    if st.form_submit_button("Save Grade"):
                        save_grade(g_student, g_subject, g_term, int(g_score))
                        st.success(f"✅ {g_student} · {g_subject} · {g_term} → {g_score}")

            sec("View Report Card")
            view_student=st.selectbox("Select Student",[s["name"] for s in students],key="rc_sel")
            stu_data=next((s for s in students if s["name"]==view_student),None)
            gr=load_grades(view_student)
            if stu_data:
                G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-top:3px solid #22c55e;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;display:flex;align-items:center;gap:16px;">
                    <img src="{stu_data.get('img','')}" style="width:54px;height:54px;border-radius:50%;object-fit:cover;border:2px solid #22c55e;">
                    <div><div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:#e8e8e8;letter-spacing:1px;">{view_student}</div>
                    <div style="font-size:0.78rem;color:#555;">Roll {stu_data.get('roll','—')} · {stu_data.get('class','—')} · Attendance: {stu_data.get('attendance','—')}</div></div>
                </div>""")
                if gr:
                    rows=[]
                    for subj in ALL_SUBJECTS:
                        row={"Subject":subj}
                        term_scores=gr.get(subj,{})
                        total=0;count=0
                        for term in TERMS:
                            sc=term_scores.get(term,"—"); row[term]=sc
                            if sc!="—": total+=sc; count+=1
                        row["Average"]=round(total/count) if count else "—"
                        row["Grade"]=grade_letter(row["Average"]) if row["Average"]!="—" else "—"
                        rows.append(row)
                    df=pd.DataFrame(rows); st.dataframe(df,use_container_width=True,hide_index=True)
                    subj_avgs=[]
                    for subj in ALL_SUBJECTS:
                        scores=[v for v in gr.get(subj,{}).values() if isinstance(v,(int,float))]
                        subj_avgs.append(round(sum(scores)/len(scores)) if scores else 0)
                    fig=go.Figure(go.Scatterpolar(r=subj_avgs+[subj_avgs[0]],theta=ALL_SUBJECTS+[ALL_SUBJECTS[0]],fill='toself',fillcolor='rgba(34,197,94,0.1)',line=dict(color='#22c55e',width=2)))
                    fig.update_layout(polar=dict(bgcolor='#111',radialaxis=dict(visible=True,range=[0,100],gridcolor='#2a2a2a',color='#444'),angularaxis=dict(gridcolor='#2a2a2a',color='#666')),height=300,**PLOT)
                    st.plotly_chart(fig,use_container_width=True)
                    st.download_button(f"⬇ Download Report Card (CSV)",data=df.to_csv(index=False),file_name=f"{view_student.replace(' ','_')}_report.csv",mime="text/csv")
                else:
                    st.info("No grades recorded yet. Use the form above to enter grades.")

            sec("Class Grade Overview")
            all_grades = load_all_grades()
            overview_rows=[]
            for s in students:
                g=all_grades.get(s["name"],{})
                all_scores=[sc for sd in g.values() for sc in sd.values() if isinstance(sc,(int,float))]
                avg=round(sum(all_scores)/len(all_scores)) if all_scores else "—"
                overview_rows.append({"Student":s["name"],"Class":s.get("class","—"),"Roll":s.get("roll","—"),"Overall Avg":avg,"Grade":grade_letter(avg) if avg!="—" else "—","Attendance":s.get("attendance","—")})
            st.dataframe(pd.DataFrame(overview_rows),use_container_width=True,hide_index=True)

    # ════════════════ TIMETABLE ════════════════
    elif selected == "Timetable":
        t = st.session_state.teacher
        header("TIMETABLE","Class schedule & weekly planner","PUBLIC")
        G("""<div style="border-radius:12px;overflow:hidden;margin-bottom:1rem;">
            <img src="https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=1200&q=80"
                 style="width:100%;height:100px;object-fit:cover;display:block;filter:brightness(0.28);">
        </div>""")
        DAYS  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
        HOURS = ["08:00","09:00","10:00","11:00","12:00","13:00","14:00"]
        tt    = load_timetable()
        today_name = datetime.now().strftime("%A")
        hdr_cells = "".join(f'<th style="padding:8px 14px;font-size:0.72rem;font-weight:600;letter-spacing:1px;color:{"#22c55e" if d==today_name else "#555"};text-transform:uppercase;border-bottom:1px solid {"#22c55e" if d==today_name else "#222"};">{d[:3]}</th>' for d in DAYS)
        body_rows = ""
        for h in HOURS:
            cells=""
            for d in DAYS:
                subj=tt.get(d,{}).get(h,"—")
                c=SUBJ_COLOR.get(subj,"#333")
                if subj in("—",""):    cell_inner='<span style="color:#333;font-size:0.78rem;">—</span>'
                elif h=="12:00":       cell_inner='<span style="color:#555;font-size:0.72rem;font-style:italic;">Lunch</span>'
                else:                  cell_inner=f'<span style="background:{c}20;color:{c};border:1px solid {c}40;border-radius:6px;padding:2px 8px;font-size:0.75rem;font-weight:600;">{subj}</span>'
                bg="rgba(34,197,94,0.04)" if d==today_name else "transparent"
                cells+=f'<td style="padding:8px 14px;text-align:center;background:{bg};">{cell_inner}</td>'
            body_rows+=f'<tr><td style="padding:8px 14px;font-size:0.76rem;color:#555;font-weight:600;white-space:nowrap;">{h}</td>{cells}</tr>'
        G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;overflow:auto;margin-bottom:1rem;">
            <table style="width:100%;border-collapse:collapse;">
                <thead><tr><th style="padding:8px 14px;font-size:0.68rem;color:#333;text-transform:uppercase;">Time</th>{hdr_cells}</tr></thead>
                <tbody>{body_rows}</tbody>
            </table></div>""")
        legend=" ".join(f'<span style="background:{c}20;color:{c};border:1px solid {c}40;border-radius:20px;padding:3px 10px;font-size:0.72rem;font-weight:600;">{s}</span>' for s,c in SUBJ_COLOR.items())
        G(f'<div style="margin-bottom:1rem;">{legend}</div>')
        if t:
            with st.expander("✏️  Edit Timetable (Teacher Only)",expanded=False):
                with st.form("tt_form"):
                    ec1,ec2,ec3=st.columns(3)
                    with ec1: e_day=st.selectbox("Day",DAYS)
                    with ec2: e_hour=st.selectbox("Period",HOURS)
                    with ec3: e_subj=st.selectbox("Subject",["—","Math","Science","English","History","Free","Lunch"])
                    if st.form_submit_button("Update Slot"):
                        update_timetable_slot(e_day, e_hour, e_subj)
                        st.success(f"✅ Updated {e_day} {e_hour} → {e_subj}"); st.rerun()

    # ════════════════ ANNOUNCEMENTS ════════════════
    elif selected == "Announcements":
        t = st.session_state.teacher
        header("ANNOUNCEMENTS","School notices & updates","PUBLIC")
        G("""<div style="border-radius:12px;overflow:hidden;margin-bottom:1rem;">
            <img src="https://images.unsplash.com/photo-1516321497487-e288fb19713f?w=1200&q=80"
                 style="width:100%;height:100px;object-fit:cover;display:block;filter:brightness(0.25);">
        </div>""")
        TAG_COLORS={"Event":"#3b82f6","Exam":"#ef4444","Holiday":"#22c55e","General":"#888","Urgent":"#f97316"}
        if t:
            with st.expander("📢  Post New Announcement",expanded=False):
                with st.form("ann_form"):
                    a_title=st.text_input("Title *",placeholder="e.g. Parent-Teacher Meeting")
                    a_body=st.text_area("Message *",placeholder="Details…")
                    ac1,ac2=st.columns(2)
                    with ac1: a_tag=st.selectbox("Tag",["General","Event","Exam","Holiday","Urgent"])
                    with ac2: a_pinned=st.checkbox("📌 Pin this announcement")
                    if st.form_submit_button("Post Announcement"):
                        if not a_title.strip() or not a_body.strip(): st.error("Title and message required.")
                        else:
                            add_announcement(a_title.strip(), a_body.strip(), t["name"], a_pinned, a_tag)
                            st.success("✅ Posted!"); st.rerun()

        anns = load_announcements()
        pinned   = [a for a in anns if a.get("pinned")]
        unpinned = [a for a in anns if not a.get("pinned")]
        if pinned:
            sec("📌 Pinned")
            for a in pinned:
                tc=TAG_COLORS.get(a.get("tag","General"),"#888")
                G(f"""<div style="background:#1a1a1a;border:1px solid #22c55e;border-left:4px solid #22c55e;border-radius:12px;padding:1rem 1.3rem;margin-bottom:0.7rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <span style="font-weight:700;font-size:0.95rem;color:#e8e8e8;">📌 {a['title']}</span>
                        <span style="background:{tc}20;color:{tc};border:1px solid {tc}40;border-radius:20px;padding:2px 10px;font-size:0.68rem;font-weight:600;">{a.get('tag','General')}</span>
                    </div>
                    <div style="font-size:0.84rem;color:#999;line-height:1.7;margin-bottom:6px;">{a['body']}</div>
                    <div style="font-size:0.72rem;color:#444;">{a['author']} · {a['date']}</div>
                </div>""")
        sec("All Notices")
        for a in unpinned:
            tc=TAG_COLORS.get(a.get("tag","General"),"#888")
            G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-left:3px solid {tc};border-radius:12px;padding:1rem 1.3rem;margin-bottom:0.7rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-weight:600;font-size:0.9rem;color:#e8e8e8;">{a['title']}</span>
                    <span style="background:{tc}20;color:{tc};border:1px solid {tc}40;border-radius:20px;padding:2px 10px;font-size:0.68rem;font-weight:600;">{a.get('tag','General')}</span>
                </div>
                <div style="font-size:0.84rem;color:#999;line-height:1.7;margin-bottom:6px;">{a['body']}</div>
                <div style="font-size:0.72rem;color:#444;">{a['author']} · {a['date']}</div>
            </div>""")
        if t and anns:
            pad(6); sec("Remove Announcement")
            del_ann=st.selectbox("Select to delete",["— select —"]+[f"{a['id']}. {a['title']}" for a in anns])
            if del_ann!="— select —":
                ann_id=int(del_ann.split(".")[0])
                if st.button("🗑  Delete this announcement"):
                    delete_announcement(ann_id)
                    st.success("Removed."); st.rerun()

    # ════════════════ FEEDBACK ════════════════
    elif selected == "Feedback":
        t = st.session_state.teacher
        header("STUDENT FEEDBACK","Teacher remarks & progress notes","PUBLIC")
        G("""<div style="border-radius:12px;overflow:hidden;margin-bottom:1rem;">
            <img src="https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=80"
                 style="width:100%;height:100px;object-fit:cover;display:block;filter:brightness(0.28);">
        </div>""")
        students=load_students()
        if t:
            with st.expander("✏️  Add Remark",expanded=False):
                with st.form("remark_form"):
                    r_student=st.selectbox("Student",[s["name"] for s in students])
                    r_subject=st.selectbox("Subject",t.get("subjects",["General"]))
                    r_type=st.selectbox("Type",["Academic","Behaviour","Attendance","Achievement","Improvement Needed"])
                    r_text=st.text_area("Remark *",placeholder="e.g. Excellent progress in algebra…")
                    if st.form_submit_button("Submit Remark"):
                        if not r_text.strip(): st.error("Remark cannot be empty.")
                        else:
                            add_remark(r_student, t["name"], r_subject, r_type, r_text.strip())
                            st.success(f"✅ Remark added for {r_student}."); st.rerun()

        TYPE_COLORS={"Academic":"#3b82f6","Behaviour":"#f59e0b","Attendance":"#ef4444","Achievement":"#22c55e","Improvement Needed":"#f97316"}
        sec("View Remarks by Student")
        view_s=st.selectbox("Select Student",["All"]+[s["name"] for s in students],key="fb_sel")
        display_list = load_remarks(view_s)

        if not display_list:
            st.info("No remarks recorded yet.")
        else:
            for r in display_list:
                tc=TYPE_COLORS.get(r["type"],"#888"); sc=SUBJ_COLOR.get(r["subject"],"#888")
                stu=next((s for s in students if s["name"]==r["student"]),{})
                G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-left:3px solid {tc};border-radius:12px;padding:1rem 1.3rem;margin-bottom:0.7rem;">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                        <img src="{stu.get('img','')}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;border:1px solid #333;">
                        <div><span style="font-weight:600;font-size:0.88rem;color:#e8e8e8;">{r['student']}</span><span style="font-size:0.72rem;color:#555;margin-left:8px;">{stu.get('class','—')}</span></div>
                        <div style="margin-left:auto;display:flex;gap:6px;">
                            <span style="background:{sc}20;color:{sc};border:1px solid {sc}40;border-radius:20px;padding:2px 8px;font-size:0.68rem;font-weight:600;">{r['subject']}</span>
                            <span style="background:{tc}20;color:{tc};border:1px solid {tc}40;border-radius:20px;padding:2px 8px;font-size:0.68rem;font-weight:600;">{r['type']}</span>
                        </div>
                    </div>
                    <div style="font-size:0.86rem;color:#bbb;line-height:1.7;margin-bottom:6px;">"{r['text']}"</div>
                    <div style="font-size:0.72rem;color:#444;">— {r['teacher']} · {r['date']}</div>
                </div>""")

    # ════════════════ LEADERBOARD ════════════════
    elif selected == "Leaderboard":
        header("LEADERBOARD","Top performers & class rankings","PUBLIC")
        G("""<div style="border-radius:12px;overflow:hidden;margin-bottom:1rem;">
            <img src="https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1200&q=80"
                 style="width:100%;height:110px;object-fit:cover;display:block;filter:brightness(0.28);">
        </div>""")
        students=load_students()
        if not students:
            st.info("No students enrolled yet.")
        else:
            lb_mode=st.selectbox("Rank by",["Overall Score","Attendance","Combined (Score + Attendance)"])
            def combined_score(s): return round(s["score"]*0.6+int(s["attendance"].replace("%",""))*0.4)
            if lb_mode=="Overall Score":    ranked=sorted(students,key=lambda s:s["score"],reverse=True); key_fn=lambda s:s["score"]; label="Score"
            elif lb_mode=="Attendance":     ranked=sorted(students,key=lambda s:int(s["attendance"].replace("%","")),reverse=True); key_fn=lambda s:int(s["attendance"].replace("%","")); label="Attendance %"
            else:                           ranked=sorted(students,key=combined_score,reverse=True); key_fn=combined_score; label="Combined"
            medals=["🥇","🥈","🥉"]; RANK_COLORS=["#f59e0b","#9ca3af","#cd7c2f"]
            sec("Top Performers")
            if len(ranked)>=3:
                pod_cols=st.columns(3)
                for ci,(s,medal,rc) in enumerate(zip(ranked[:3],medals,RANK_COLORS)):
                    val=key_fn(s)
                    with pod_cols[ci]:
                        G(f"""<div style="background:#1a1a1a;border:1px solid {rc}40;border-top:3px solid {rc};border-radius:12px;padding:1.5rem 1rem;text-align:center;margin-bottom:0.5rem;">
                            <div style="font-size:2rem;margin-bottom:8px;">{medal}</div>
                            <img src="{s.get('img','')}" style="width:50px;height:50px;border-radius:50%;object-fit:cover;border:2px solid {rc};margin-bottom:8px;">
                            <div style="font-weight:700;font-size:0.9rem;color:#e8e8e8;margin-bottom:2px;">{s['name'].split()[0]}</div>
                            <div style="font-size:0.72rem;color:#555;margin-bottom:8px;">{s.get('class','—')}</div>
                            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:{rc};line-height:1;">{val}{'%' if label=='Attendance %' else ''}</div>
                            <div style="font-size:0.65rem;color:#444;letter-spacing:1px;text-transform:uppercase;">{label}</div>
                        </div>""")
            sec(f"Full Rankings — {label}")
            for rank,s in enumerate(ranked,1):
                val=key_fn(s); bar_color="#22c55e" if rank<=3 else "#3b82f6" if rank<=len(ranked)//2 else "#555"
                medal_str=medals[rank-1] if rank<=3 else f"#{rank}"
                G(f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:12px;">
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#444;width:36px;text-align:center;flex-shrink:0;">{medal_str}</div>
                    <img src="{s.get('img','')}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;border:1px solid #333;flex-shrink:0;">
                    <div style="flex:1;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                            <span style="font-weight:600;font-size:0.88rem;color:#e8e8e8;">{s['name']}</span>
                            <span style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;color:{bar_color};">{val}{'%' if label=='Attendance %' else ''}</span>
                        </div>
                        <div style="background:#222;border-radius:3px;height:3px;">
                            <div style="width:{min(val,100)}%;background:{bar_color};height:3px;border-radius:3px;"></div>
                        </div>
                    </div></div>""")
            sec("Achievements")
            badge_grid=""
            for s in students:
                badges=[]
                if s["score"]>=90: badges.append(("🌟","Scholar"))
                if s["score"]>=80: badges.append(("📚","High Achiever"))
                if int(s["attendance"].replace("%",""))>=95: badges.append(("✅","Perfect Attendance"))
                if int(s["attendance"].replace("%",""))<75: badges.append(("⚠️","Low Attendance"))
                if combined_score(s)>=85: badges.append(("🏆","All-Rounder"))
                if badges:
                    badge_html=" ".join(f'<span style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:20px;padding:2px 10px;font-size:0.72rem;color:#aaa;">{b[0]} {b[1]}</span>' for b in badges)
                    badge_grid+=f'<div style="margin-bottom:0.5rem;"><span style="font-size:0.82rem;color:#ddd;font-weight:600;">{s["name"]}</span> <span style="font-size:0.72rem;color:#444;">{s.get("class","—")}</span><br>{badge_html}</div>'
            if badge_grid:
                G(f'<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:1.2rem 1.4rem;">{badge_grid}</div>')
