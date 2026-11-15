



# =========================================================
# 1. IMPORTS AND PAGE CONFIGURATION
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import fitz
import re
import io

from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from modules.recommendation_engine import (
    rank_internships,
    calculate_match
)

from modules.ml_model import predict_suitability


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="InternAlign AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 2. PREMIUM DARK PURPLE THEME
# =========================================================

st.markdown("""
<style>

/* =====================================================
   MAIN BACKGROUND
===================================================== */

.stApp {
    background:
        radial-gradient(
            ellipse at 10% 0%,
            rgba(124,58,237,0.16),
            transparent 35%
        ),
        radial-gradient(
            ellipse at 90% 90%,
            rgba(79,70,229,0.12),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #0F0C1D,
            #17132C
        );

    color: #F8FAFC;
}

/* =====================================================
   MAIN CONTENT
===================================================== */

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* =====================================================
   HEADINGS
===================================================== */

h1, h2, h3, h4 {
    color: #E9D5FF !important;
    font-weight: 800 !important;
}

/* =====================================================
   GENERAL TEXT
===================================================== */

p, label, span {
    color: #E2E8F0;
}


/* =====================================================
   PREMIUM SIDEBAR DESIGN
===================================================== */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #100D20 0%,
        #1B1532 55%,
        #251944 100%
    ) !important;

    border-right: 1px solid rgba(167, 139, 250, 0.30);
    box-shadow: 5px 0 25px rgba(0, 0, 0, 0.25);
}

/* SIDEBAR CONTENT */

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

/* SIDEBAR HEADINGS */

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #DDD6FE !important;
    font-weight: 800 !important;
}

/* NAVIGATION SPACING */

[data-testid="stSidebar"] [data-testid="stRadio"] {
    padding-top: 12px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #DDD6FE !important;
    font-size: 14px;
    font-weight: 600;
    padding: 9px 12px;
    border-radius: 11px;
    transition: all 0.25s ease;
}

/* NAVIGATION HOVER */

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(139, 92, 246, 0.18);
    color: #FFFFFF !important;
}

/* RADIO BUTTON ACCENT */

[data-testid="stSidebar"] [data-testid="stRadio"] input {
    accent-color: #A78BFA;
}

/* SIDEBAR DIVIDERS */

[data-testid="stSidebar"] hr {
    border-color: rgba(167, 139, 250, 0.22);
    margin: 18px 0;
}

/* SIDEBAR TEXT */

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #C4B5FD;
}

/* SIDEBAR FOOTER */

.sidebar-footer {
    background: rgba(124, 58, 237, 0.13);
    border: 1px solid rgba(167, 139, 250, 0.25);
    border-radius: 13px;
    padding: 13px;
    text-align: center;
    color: #DDD6FE;
    font-size: 12px;
    line-height: 1.7;
}
/* HIGHLIGHT SELECTED SIDEBAR MENU */

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(
        90deg,
        #7C3AED,
        #6366F1
    ) !important;

    color: #FFFFFF !important;
    font-weight: 800 !important;
    border-radius: 12px;
    border-left: 4px solid #C4B5FD;
    box-shadow: 0 4px 18px rgba(124, 58, 237, 0.45);
    padding: 11px 13px;
}

/* HIGHLIGHTED MENU TEXT */

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
    color: #FFFFFF !important;
}

/* SMOOTH HOVER EFFECT */

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background-color: rgba(139, 92, 246, 0.25);
    transform: translateX(3px);
}

/* =====================================================
   BUTTONS
===================================================== */

.stButton > button {
    background: linear-gradient(
        135deg,
        #7C3AED,
        #6366F1
    );

    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 10px 22px;
    font-weight: 700;
    transition: 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(
        135deg,
        #6D28D9,
        #4F46E5
    );

    transform: translateY(-2px);

    box-shadow: 0 6px 18px rgba(124,58,237,0.35);
}

/* =====================================================
   INPUT FIELDS
===================================================== */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #211B38 !important;
    color: white !important;
    border: 1px solid #6D5AA8 !important;
    border-radius: 10px !important;
}

/* =====================================================
   SELECT BOX
===================================================== */

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background-color: #211B38;
    border: 1px solid #6D5AA8;
    border-radius: 10px;
    color: white;
}

/* =====================================================
   FILE UPLOADER
===================================================== */

[data-testid="stFileUploader"] {
    background: rgba(124,58,237,0.08);
    border: 1px dashed #A78BFA;
    border-radius: 15px;
    padding: 15px;
}

/* =====================================================
   METRIC CARDS
===================================================== */

[data-testid="stMetric"] {
    background: linear-gradient(
        135deg,
        #211B38,
        #30234F
    );

    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 16px;
    padding: 18px;

    box-shadow: 0 5px 18px rgba(0,0,0,0.2);
}

[data-testid="stMetricLabel"] {
    color: #C4B5FD !important;
}

[data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 800;
}

/* =====================================================
   DATAFRAME
===================================================== */

[data-testid="stDataFrame"] {
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 12px;
}

/* =====================================================
   TABS
===================================================== */

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #211B38;
    border-radius: 10px;
    color: #E9D5FF;
    padding: 10px 18px;
}

.stTabs [aria-selected="true"] {
    background-color: #6D28D9 !important;
    color: white !important;
}

/* =====================================================
   ALERTS
===================================================== */

[data-testid="stAlert"] {
    border-radius: 12px;
}

/* =====================================================
   WELCOME PAGE DESIGN
===================================================== */

.welcome-container {
    min-height: 65vh;

    display: flex;
    justify-content: center;
    align-items: center;

    text-align: center;

    background: linear-gradient(
        135deg,
        #17132C,
        #312E81,
        #6D28D9
    );

    border: 1px solid #A78BFA;
    border-radius: 25px;

    padding: 45px 25px;
    margin-top: 20px;

    box-shadow: 0 10px 35px rgba(124,58,237,0.25);
}

.welcome-content {
    max-width: 800px;
}

.welcome-tag {
    color: #DDD6FE;
    letter-spacing: 3px;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 25px;
}

.welcome-title {
    font-size: 48px;
    font-weight: 900;
    color: white;
    margin-bottom: 15px;
}

.welcome-title span {
    color: #C4B5FD;
}

.welcome-subtitle {
    font-size: 20px;
    color: #E9D5FF;
    margin-bottom: 25px;
}

.welcome-divider {
    width: 100px;
    height: 4px;
    background: #C084FC;
    margin: 20px auto;
    border-radius: 10px;
}

.welcome-description {
    color: #E2E8F0;
    font-size: 17px;
    line-height: 1.9;
}

.welcome-features {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 15px;
    margin-top: 30px;
}

.welcome-feature {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 12px;
    padding: 12px 18px;
    color: white;
}

.welcome-bottom {
    margin-top: 35px;
    color: #DDD6FE;
    font-size: 13px;
    letter-spacing: 3px;
    font-weight: bold;
}

.welcome-footer {
    text-align: center;
    color: #A78BFA;
    font-size: 12px;
    margin-top: 25px;
    line-height: 1.7;
}

/* ================= DASHBOARD DESIGN ================= */

.dashboard-banner {
    background: linear-gradient(120deg, #1E1B4B, #4C1D95, #7C3AED);
    border: 1px solid rgba(196, 181, 253, 0.4);
    border-radius: 22px;
    padding: 32px;
    margin: 15px 0 28px 0;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.22);
}

.dashboard-banner h1 {
    color: #FFFFFF !important;
    font-size: 32px !important;
    font-weight: 750 !important;
    margin-bottom: 12px;
}

.dashboard-banner p {
    color: #E9D5FF !important;
    font-size: 16px;
}

/* FEATURE CARDS */

.feature-card {
    background: linear-gradient(145deg, #211B38, #30234F);
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 18px;
    padding: 22px;
    min-height: 145px;
    margin-bottom: 18px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
    transition: all 0.25s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    border-color: #A78BFA;
    box-shadow: 0 10px 25px rgba(124, 58, 237, 0.2);
}

.feature-card h3 {
    color: #C4B5FD !important;
    font-size: 18px !important;
    font-weight: 650;
}

.feature-card p {
    color: #E2E8F0 !important;
    font-size: 14px;
    line-height: 1.6;
}

/* ================= OVERVIEW METRIC CARDS ================= */

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #211B38, #38245C);
    border: 1px solid rgba(167, 139, 250, 0.35);
    border-radius: 18px;
    padding: 22px 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
    transition: all 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    border-color: #A78BFA;
    box-shadow: 0 10px 25px rgba(124, 58, 237, 0.2);
}

div[data-testid="stMetricLabel"] {
    color: #C4B5FD !important;
    font-size: 15px !important;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 30px !important;
    font-weight: 750;
}

/* ================= INTERNSHIP TABLE DESIGN ================= */

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(167, 139, 250, 0.4);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

/* TABLE CONTAINER */

div[data-testid="stDataFrame"] > div {
    border-radius: 16px;
}

/* TABLE TOOLBAR */

div[data-testid="stDataFrame"] button {
    color: #C4B5FD !important;
}

/* TABLE BORDER */

div[data-testid="stDataFrame"] iframe {
    border-radius: 16px;
}

/* ================= DASHBOARD HEADINGS ================= */

.stApp h2, .stApp h3 {
    color: #C4B5FD !important;
    font-weight: 700;
}

/* ================= TIP BOX ================= */

div[data-testid="stAlert"] {
    background: linear-gradient(120deg, #211B38, #38245C);
    border: 1px solid rgba(167, 139, 250, 0.4);
    border-radius: 14px;
    color: #E9D5FF !important;
    padding: 16px;
}

/* ================= CAPTIONS ================= */

.stCaption {
    color: #A78BFA !important;
}

</style>
""", unsafe_allow_html=True)





