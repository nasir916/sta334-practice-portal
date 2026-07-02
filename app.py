import streamlit as st
import json
import os
import time
import datetime
import requests
import base64
import grader
import pdf_generator

# Page Config
st.set_page_config(
    page_title="STA334 R Practice Portal",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Workspace Paths
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(WORKSPACE_DIR, "config.json")
DATA_PATH = os.path.join(WORKSPACE_DIR, "practice_sets.json")

# Load configuration (like Google Apps Script URL)
def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"google_apps_script_url": ""}

def save_config(config):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Failed to save config: {e}")

# Load Practice Sets Data
def load_practice_data():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading questions data: {e}")
    return []

# Custom CSS for Premium Design (Glassmorphism & Neon Accent)
def inject_custom_css():
    st.markdown("""
        <style>
        /* Base Background Styling */
        .stApp {
            background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1e1b4b 100%);
            color: #f1f5f9;
            font-family: 'Outfit', 'Inter', -apple-system, sans-serif;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.9) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
        }
        
        /* Custom Cards */
        .premium-card {
            background: rgba(30, 41, 59, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }
        
        .subq-card {
            background: rgba(15, 23, 42, 0.35);
            border-left: 4px solid #4f46e5;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 0 8px 8px 0;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        /* Question Graded Cards */
        .correct-card {
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.05);
        }
        
        .partial-card {
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 0 15px rgba(245, 158, 11, 0.05);
        }
        
        .incorrect-card {
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.05);
        }
        
        /* Input Textareas styling */
        textarea {
            background-color: #0f172a !important;
            color: #38bdf8 !important;
            font-family: 'Fira Code', 'Courier New', monospace !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 6px !important;
        }
        
        textarea:focus {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
        }
        
        /* Custom buttons styling */
        div.stButton > button {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 10px 24px !important;
            border-radius: 8px !important;
            transition: all 0.25s ease !important;
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.25) !important;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
        }
        
        /* Table rendering styling */
        .dataframe {
            width: 100% !important;
            border-collapse: collapse !important;
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            font-size: 13px !important;
        }
        
        .dataframe th {
            background: rgba(30, 41, 59, 0.8) !important;
            color: #ffffff !important;
            padding: 8px 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            text-align: left !important;
        }
        
        .dataframe td {
            padding: 8px 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #e2e8f0 !important;
        }
        
        /* Float Timer alignment */
        .timer-box {
            position: fixed;
            top: 60px;
            right: 20px;
            z-index: 100;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize Session State Variables
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "student_id" not in st.session_state:
    st.session_state.student_id = ""
if "selected_set_idx" not in st.session_state:
    st.session_state.selected_set_idx = None
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "session_finished" not in st.session_state:
    st.session_state.session_finished = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0
if "answers" not in st.session_state:
    st.session_state.answers = {} # key: (q_no, sub_no), value: text
if "grading_results" not in st.session_state:
    st.session_state.grading_results = {} # key: (q_no, sub_no), value: dict(score, max_marks, feedback)
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = ""
if "upload_status" not in st.session_state:
    st.session_state.upload_status = ""

# Load configurations
config = load_config()
practice_data = load_practice_data()

# Inject styling
inject_custom_css()

# Timer parameters
TIME_LIMIT_MINUTES = 60
TIME_LIMIT_SECONDS = TIME_LIMIT_MINUTES * 60

# Render Timer component in sidebar
def render_timer():
    if st.session_state.session_active and st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        time_left = max(0, int(TIME_LIMIT_SECONDS - elapsed))
        
        # Check for auto-submit
        if time_left <= 0:
            st.session_state.elapsed_time = TIME_LIMIT_SECONDS
            st.session_state.session_active = False
            st.session_state.session_finished = True
            submit_quiz()
            st.rerun()
            
        # JS-based ticking timer
        with st.sidebar:
            st.components.v1.html(f"""
                <div style="
                    background: rgba(30, 41, 59, 0.95);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 10px;
                    text-align: center;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    color: #f1f5f9;
                ">
                    <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 4px;">Time Remaining</div>
                    <div id="countdown" style="font-size: 22px; font-weight: bold; color: #10b981; font-family: monospace; letter-spacing: 0.5px;">--:--</div>
                </div>
                
                <script>
                    (function() {{
                        var timeLeft = {time_left};
                        var countdownEl = document.getElementById('countdown');
                        if (!countdownEl) return;
                        
                        function updateTimer() {{
                            if (timeLeft <= 0) {{
                                countdownEl.innerHTML = "00:00";
                                countdownEl.style.color = "#ef4444";
                                clearInterval(timerInterval);
                                return;
                            }}
                            var mins = Math.floor(timeLeft / 60);
                            var secs = timeLeft % 60;
                            countdownEl.innerHTML = 
                                (mins < 10 ? "0" + mins : mins) + ":" + 
                                (secs < 10 ? "0" + secs : secs);
                            
                            if (timeLeft <= 300) {{ // less than 5 mins
                                countdownEl.style.color = "#f43f5e";
                            }} else if (timeLeft <= 900) {{ // less than 15 mins
                                countdownEl.style.color = "#fb923c";
                            }} else {{
                                countdownEl.style.color = "#10b981";
                            }}
                            timeLeft--;
                        }}
                        
                        updateTimer();
                        var timerInterval = setInterval(updateTimer, 1000);
                    }})();
                </script>
            """, height=72)

        
        # Display student info in sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Student Name:** {st.session_state.student_name}")
        st.sidebar.markdown(f"**Student ID:** {st.session_state.student_id}")
        st.sidebar.markdown(f"**Practice Set:** Set {st.session_state.selected_set_idx}")
        
        if st.sidebar.button("⚠️ Submit & Finish Now"):
            st.session_state.elapsed_time = int(time.time() - st.session_state.start_time)
            st.session_state.session_active = False
            st.session_state.session_finished = True
            submit_quiz()
            st.rerun()

# Grade all questions and generate PDF
def submit_quiz():
    set_idx = st.session_state.selected_set_idx
    set_data = next((s for s in practice_data if s['practice_set'] == set_idx), None)
    if not set_data:
        return
        
    results = {}
    for q in set_data['questions']:
        q_no = q['question_no']
        for sq in q['subquestions']:
            sub_no = sq['sub_no']
            ans = st.session_state.answers.get((q_no, sub_no), "")
            score, max_m, feedback = grader.grade_question(set_idx, q_no, sub_no, ans)
            results[(q_no, sub_no)] = {
                "score": score,
                "max_marks": max_m,
                "feedback": feedback
            }
            
    st.session_state.grading_results = results
    
    # Generate PDF
    pdf_path = pdf_generator.generate_student_pdf(
        student_name=st.session_state.student_name,
        student_id=st.session_state.student_id,
        set_idx=set_idx,
        questions_data=set_data['questions'],
        student_answers=st.session_state.answers,
        grading_results=results,
        output_dir=WORKSPACE_DIR
    )
    st.session_state.pdf_path = pdf_path
    
    # Try Auto-Upload
    upload_url = config.get("google_apps_script_url", "").strip()
    if upload_url:
        try:
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
                
            base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
            filename = os.path.basename(pdf_path)
            
            payload = {
                "filename": filename,
                "mimeType": "application/pdf",
                "base64": base64_pdf
            }
            
            # Send file to Google Apps Script Web App
            response = requests.post(upload_url, json=payload, timeout=20)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("success"):
                    st.session_state.upload_status = "SUCCESS"
                else:
                    st.session_state.upload_status = f"FAILED: {res_json.get('error')}"
            else:
                st.session_state.upload_status = f"FAILED: Server returned status {response.status_code}"
        except Exception as e:
            st.session_state.upload_status = f"FAILED: {str(e)}"
    else:
        st.session_state.upload_status = "NOT_CONFIGURED"

# Render Table Helper
def render_table(asset_table):
    headers = asset_table['headers']
    rows = asset_table['rows']
    
    # Render using st.markdown HTML for beautiful styling
    html = '<table class="dataframe"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for r in rows:
        html += '<tr>'
        for cell in r:
            html += f'<td>{cell}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)


# ==========================================
# MAIN WORKFLOW
# ==========================================

# 1. REGISTRATION PAGE
if not st.session_state.session_active and not st.session_state.session_finished:
    st.markdown("<h1 style='text-align: center;'>📊 STA334 R Practice Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; margin-top: -15px;'>Introduce yourself and select a practice set to begin your exercise.</p>", unsafe_allow_html=True)
    
    with st.form("registration_form"):
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.subheader("Student Details")
        
        name = st.text_input("Full Name (as in Identity Card):", placeholder="e.g. AHMAD BIN ABDULLAH").upper()
        student_id = st.text_input("Student ID Number:", placeholder="e.g. 2024123456")
        
        st.subheader("Select Practice Exercise")
        # Build practice set options from parsed JSON
        options = {}
        for s in practice_data:
            s_idx = s['practice_set']
            options[s_idx] = f"Practice Set {s_idx} - {s['focus'].replace('Focus: ', '')}"
            
        selected_set = st.selectbox(
            "Choose Practice Set:",
            options=list(options.keys()),
            format_func=lambda x: options[x]
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Submit Button
        submitted = st.form_submit_button("🚀 Start Practice Set")
        if submitted:
            if not name or not student_id:
                st.error("Please fill in both Name and Student ID before starting.")
            else:
                st.session_state.student_name = name
                st.session_state.student_id = student_id
                st.session_state.selected_set_idx = selected_set
                st.session_state.session_active = True
                st.session_state.start_time = time.time()
                st.session_state.current_question_idx = 0
                st.session_state.answers = {}
                st.session_state.grading_results = {}
                st.session_state.session_finished = False
                st.rerun()

    # Admin Configurations in Sidebar / Expander
    st.markdown("---")
    with st.expander("⚙️ Lecturer Admin & Upload Setup"):
        st.markdown("""
        Configure the **Google Apps Script Web App URL** to enable automated file submissions directly to your Google Drive folder.
        """)
        
        new_url = st.text_input(
            "Google Apps Script Web App URL:",
            value=config.get("google_apps_script_url", ""),
            placeholder="https://script.google.com/macros/s/.../exec"
        )
        
        if st.button("Save Admin Configuration"):
            config["google_apps_script_url"] = new_url.strip()
            save_config(config)
            st.success("Google Apps Script URL saved successfully!")

# 2. QUIZ SESSION PAGE
elif st.session_state.session_active:
    render_timer()
    
    set_idx = st.session_state.selected_set_idx
    set_data = next((s for s in practice_data if s['practice_set'] == set_idx), None)
    
    if set_data:
        st.title(set_data['title'])
        st.caption(f"{set_data['course']} | {set_data['focus']}")
        st.info(set_data['info'])
        
        questions = set_data['questions']
        q_idx = st.session_state.current_question_idx
        q = questions[q_idx]
        
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.subheader(f"Question {q['question_no']} ({q['total_marks']} Marks)")
        
        # Render question context
        if q['context']:
            st.markdown(f"<div style='font-style: italic; color: #e2e8f0; line-height: 1.5; margin-bottom: 15px;'>{q['context']}</div>", unsafe_allow_html=True)
            
        # Render question level assets (Tables)
        for asset in q.get('assets', []):
            if asset['type'] == 'table':
                st.write("**Reference Table/Dataset:**")
                render_table(asset)
                st.markdown("<br>", unsafe_allow_html=True)
                
        # Render subquestions
        for sq in q['subquestions']:
            sub_no = sq['sub_no']
            key = (q['question_no'], sub_no)
            
            st.markdown("<div class='subq-card'>", unsafe_allow_html=True)
            st.markdown(f"**{sub_no}) {sq['text']}** <span style='color: #a78bfa;'>({sq['marks']} marks)</span>", unsafe_allow_html=True)
            
            # Subquestion assets (e.g., expected output tables or charts/plots)
            for asset in sq.get('assets', []):
                if asset['type'] == 'table':
                    st.write("**Expected Output Table:**")
                    render_table(asset)
                elif asset['type'] == 'image':
                    # Load and display local extracted image
                    img_p = os.path.join(WORKSPACE_DIR, asset['path'])
                    if os.path.exists(img_p):
                        st.image(img_p, caption="Reference Plot/Chart")
            
            # Answer input
            val = st.text_area(
                "Type your R code or answer below:",
                value=st.session_state.answers.get(key, ""),
                key=f"input_{q['question_no']}_{sub_no}"
            )
            st.session_state.answers[key] = val
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Navigation Buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if q_idx > 0:
                if st.button("⬅️ Previous Question"):
                    st.session_state.current_question_idx -= 1
                    st.rerun()
        with col3:
            if q_idx < len(questions) - 1:
                if st.button("Next Question ➡️"):
                    st.session_state.current_question_idx += 1
                    st.rerun()
            else:
                if st.button("🏁 Finish Practice"):
                    st.session_state.elapsed_time = int(time.time() - st.session_state.start_time)
                    st.session_state.session_active = False
                    st.session_state.session_finished = True
                    submit_quiz()
                    st.rerun()

# 3. RESULTS & FEEDBACK REVIEW PAGE
elif st.session_state.session_finished:
    st.balloons()
    
    set_idx = st.session_state.selected_set_idx
    set_data = next((s for s in practice_data if s['practice_set'] == set_idx), None)
    
    st.markdown("<h1 style='text-align: center;'>🏆 Practice Session Completed!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Your answers have been graded. Review your performance report below.</p>", unsafe_allow_html=True)
    
    # Calculate Score
    results = st.session_state.grading_results
    total_score = sum(res['score'] for res in results.values())
    total_max = sum(res['max_marks'] for res in results.values())
    pct = (total_score / total_max * 100) if total_max > 0 else 0.0
    
    # Score Card
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.2) 0%, rgba(124, 58, 237, 0.2) 100%);
            border: 2px solid rgba(124, 58, 237, 0.4);
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px 0 rgba(124, 58, 237, 0.15);
            backdrop-filter: blur(10px);
        ">
            <h3 style="margin: 0; color: #c084fc;">Overall Performance Score</h3>
            <div style="font-size: 48px; font-weight: 800; color: #ffffff; margin: 10px 0;">
                {total_score:.1f} <span style="font-size: 24px; color: #a78bfa; font-weight: 500;">/ {total_max:.1f} Marks</span>
            </div>
            <div style="font-size: 20px; font-weight: 600; color: #34d399;">
                Percentage: {pct:.1f}%
            </div>
            <div style="font-size: 13px; color: #cbd5e1; margin-top: 8px;">
                Time Elapsed: {st.session_state.elapsed_time // 60}m {st.session_state.elapsed_time % 60}s
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # PDF Download Section
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.subheader("📁 Performance Report PDF & Submission")
    
    # Load PDF file for download button
    pdf_filename = f"{st.session_state.student_name} - {st.session_state.student_id}.pdf"
    if os.path.exists(st.session_state.pdf_path):
        with open(st.session_state.pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        st.download_button(
            label="⬇️ Download Official PDF Report",
            data=pdf_bytes,
            file_name=pdf_filename,
            mime="application/pdf"
        )
    else:
        st.warning("PDF file could not be generated. Please consult the lecturer.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Google Drive upload status box
    if st.session_state.upload_status == "SUCCESS":
        st.success("✅ Success! Your PDF report has been automatically uploaded to the Lecturer's Google Drive.")
    elif st.session_state.upload_status == "NOT_CONFIGURED":
        st.info("ℹ️ Automated upload is disabled (Lecturer Google Apps Script URL is not set). Please submit manually.")
        st.markdown(f"""
            <a href="https://drive.google.com/drive/folders/1BaEn7x30pS3TG2GOcjbBTil-oJldIt0x?usp=sharing" target="_blank">
                <button style="
                    background: #2563eb;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 600;
                    cursor: pointer;
                ">
                    📂 Open Google Drive Folder
                </button>
            </a>
            <span style="font-size: 12px; margin-left: 10px; color: #cbd5e1;">Download the PDF above and drag-and-drop it into the folder.</span>
        """, unsafe_allow_html=True)
    else:
        st.error(f"❌ Automated upload failed ({st.session_state.upload_status}). Please submit manually.")
        st.markdown(f"""
            <a href="https://drive.google.com/drive/folders/1BaEn7x30pS3TG2GOcjbBTil-oJldIt0x?usp=sharing" target="_blank">
                <button style="
                    background: #2563eb;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 600;
                    cursor: pointer;
                ">
                    📂 Open Google Drive Folder
                </button>
            </a>
            <span style="font-size: 12px; margin-left: 10px; color: #cbd5e1;">Download the PDF above and drag-and-drop it into the folder.</span>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Review Question Details
    st.subheader("🔍 Review Question Details & Answers")
    if set_data:
        for q in set_data['questions']:
            q_no = q['question_no']
            st.markdown(f"### Question {q_no}")
            
            for sq in q['subquestions']:
                sub_no = sq['sub_no']
                key = (q_no, sub_no)
                res = results.get(key, {"score": 0.0, "max_marks": 0, "feedback": ""})
                
                score = res['score']
                max_m = res['max_marks']
                student_ans = st.session_state.answers.get(key, "").strip()
                ref_ans = sq.get('reference_answer', "").strip()
                
                # Choose styling card based on grade
                card_class = "correct-card" if score == max_m else ("partial-card" if score > 0 else "incorrect-card")
                status_icon = "✔" if score == max_m else ("⚠" if score > 0 else "✘")
                
                st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
                st.markdown(f"**{status_icon} Part {sub_no}) {sq['text']}**", unsafe_allow_html=True)
                
                # Show answers side-by-side or stacked
                st.write("**Your Answer:**")
                st.code(student_ans if student_ans else "(Left blank)", language="R")
                
                # If wrong or partial, show reference answer
                if score < max_m:
                    st.write("**Reference Answer:**")
                    st.code(ref_ans, language="R")
                    
                st.markdown(f"**Marks:** {score:.1f} / {max_m:.1f} &nbsp;&nbsp;|&nbsp;&nbsp; **Feedback:** *{res['feedback']}*", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
    st.markdown("---")
    if st.button("🔄 Practice Another Set"):
        # Reset session state except configuration
        st.session_state.session_active = False
        st.session_state.session_finished = False
        st.session_state.selected_set_idx = None
        st.session_state.answers = {}
        st.session_state.grading_results = {}
        st.session_state.current_question_idx = 0
        st.session_state.elapsed_time = 0
        st.session_state.pdf_path = ""
        st.session_state.upload_status = ""
        st.rerun()
