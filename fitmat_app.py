import streamlit as st
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fitmat Coaching Classes",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --navy:   #0d1b2a;
    --teal:   #00b4a0;
    --gold:   #f5a623;
    --cream:  #fdf6ec;
    --card:   #ffffff;
    --border: #e8e0d4;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream);
    color: var(--navy);
}

/* ── hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a3550 60%, #0d3d3a 100%);
    border-radius: 20px;
    padding: 60px 48px;
    text-align: center;
    margin-bottom: 36px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,180,160,0.25), transparent 70%);
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.4rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -1px;
    margin: 0;
}
.hero-title span { color: #00b4a0; }
.hero-sub {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.72);
    margin-top: 10px;
    font-weight: 300;
    letter-spacing: 0.5px;
}
.hero-badge {
    display: inline-block;
    background: rgba(245,166,35,0.18);
    border: 1px solid rgba(245,166,35,0.5);
    color: #f5a623;
    border-radius: 40px;
    padding: 4px 18px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 18px;
}

/* ── Login card ── */
.login-wrap {
    max-width: 420px;
    margin: 0 auto;
    background: white;
    border-radius: 20px;
    padding: 44px 40px;
    box-shadow: 0 12px 48px rgba(13,27,42,0.12);
    border: 1px solid var(--border);
}
.login-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 6px;
}
.login-sub {
    color: #7a8490;
    font-size: 0.92rem;
    margin-bottom: 28px;
}

/* ── Streamlit input overrides ── */
div[data-baseweb="input"] input {
    border-radius: 10px !important;
    border: 1.5px solid #dce3ea !important;
    padding: 12px 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border 0.2s;
}
div[data-baseweb="input"] input:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px rgba(0,180,160,0.12) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #00b4a0, #008f7e) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    width: 100%;
    cursor: pointer;
    letter-spacing: 0.3px;
    transition: transform 0.15s, box-shadow 0.15s;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,180,160,0.35) !important;
}

/* ── Info cards ── */
.info-card {
    background: white;
    border-radius: 16px;
    padding: 28px 26px;
    border: 1px solid var(--border);
    box-shadow: 0 4px 18px rgba(13,27,42,0.06);
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
}
.info-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 32px rgba(13,27,42,0.12);
}
.card-icon {
    font-size: 2rem;
    margin-bottom: 12px;
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 8px;
}
.card-body {
    font-size: 0.88rem;
    color: #5a6470;
    line-height: 1.65;
}

/* ── Section headers ── */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--navy);
    border-left: 4px solid var(--teal);
    padding-left: 14px;
    margin: 36px 0 20px;
}