# =========================================================
# 3. SESSION DATA
# =========================================================

if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True

if "student_profile" not in st.session_state:
    st.session_state.student_profile = {}

if "applications" not in st.session_state:
    st.session_state.applications = []

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []


# =========================================================
# 4. INTERNSHIP DATABASE
# =========================================================

@st.cache_data
def load_internships():
    return pd.read_csv("data/internships.csv")


internships = load_internships()

internship_records = []

for _, row in internships.iterrows():

    internship_records.append({
        "title": row["Role"],
        "company": row["Company"],
        "skills": [
            skill.strip()
            for skill in str(row["Skills"]).split(",")
        ],
        "domain": row["Domain"],
        "work_mode": row["Work Mode"],
        "experience_level": row["Experience Level"],
        "eligible_degree": row["Eligible Degree"],
        "eligible_year": row["Eligible Year"]
    })


# =========================================================
# 5. SKILL LIST
# =========================================================

skill_list = [
    "Python", "Java", "C", "C++", "SQL", "Excel",
    "Machine Learning", "Deep Learning", "TensorFlow",
    "PyTorch", "HTML", "CSS", "JavaScript", "React",
    "AWS", "Cloud", "Data Analysis", "Pandas", "NumPy",
    "Power BI", "Tableau", "Communication",
    "Problem Solving", "Natural Language Processing",
    "Artificial Intelligence"
]


# =========================================================
# 6. RESUME FUNCTIONS
# =========================================================

def extract_resume_text(uploaded_file):

    text = ""

    pdf = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text


def extract_skills(text):

    found_skills = []

    for skill in skill_list:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills


# =========================================================
# 7. PDF RECOMMENDATION REPORT
# =========================================================

def generate_recommendation_pdf(recommendations, student_name):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph("InternAlign AI", styles["Title"])
    )

    story.append(
        Paragraph(
            "Internship Recommendation Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"Student Name: {escape(str(student_name or 'Student'))}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"Report Date: {datetime.now().strftime('%d-%m-%Y')}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Ranked Internship Recommendations",
            styles["Heading2"]
        )
    )

    table_data = [[
        "Rank", "Internship", "Company", "Match", "Eligibility"
    ]]

    for item in recommendations:

        table_data.append([
            str(item.get("rank", "-")),
            Paragraph(
                escape(str(item.get("title", "N/A"))),
                styles["Normal"]
            ),
            Paragraph(
                escape(str(item.get("company", "N/A"))),
                styles["Normal"]
            ),
            f"{item.get('match_percentage', 0)}%",
            "Eligible" if item.get("eligible", False)
            else "Not Eligible"
        ])

    table = Table(
        table_data,
        colWidths=[35, 125, 115, 65, 100],
        repeatRows=1
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#5B21B6")),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("VALIGN", (0, 0), (-1, -1), "TOP"),

        ("PADDING", (0, 0), (-1, -1), 7),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#EDE9FE")])

    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Detailed Recommendation Information",
            styles["Heading2"]
        )
    )

    for item in recommendations:

        story.append(
            Paragraph(
                f"Rank {item.get('rank', '-')} - "
                f"{escape(str(item.get('title', 'Internship')))}",
                styles["Heading3"]
            )
        )

        story.append(
            Paragraph(
                f"Company: {escape(str(item.get('company', 'N/A')))}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"Match Score: {item.get('match_percentage', 0)}%",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                "Eligibility: "
                + (
                    "Eligible"
                    if item.get("eligible", False)
                    else "Not Eligible"
                ),
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                "Recommendation Reason: "
                + escape(str(item.get(
                    "recommendation_reason",
                    "Based on your profile."
                ))),
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                "Matched Skills: "
                + escape(", ".join(map(
                    str, item.get("matched_skills", [])
                ))),
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                "Skills to Improve: "
                + escape(", ".join(map(
                    str, item.get("missing_skills", [])
                ))),
                styles["Normal"]
            )
        )

        story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Note: Internship listings are sample demonstration "
            "data and are not verified live vacancies. "
            "ML predictions are based on illustrative synthetic training data.",
            styles["Italic"]
        )
    )

    document.build(story)
    buffer.seek(0)

    return buffer.getvalue()



# =========================================================
# 8. PREMIUM WELCOME PAGE
# =========================================================