/* ── Timetable table ── */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 18px rgba(13,27,42,0.07);
    font-size: 0.9rem;
}
.styled-table thead {
    background: linear-gradient(135deg, #0d1b2a, #1a3550);
    color: white;
}
.styled-table th, .styled-table td {
    padding: 13px 18px;
    text-align: left;
    border-bottom: 1px solid #eef1f4;
}
.styled-table tbody tr:nth-child(even) { background: #f7fbfa; }
.styled-table tbody tr:hover { background: rgba(0,180,160,0.07); }
.badge {
    display: inline-block;
    padding: 3px 11px;
    border-radius: 30px;
    font-size: 0.78rem;
    font-weight: 600;
}
.badge-green  { background: #e6f7f5; color: #008f7e; }
.badge-gold   { background: #fff4e0; color: #c47d00; }
.badge-navy   { background: #e8ecf2; color: #2b4878; }

/* ── Announcement card ── */
.announcement {
    background: white;
    border-radius: 14px;
    padding: 20px 22px;
    border-left: 4px solid var(--teal);
    margin-bottom: 14px;
    box-shadow: 0 3px 12px rgba(13,27,42,0.06);
}
.ann-date { font-size: 0.78rem; color: #9aa3ab; margin-bottom: 4px; }
.ann-title { font-weight: 600; color: var(--navy); margin-bottom: 4px; }
.ann-body  { font-size: 0.87rem; color: #5a6470; line-height: 1.6; }

/* ── Notes grid ── */
.note-card {
    background: white;
    border-radius: 14px;
    padding: 22px 20px;
    border: 1px solid var(--border);
    text-align: center;
    box-shadow: 0 3px 12px rgba(13,27,42,0.06);
    transition: transform 0.2s;
}
.note-card:hover { transform: translateY(-3px); }
.note-icon { font-size: 2.4rem; margin-bottom: 10px; }
.note-subject { font-weight: 600; color: var(--navy); font-size: 0.95rem; }
.note-class { font-size: 0.8rem; color: #9aa3ab; margin-top: 3px; }

/* ── Welcome bar ── */
.welcome-bar {
    background: linear-gradient(135deg, #0d1b2a, #1a3550);
    border-radius: 14px;
    padding: 18px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
    color: white;
}
.welcome-name { font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 700; }
.welcome-sub  { font-size: 0.83rem; color: rgba(255,255,255,0.6); margin-top: 2px; }
.logout-btn {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.25);
    color: white;
    border-radius: 8px;
    padding: 7px 18px;
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
}

/* ── Tab override ── */
.stTabs [data-baseweb="tab-list"] {
    background: #eef1f5;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--teal) !important;
    box-shadow: 0 2px 8px rgba(13,27,42,0.1);
}
</style>
""", unsafe_allow_html=True)

# ── Credential store (extend as needed) ──────────────────────────────────────
USERS = {
    "admin":    {"password": "fitmat@admin", "role": "Admin",    "name": "Admin"},
    "student1": {"password": "pass1234",     "role": "Student",  "name": "Rahul Sharma"},
    "student2": {"password": "pass5678",     "role": "Student",  "name": "Priya Patil"},
    "teacher1": {"password": "teach2024",    "role": "Teacher",  "name": "Mrs. Desai"},
}

# ── Session state ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username  = ""
    st.session_state.role      = ""
    st.session_state.name      = ""

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_login():
    # Hero
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">Std. 8 · 9 · 10</div>
        <h1 class="hero-title">Fit<span>mat</span></h1>
        <p class="hero-sub">Where Every Student Finds Their Formula for Success</p>
    </div>
    """, unsafe_allow_html=True)

    # Three quick-info cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="info-card">
            <div class="card-icon">🎯</div>
            <div class="card-title">Expert Faculty</div>
            <div class="card-body">Experienced teachers for Maths, Science, English & Social Science.</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="info-card">
            <div class="card-icon">📅</div>
            <div class="card-title">Structured Batches</div>
            <div class="card-body">Morning & evening batches for Std. 8, 9 and 10 — small groups for personal attention.</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="info-card">
            <div class="card-icon">📈</div>
            <div class="card-title">Proven Results</div>
            <div class="card-body">Consistent 90 %+ board results with regular tests, notes & doubt sessions.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Login form
    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown("""
        <div class="login-wrap">
            <div class="login-title">Student Portal</div>
            <div class="login-sub">Sign in to access your dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", placeholder="Enter password", type="password")

        if st.button("Sign In →"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.role      = USERS[username]["role"]
                st.session_state.name      = USERS[username]["name"]
                st.rerun()
            else:
                st.error("❌ Invalid username or password. Please try again.")

        st.markdown("""
        <p style="text-align:center;font-size:0.8rem;color:#aab2bb;margin-top:18px;">
        Contact your class teacher to get login credentials.
        </p>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_dashboard():
    today = datetime.now().strftime("%A, %d %B %Y")

    # Welcome bar + logout
    col_w, col_btn = st.columns([5, 1])
    with col_w:
        st.markdown(f"""
        <div class="welcome-bar">
            <div>
                <div class="welcome-name">Welcome back, {st.session_state.name} 👋</div>
                <div class="welcome-sub">{today} &nbsp;·&nbsp; {st.session_state.role}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            for k in ["logged_in","username","role","name"]:
                st.session_state[k] = False if k == "logged_in" else ""
            st.rerun()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠  About Fitmat",
        "📅  Timetable",
        "📢  Announcements",
        "📄  Study Material",
    ])

    # ── TAB 1 · ABOUT ─────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">About Fitmat Coaching Classes</div>', unsafe_allow_html=True)

        a1, a2 = st.columns([1.4, 1])
        with a1:
            st.markdown("""
            <div class="info-card">
                <div class="card-title">🏫 Our Mission</div>
                <div class="card-body">
                Fitmat Coaching Classes is dedicated to nurturing every student in Std. 8, 9 and 10
                with personalised attention, rigorous practice and a supportive learning environment.
                We believe every student can excel — our job is to show them how.<br><br>
                <b>Est.</b> 2018 &nbsp;|&nbsp; <b>Location:</b> Artist Village, Maharashtra<br>
                <b>Contact:</b> fitmat.classes@gmail.com &nbsp;|&nbsp; +91 98765 43210
                </div>
            </div>
            """, unsafe_allow_html=True)
        with a2:
            st.markdown("""
            <div class="info-card">
                <div class="card-title">📌 Quick Facts</div>
                <div class="card-body">
                ✅ Standards Offered: 8, 9 & 10<br><br>
                ✅ Subjects: Maths · Science · English · SST<br><br>
                ✅ Batch Size: Max 20 students<br><br>
                ✅ Tests every Saturday<br><br>
                ✅ Free doubt sessions on request
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Our Faculty</div>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        faculty = [
            ("👩‍🏫", "Mrs. Desai", "Maths · Std 8, 9, 10", "M.Sc Maths · 12 yrs exp"),
            ("👨‍🏫", "Mr. Kulkarni", "Science · Std 9, 10", "M.Sc Physics · 8 yrs exp"),
            ("👩‍🏫", "Ms. Joshi", "English & SST · Std 8, 9", "MA English · 6 yrs exp"),
        ]
        for col, (icon, name, sub, qual) in zip([f1, f2, f3], faculty):
            with col:
                st.markdown(f"""
                <div class="info-card" style="text-align:center">
                    <div style="font-size:2.8rem">{icon}</div>
                    <div class="card-title" style="text-align:center">{name}</div>
                    <div class="card-body" style="text-align:center">{sub}<br><span style="color:#00b4a0;font-weight:600">{qual}</span></div>
                </div>""", unsafe_allow_html=True)

    # ── TAB 2 · TIMETABLE ─────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Weekly Class Timetable</div>', unsafe_allow_html=True)

        st.markdown("""
        <table class="styled-table">
        <thead><tr><th>Day</th><th>Time</th><th>Standard</th><th>Subject</th><th>Teacher</th><th>Room</th></tr></thead>
        <tbody>
        <tr><td>Monday</td><td>7:00 – 8:30 AM</td><td><span class="badge badge-green">Std 8</span></td><td>Maths</td><td>Mrs. Desai</td><td>Room 1</td></tr>
        <tr><td>Monday</td><td>5:00 – 6:30 PM</td><td><span class="badge badge-gold">Std 10</span></td><td>Science</td><td>Mr. Kulkarni</td><td>Room 2</td></tr>
        <tr><td>Tuesday</td><td>7:00 – 8:30 AM</td><td><span class="badge badge-navy">Std 9</span></td><td>Maths</td><td>Mrs. Desai</td><td>Room 1</td></tr>
        <tr><td>Tuesday</td><td>5:00 – 6:30 PM</td><td><span class="badge badge-green">Std 8</span></td><td>Science</td><td>Mr. Kulkarni</td><td>Room 2</td></tr>
        <tr><td>Wednesday</td><td>7:00 – 8:30 AM</td><td><span class="badge badge-gold">Std 10</span></td><td>Maths</td><td>Mrs. Desai</td><td>Room 1</td></tr>
        <tr><td>Wednesday</td><td>5:00 – 6:30 PM</td><td><span class="badge badge-navy">Std 9</span></td><td>English</td><td>Ms. Joshi</td><td>Room 3</td></tr>
        <tr><td>Thursday</td><td>7:00 – 8:30 AM</td><td><span class="badge badge-green">Std 8</span></td><td>English & SST</td><td>Ms. Joshi</td><td>Room 3</td></tr>
        <tr><td>Thursday</td><td>5:00 – 6:30 PM</td><td><span class="badge badge-gold">Std 10</span></td><td>Maths</td><td>Mrs. Desai</td><td>Room 1</td></tr>
        <tr><td>Friday</td><td>7:00 – 8:30 AM</td><td><span class="badge badge-navy">Std 9</span></td><td>Science</td><td>Mr. Kulkarni</td><td>Room 2</td></tr>
        <tr><td>Friday</td><td>5:00 – 6:30 PM</td><td><span class="badge badge-green">Std 8</span></td><td>Maths</td><td>Mrs. Desai</td><td>Room 1</td></tr>
        <tr><td><b>Saturday</b></td><td>9:00 – 11:00 AM</td><td>All Stds</td><td>📝 Weekly Test</td><td>All Faculty</td><td>Hall</td></tr>
        <tr><td><b>Sunday</b></td><td colspan="5">🏖️ Holiday</td></tr>
        </tbody>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 Doubt sessions are available after every class. Contact your teacher to book a slot.")

    # ── TAB 3 · ANNOUNCEMENTS ─────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Latest Announcements</div>', unsafe_allow_html=True)

        announcements = [
            ("05 May 2026", "🔴 Important", "Pre-Board Examination Schedule Released",
             "Pre-board exams for Std 10 will be held from 15–20 May 2026. Syllabus covers all chapters. Admit cards to be collected from the office."),
            ("01 May 2026", "📘 Academic", "New Chapter Starts — Trigonometry (Std 10)",
             "Mrs. Desai will begin the Trigonometry unit from Monday 6th May. Students are requested to bring a protractor and compass."),
            ("28 Apr 2026", "📝 Test Results", "April Monthly Test Marks Uploaded",
             "Results for the April monthly test (Maths & Science) have been updated. Please collect your answer sheets on Saturday."),
            ("20 Apr 2026", "🏖️ Holiday Notice", "Class Closed — Maharashtra Day",
             "Fitmat Coaching Classes will remain closed on 1st May 2026 on account of Maharashtra Day. Classes resume on 2nd May."),
            ("15 Apr 2026", "📢 General", "Fee Reminder — May Month",
             "May month fees are due by 10th May 2026. Please submit fees to the office or via UPI. Late fee of ₹50 applicable after due date."),
        ]

        colors = ["#e74c3c","#2980b9","#27ae60","#e67e22","#8e44ad"]
        for i, (date, tag, title, body) in enumerate(announcements):
            color = colors[i % len(colors)]
            st.markdown(f"""
            <div class="announcement" style="border-left-color:{color}">
                <div class="ann-date">{date} &nbsp;·&nbsp; <span style="color:{color};font-weight:600">{tag}</span></div>
                <div class="ann-title">{title}</div>
                <div class="ann-body">{body}</div>
            </div>""", unsafe_allow_html=True)

        if st.session_state.role == "Admin":
            st.markdown('<div class="section-header">➕ Post Announcement (Admin)</div>', unsafe_allow_html=True)
            new_title = st.text_input("Announcement Title")
            new_body  = st.text_area("Announcement Body")
            if st.button("Post Announcement"):
                if new_title and new_body:
                    st.success(f"✅ Announcement '{new_title}' posted successfully!")
                else:
                    st.warning("Please fill in both title and body.")

    # ── TAB 4 · STUDY MATERIAL ────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-header">Study Material & Notes</div>', unsafe_allow_html=True)

        notes = [
            ("📐", "Algebra Basics", "Std 8 · Maths"),
            ("🔭", "Light & Reflection", "Std 10 · Science"),
            ("📊", "Statistics", "Std 9 · Maths"),
            ("🌍", "Geography — Resources", "Std 8 · SST"),
            ("⚗️", "Acids, Bases & Salts", "Std 10 · Science"),
            ("📝", "Letter Writing Guide", "Std 9 · English"),
            ("📐", "Coordinate Geometry", "Std 10 · Maths"),
            ("🌱", "Life Processes", "Std 10 · Science"),
            ("📘", "Understanding Media", "Std 9 · SST"),
        ]

        cols = st.columns(3)
        for i, (icon, subject, cls) in enumerate(notes):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="note-card">
                    <div class="note-icon">{icon}</div>
                    <div class="note-subject">{subject}</div>
                    <div class="note-class">{cls}</div>
                    <div style="margin-top:14px">
                        <span style="background:#e6f7f5;color:#008f7e;padding:5px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;cursor:pointer">⬇ Download PDF</span>
                    </div>
                </div>
                <br>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <p style="text-align:center;color:#9aa3ab;font-size:0.85rem">
        📌 New material is uploaded every week. Check back regularly or ask your teacher.
        </p>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.logged_in:
    show_dashboard()
else:
    show_login()