if st.session_state.show_welcome:

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(
        "<h1 style='text-align:center; color:#C4B5FD;'>🎓 InternAlign AI</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<h3 style='text-align:center;'>Aligning Students with the Right Internship</h3>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        "<h4 style='text-align:center;'>WELCOME TO YOUR CAREER JOURNEY</h4>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='text-align:center; font-size:18px;'>
        Discover opportunities that match your skills.<br>
        Identify your skill gaps. Build your future.<br><br>
        Your journey towards the right internship starts here.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("✨ AI Recommendations")

    with col2:
        st.info("📊 Skill Gap Analysis")

    with col3:
        st.info("🚀 Career Growth")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("Get Started 🚀", use_container_width=True):
            st.session_state.show_welcome = False
            st.rerun()

    st.stop()
# =========================================================
# 9. SIDEBAR NAVIGATION
# =========================================================

st.sidebar.markdown("## 🎓 InternAlign AI")

st.sidebar.caption(
    "Aligning Students with the Right Internship"
)

st.sidebar.markdown("---")

pages = [
    "Dashboard",
    "My Profile",
    "Resume Analyzer",
    "Find Internships",
    "AI Recommendations",
    "Skill Gap Analysis",
    "What-if Simulator",
    "Project Matching",
    "Learning Roadmap",
    "Interview Preparation",
    "Application Tracker",
    "Analytics"
]

page = st.sidebar.radio(
    "Navigation",
    pages
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "InternAlign AI | Student Project"
)

profile = st.session_state.student_profile


# =========================================================
# 10. DASHBOARD
# =========================================================

if page == "Dashboard":

    student_name = profile.get("name", "Student")

    st.markdown(f"""
    <div class="dashboard-banner">
        <h1>🎓 Welcome to InternAlign AI</h1>
        <p>Hello, {escape(str(student_name))}!</p>
        <p>Your journey towards finding the right internship starts here.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 Your Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💼 Available Internships", len(internships))

    with col2:
        st.metric(
            "👤 Profile Status",
            "Completed" if profile else "Not Created"
        )

    with col3:
        st.metric(
            "📌 Applications",
            len(st.session_state.applications)
        )

    st.markdown("---")
    st.subheader("🚀 Explore InternAlign AI")

    feature_columns = st.columns(3)

    feature_cards = [
        ("👤", "Student Profile",
         "Manage your academic details, skills and career interests."),

        ("📄", "Resume Analyzer",
         "Extract technical skills from your uploaded resume."),

        ("🔍", "Internship Search",
         "Discover internships using search and filters."),

        ("🤖", "AI Recommendations",
         "Find ranked internships based on your profile."),

        ("📊", "Skill Gap Analysis",
         "Identify skills you need to improve."),

        ("🧪", "What-if Simulator",
         "Explore how additional skills affect your match."),

        ("💡", "Project Matching",
         "Discover projects related to your skills."),

        ("🗺️", "Learning Roadmap",
         "Follow structured learning steps."),

        ("🎤", "Interview Preparation",
         "Practice technical interview questions.")
    ]

    for index, feature in enumerate(feature_cards):

        with feature_columns[index % 3]:

            st.markdown(f"""
            <div class="feature-card">
                <h3>{feature[0]} {feature[1]}</h3>
                <p>{feature[2]}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📌 Available Internship Opportunities")

    st.dataframe(
        internships,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "These are sample demonstration internships, "
        "not verified live vacancies."
    )

    st.info(
        "💡 Tip: Complete your student profile and add your skills "
        "to receive better internship recommendations."
    )


# =========================================================
# 11. MY PROFILE
# =========================================================

elif page == "My Profile":

    st.title("👤 Student Profile")

    with st.form("profile_form"):

        name = st.text_input(
            "Full Name",
            value=profile.get("name", "")
        )

        email = st.text_input(
            "Email",
            value=profile.get("email", "")
        )

        college = st.text_input(
            "College",
            value=profile.get("college", "")
        )

        degree_options = [
            "B.E", "B.Tech", "B.Sc", "BCA", "MCA", "Other"
        ]

        degree = st.selectbox(
            "Degree",
            degree_options,
            index=(
                degree_options.index(profile["degree"])
                if profile.get("degree") in degree_options
                else 0
            )
        )

        branch = st.text_input(
            "Branch",
            value=profile.get("branch", "")
        )

        year_options = [
            "1st Year", "2nd Year", "3rd Year", "4th Year"
        ]

        year = st.selectbox(
            "Current Year",
            year_options,
            index=(
                year_options.index(profile["year"])
                if profile.get("year") in year_options
                else 0
            )
        )

        experience_options = [
            "Beginner", "Intermediate", "Advanced"
        ]

        experience_level = st.selectbox(
            "Your Experience Level",
            experience_options,
            index=(
                experience_options.index(
                    profile["experience_level"]
                )
                if profile.get("experience_level")
                in experience_options
                else 0
            )
        )

        cgpa = st.number_input(
            "CGPA",
            min_value=0.0,
            max_value=10.0,
            value=float(profile.get("cgpa", 0.0)),
            step=0.1
        )

        location = st.text_input(
            "Preferred Location",
            value=profile.get("location", "")
        )

        work_modes = ["Any", "Remote", "Hybrid", "On-site"]

        work_mode = st.selectbox(
            "Preferred Work Mode",
            work_modes,
            index=(
                work_modes.index(profile["work_mode"])
                if profile.get("work_mode") in work_modes
                else 0
            )
        )

        skills = st.multiselect(
            "Your Skills",
            skill_list,
            default=profile.get("skills", [])
        )

        domain_options = [
            "AI/ML", "Data Science",
            "Web Development", "Cloud"
        ]

        interests = st.multiselect(
            "Career Interests",
            domain_options,
            default=profile.get("interests", [])
        )

        submitted = st.form_submit_button("Save Profile")

        if submitted:

            st.session_state.student_profile = {
                "name": name,
                "email": email,
                "college": college,
                "degree": degree,
                "branch": branch,
                "year": year,
                "experience_level": experience_level,
                "cgpa": cgpa,
                "location": location,
                "work_mode": work_mode,
                "skills": skills,
                "interests": interests
            }

            st.success("Profile saved successfully!")


# =========================================================
# 12. RESUME ANALYZER
# =========================================================

elif page == "Resume Analyzer":

    st.title("📄 Resume Analyzer")

    st.write(
        "Upload your resume in PDF format to identify "
        "your technical skills."
    )

    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("Analyze Resume"):

            try:

                resume_text = extract_resume_text(uploaded_file)
                extracted_skills = extract_skills(resume_text)

                st.session_state.resume_text = resume_text
                st.session_state.resume_skills = extracted_skills

                st.success("Resume analyzed successfully!")

            except Exception as e:

                st.error(f"Unable to read resume: {e}")

    if st.session_state.resume_text:

        st.subheader("Detected Skills")

        if st.session_state.resume_skills:

            st.write(st.session_state.resume_skills)

            if st.button("Add Skills to My Profile"):

                profile_skills = profile.get("skills", [])

                updated_skills = list(set(
                    profile_skills + st.session_state.resume_skills
                ))

                profile["skills"] = updated_skills
                st.session_state.student_profile = profile

                st.success("Skills added to your profile!")

        else:

            st.info("No matching skills were detected.")

        with st.expander("View Extracted Resume Text"):
            st.text(st.session_state.resume_text)


# =========================================================
# 13. FIND INTERNSHIPS
# =========================================================

elif page == "Find Internships":

    st.title("🔍 Advanced Internship Search")

    st.write("Find internships based on your preferences.")

    search = st.text_input(
        "Search Company or Internship Role",
        placeholder="Example: Python Developer"
    )

    col1, col2 = st.columns(2)

    with col1:

        selected_domain = st.selectbox(
            "Choose Domain",
            ["All"] + sorted(
                internships["Domain"].dropna().unique().tolist()
            )
        )

    with col2:

        selected_mode = st.selectbox(
            "Choose Work Mode",
            ["All", "Remote", "Hybrid", "On-site"]
        )

    min_stipend = st.number_input(
        "Minimum Stipend (₹)",
        min_value=0,
        value=0,
        step=1000
    )

    filtered = internships.copy()

    if search:

        filtered = filtered[
            filtered["Company"].str.contains(
                search, case=False, na=False
            )
            |
            filtered["Role"].str.contains(
                search, case=False, na=False
            )
        ]

    if selected_domain != "All":
        filtered = filtered[
            filtered["Domain"] == selected_domain
        ]

    if selected_mode != "All":
        filtered = filtered[
            filtered["Work Mode"] == selected_mode
        ]

    filtered = filtered[
        filtered["Stipend"] >= min_stipend
    ]

    st.markdown("---")
    st.subheader("Matching Internships")

    st.metric("Internships Found", len(filtered))

    if not filtered.empty:

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning("No matching internships found.")


# =========================================================
# 14. AI RECOMMENDATIONS WITH ML MODEL
# =========================================================

elif page == "AI Recommendations":

    st.title("🤖 AI Internship Recommendations")

    st.write(
        "Discover internships ranked using your skills, "
        "career interests, work preferences and eligibility."
    )

    student_skills = profile.get("skills", [])
    preferred_domain = profile.get("interests", [])
    preferred_work_mode = profile.get("work_mode", "Any")
    student_degree = profile.get("degree", "Any")
    student_year = profile.get("year", "Any")
    experience_level = profile.get("experience_level", "Beginner")

    if not student_skills:

        st.warning(
            "Please add your skills in My Profile "
            "before generating recommendations."
        )

    else:

        recommendations = rank_internships(
            student_skills,
            internship_records,
            preferred_domain,
            preferred_work_mode,
            student_degree,
            student_year,
            experience_level
        )

        for index, item in enumerate(recommendations, start=1):

            item["rank"] = index

            item["is_top_match"] = (
                index == 1 and item.get("eligible", False)
            )

            try:

                ml_result = predict_suitability(
                    skill_match=float(
                        item.get("skill_match", 0) or 0
                    ),
                    domain_match=int(
                        float(item.get("domain_match", 0) or 0) > 0
                    ),
                    degree_match=int(
                        bool(item.get("degree_match", False))
                    ),
                    year_match=int(
                        bool(item.get("year_match", False))
                    ),
                    experience_match=int(
                        bool(item.get("experience_match", False))
                    )
                )

                item["ml_prediction"] = ml_result["prediction"]
                item["ml_probability"] = ml_result["probability"]

            except Exception as error:

                item["ml_prediction"] = None
                item["ml_probability"] = None

                st.error(
                    f"ML prediction error for "
                    f"{item.get('title', 'Internship')}: {error}"
                )

        st.subheader("📊 Your Recommendation Summary")

        eligible_count = sum(
            1 for item in recommendations
            if item.get("eligible", False)
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Recommendations", len(recommendations))

        with col2:
            st.metric("Eligible Internships", eligible_count)

        with col3:

            top_score = next(
                (
                    item.get("match_percentage", 0)
                    for item in recommendations
                    if item.get("is_top_match", False)
                ),
                None
            )

            st.metric(
                "Top Match Score",
                f"{top_score}%"
                if top_score is not None
                else "N/A"
            )

        st.markdown("---")

        if recommendations:

            pdf_data = generate_recommendation_pdf(
                recommendations,
                profile.get("name", "Student")
            )

            st.download_button(
                label="📥 Download Recommendation Report (PDF)",
                data=pdf_data,
                file_name="InternAlign_AI_Recommendation_Report.pdf",
                mime="application/pdf"
            )

        else:

            st.info("No recommendations available.")

        st.markdown("---")

        top_recommendation = next(
            (
                item for item in recommendations
                if item.get("is_top_match", False)
            ),
            None
        )

        if top_recommendation:

            top_title = escape(str(
                top_recommendation.get("title", "Internship")
            ))

            top_company = escape(str(
                top_recommendation.get("company", "N/A")
            ))

            top_score = max(
                0,
                min(
                    float(
                        top_recommendation.get(
                            "match_percentage", 0
                        )
                    ),
                    100
                )
            )

            st.markdown(f"""
            <div class="top-match-banner">
                <h2>🏆 Your Top Recommended Internship</h2>
                <h3>{top_title}</h3>
                <p>🏢 {top_company}</p>
                <h2>{top_score:.1f}% Match</h2>
                <p>You meet the eligibility requirements!</p>
            </div>
            """, unsafe_allow_html=True)

            st.progress(top_score / 100)

            st.info(
                top_recommendation.get(
                    "recommendation_reason",
                    "Recommended based on your profile."
                )
            )

        else:

            st.warning(
                "No eligible top recommendation found. "
                "Review your profile and eligibility requirements."
            )

        st.markdown("---")
        st.subheader("💼 All Internship Recommendations")

        if not recommendations:
            st.info("No recommendations available.")

        for item in recommendations:

            rank = item.get("rank", "-")
            title = str(item.get("title", "Internship"))
            company = str(item.get("company", "N/A"))

            score = max(
                0,
                min(float(item.get("match_percentage", 0)), 100)
            )

            eligible = item.get("eligible", False)
            is_top_match = item.get("is_top_match", False)

            with st.container(border=True):

                safe_title = escape(title)
                safe_company = escape(company)

                card_heading = (
                    f"🏆 Rank {rank} - {safe_title}"
                    if is_top_match
                    else f"#{rank} - {safe_title}"
                )

                st.markdown(f"""
                <div class="recommendation-header">
                    <h3>{card_heading}</h3>
                    <p>🏢 {safe_company}</p>
                    <div class="match-score">{score:.1f}%</div>
                    <div class="match-label">OVERALL MATCH SCORE</div>
                </div>
                """, unsafe_allow_html=True)

                st.progress(score / 100)

                st.subheader("🧠 Machine Learning Prediction")

                ml_prediction = item.get("ml_prediction")
                ml_probability = item.get("ml_probability")

                if ml_prediction is not None:

                    ml_col1, ml_col2 = st.columns(2)

                    with ml_col1:

                        if ml_prediction == 1:
                            st.success("Prediction: Suitable Internship")
                        else:
                            st.warning("Prediction: Not Suitable Internship")

                    with ml_col2:

                        st.metric(
                            "ML Suitability Probability",
                            f"{ml_probability}%"
                        )

                    st.caption(
                        "Generated using Logistic Regression and "
                        "illustrative synthetic training data. "
                        "This is not a real hiring probability."
                    )

                else:

                    st.warning("ML prediction is currently unavailable.")

                st.subheader("🎯 Eligibility Status")

                if eligible:

                    st.success(
                        item.get(
                            "eligibility_reason",
                            "You are eligible for this internship."
                        )
                    )

                else:

                    st.warning(
                        item.get(
                            "eligibility_reason",
                            "You do not meet all eligibility requirements."
                        )
                    )

                st.subheader("📊 Match Breakdown")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Skill Match",
                        f"{item.get('skill_match', 0)}%"
                    )

                with col2:
                    st.metric(
                        "Domain Match",
                        f"{item.get('domain_match', 0)}%"
                    )

                with col3:
                    st.metric(
                        "Work Mode Match",
                        f"{item.get('work_mode_match', 0)}%"
                    )

                st.subheader("✅ Your Matched Skills")

                matched_skills = item.get("matched_skills", [])

                if matched_skills:

                    matched_html = "".join(
                        f'<span class="skill-chip">{escape(str(skill))}</span>'
                        for skill in matched_skills
                    )

                    st.markdown(
                        matched_html,
                        unsafe_allow_html=True
                    )

                else:

                    st.info("No matching skills found.")

                st.subheader("📚 Skills You Can Improve")

                missing_skills = item.get("missing_skills", [])

                if missing_skills:

                    missing_html = "".join(
                        f'<span class="missing-chip">{escape(str(skill))}</span>'
                        for skill in missing_skills
                    )

                    st.markdown(
                        missing_html,
                        unsafe_allow_html=True
                    )

                else:

                    st.success("You have all the required skills!")

                st.subheader("💡 Why This Internship?")

                st.info(
                    item.get(
                        "recommendation_reason",
                        "This internship matches your profile."
                    )
                )

                with st.expander("🔍 View Detailed Eligibility"):

                    st.write(
                        "Degree:",
                        "Eligible" if item.get("degree_match", False)
                        else "Not eligible"
                    )

                    st.write(
                        "Engineering Year:",
                        "Eligible" if item.get("year_match", False)
                        else "Not eligible"
                    )

                    st.write(
                        "Experience Level:",
                        "Eligible" if item.get("experience_match", False)
                        else "Not eligible"
                    )


# =========================================================
# 15. SKILL GAP ANALYSIS
# =========================================================

elif page == "Skill Gap Analysis":

    st.title("📊 Skill Gap Analysis")

    student_skills = profile.get("skills", [])

    if not student_skills:

        st.warning("Please add your skills in My Profile.")

    else:

        st.write("Your current skills:")
        st.write(student_skills)

        selected_internship = st.selectbox(
            "Choose Internship",
            internships["Role"].tolist()
        )

        selected_row = internships[
            internships["Role"] == selected_internship
        ].iloc[0]

        required_skills = [
            skill.strip()
            for skill in str(selected_row["Skills"]).split(",")
        ]

        result = calculate_match(
            student_skills,
            required_skills
        )

        st.metric(
            "Skill Compatibility",
            f"{result['match_percentage']}%"
        )

        st.subheader("Matched Skills")

        st.write(
            result["matched_skills"]
            if result["matched_skills"]
            else "No matched skills"
        )

        st.subheader("Skills to Learn")

        st.write(
            result["missing_skills"]
            if result["missing_skills"]
            else "You have all required skills!"
        )


# =========================================================
# 16. WHAT-IF SIMULATOR
# =========================================================

elif page == "What-if Simulator":

    st.title("🧪 What-if Skill Simulator")

    student_skills = profile.get("skills", [])

    if not student_skills:

        st.warning("Please add your skills in My Profile.")

    else:

        st.write("Select additional skills to simulate.")

        additional_skills = st.multiselect(
            "Add Skills",
            [
                skill for skill in skill_list
                if skill not in student_skills
            ]
        )

        simulated_skills = list(
            set(student_skills + additional_skills)
        )

        selected_internship = st.selectbox(
            "Choose Internship",
            internships["Role"].tolist()
        )

        selected_row = internships[
            internships["Role"] == selected_internship
        ].iloc[0]

        required_skills = [
            skill.strip()
            for skill in str(selected_row["Skills"]).split(",")
        ]

        current_result = calculate_match(
            student_skills,
            required_skills
        )

        future_result = calculate_match(
            simulated_skills,
            required_skills
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Current Match",
                f"{current_result['match_percentage']}%"
            )

        with col2:

            st.metric(
                "Simulated Match",
                f"{future_result['match_percentage']}%",
                delta=round(
                    future_result["match_percentage"]
                    - current_result["match_percentage"],
                    2
                )
            )

        st.write("New skills added:", additional_skills)


# =========================================================
# 17. PROJECT MATCHING
# =========================================================

elif page == "Project Matching":

    st.title("💡 Project Matching")

    project_data = {
        "Python": [
            "Student Management System",
            "Library Management System"
        ],
        "Machine Learning": [
            "Student Performance Prediction",
            "House Price Prediction"
        ],
        "Deep Learning": [
            "Image Classification",
            "Object Detection"
        ],
        "SQL": [
            "Student Database System",
            "Inventory Management"
        ],
        "Web Development": [
            "Portfolio Website",
            "Online Library Website"
        ]
    }

    selected_skill = st.selectbox(
        "Select a skill",
        list(project_data.keys())
    )

    st.subheader("Suggested Projects")

    for project in project_data[selected_skill]:
        st.write("🚀 " + project)


# =========================================================
# 18. LEARNING ROADMAP
# =========================================================

elif page == "Learning Roadmap":

    st.title("🗺️ Learning Roadmap")

    roadmap = {
        "Python": [
            "Python Basics",
            "Variables and Data Types",
            "Loops and Functions",
            "Object-Oriented Programming",
            "Python Projects"
        ],
        "Machine Learning": [
            "Python Fundamentals",
            "NumPy and Pandas",
            "Data Visualization",
            "Machine Learning Algorithms",
            "Model Evaluation"
        ],
        "Deep Learning": [
            "Python Fundamentals",
            "Neural Networks",
            "TensorFlow or PyTorch",
            "CNN and RNN",
            "Deep Learning Projects"
        ],
        "Web Development": [
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "Build a Website"
        ],
        "SQL": [
            "SQL Basics",
            "SELECT and WHERE",
            "Joins",
            "Subqueries",
            "Database Projects"
        ]
    }

    selected_topic = st.selectbox(
        "Choose Learning Topic",
        list(roadmap.keys())
    )

    st.subheader("Your Learning Steps")

    for index, topic in enumerate(roadmap[selected_topic]):
        st.write(f"{index + 1}. {topic}")


# =========================================================
# 19. INTERVIEW PREPARATION
# =========================================================

elif page == "Interview Preparation":

    st.title("🎤 Interview Preparation")

    interview_questions = {
        "Python": [
            "What is Python?",
            "What are lists and tuples?",
            "What is a function?",
            "What is OOP?"
        ],
        "Machine Learning": [
            "What is Machine Learning?",
            "What is supervised learning?",
            "What is overfitting?",
            "What is model training?"
        ],
        "SQL": [
            "What is SQL?",
            "What is a primary key?",
            "What is a foreign key?",
            "Explain joins."
        ],
        "Web Development": [
            "What is HTML?",
            "What is CSS?",
            "What is JavaScript?",
            "What is responsive design?"
        ]
    }

    selected_topic = st.selectbox(
        "Select Interview Topic",
        list(interview_questions.keys())
    )

    st.subheader("Practice Questions")

    for index, question in enumerate(
        interview_questions[selected_topic]
    ):
        st.write(f"{index + 1}. {question}")

    answer = st.text_area("Write your practice answer")

    if st.button("Submit Practice Answer"):

        if answer.strip():
            st.success(
                "Your practice answer has been recorded on this page."
            )

        else:
            st.warning("Please enter an answer first.")


# =========================================================
# 20. APPLICATION TRACKER
# =========================================================

elif page == "Application Tracker":

    st.title("📌 Application Tracker")

    status_options = [
        "Applied",
        "Under Review",
        "Shortlisted",
        "Interview",
        "Selected",
        "Rejected"
    ]

    st.subheader("➕ Add New Application")

    with st.form("application_form"):

        company = st.text_input("Company Name")
        role = st.text_input("Internship Role")

        status = st.selectbox(
            "Application Status",
            status_options
        )

        submitted = st.form_submit_button("Add Application")

        if submitted:

            if company.strip() and role.strip():

                st.session_state.applications.append({
                    "Company": company.strip(),
                    "Role": role.strip(),
                    "Status": status
                })

                st.success("Application added successfully!")

            else:

                st.warning("Enter company name and role.")

    st.markdown("---")
    st.subheader("📋 My Applications")

    if st.session_state.applications:

        for index, application in enumerate(
            st.session_state.applications
        ):

            with st.container(border=True):

                st.markdown(
                    f"### 🏢 {application['Company']}"
                )

                st.write(
                    f"**Internship Role:** {application['Role']}"
                )

                current_status = application.get(
                    "Status", "Applied"
                )

                if current_status not in status_options:
                    current_status = "Applied"

                st.write(f"**Current Status:** {current_status}")

                selected_status = st.selectbox(
                    "Update Application Status",
                    status_options,
                    index=status_options.index(current_status),
                    key=f"application_status_{index}"
                )

                if st.button(
                    "Update Status",
                    key=f"update_application_{index}"
                ):

                    st.session_state.applications[index]["Status"] = (
                        selected_status
                    )

                    st.success(
                        f"Status updated to {selected_status}!"
                    )

                    st.rerun()

        st.markdown("---")
        st.subheader("📊 Application Summary")

        application_df = pd.DataFrame(
            st.session_state.applications
        )

        st.dataframe(
            application_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No applications added yet.")


# =========================================================
# 21. ANALYTICS DASHBOARD
# =========================================================

elif page == "Analytics":

    st.title("📈 Analytics Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Internships", len(internships))

    with col2:
        st.metric(
            "Total Applications",
            len(st.session_state.applications)
        )

    with col3:
        st.metric(
            "Available Domains",
            internships["Domain"].nunique()
        )

    st.markdown("---")
    st.subheader("Internships by Domain")

    domain_counts = (
        internships["Domain"]
        .value_counts()
        .reset_index()
    )

    domain_counts.columns = ["Domain", "Count"]

    fig = px.bar(
        domain_counts,
        x="Domain",
        y="Count",
        title="Internships by Domain",
        color="Domain",
        color_discrete_sequence=px.colors.sequential.Purples
    )

    fig.update_layout(
        paper_bgcolor="#11172B",
        plot_bgcolor="#11172B",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Internships by Work Mode")

    mode_counts = (
        internships["Work Mode"]
        .value_counts()
        .reset_index()
    )

    mode_counts.columns = ["Work Mode", "Count"]

    fig2 = px.pie(
        mode_counts,
        names="Work Mode",
        values="Count",
        title="Work Mode Distribution",
        color_discrete_sequence=px.colors.sequential.Purples
    )

    fig2.update_layout(
        paper_bgcolor="#11172B",
        font_color="white"
    )

    st.plotly_chart(fig2, use_container_width=True)

    if st.session_state.applications:

        st.subheader("Application Status")

        application_df = pd.DataFrame(
            st.session_state.applications
        )

        status_counts = (
            application_df["Status"]
            .value_counts()
            .reset_index()
        )

        status_counts.columns = ["Status", "Count"]

        fig3 = px.bar(
            status_counts,
            x="Status",
            y="Count",
            title="Application Status Distribution",
            color="Status",
            color_discrete_sequence=px.colors.sequential.Purples
        )

        fig3.update_layout(
            paper_bgcolor="#11172B",
            plot_bgcolor="#11172B",
            font_color="white"
        )

        st.plotly_chart(fig3, use_container_width=True)


# =========================================================
# 22. SIDEBAR FOOTER
# =========================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Built with Python, Streamlit and Scikit-learn"
)

st.sidebar.caption(
    "InternAlign AI | Student Project"
)
