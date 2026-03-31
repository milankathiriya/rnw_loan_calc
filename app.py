import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Northern Arc – Loan Calculator",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="collapsed",
) 

# ─── MASTER DATA ────────────────────────────────────────────────────────────
COURSES = {
    "AI/ML & Data Science":                         {"fee": 130000, "duration": 16},
    "Animation & VFX 2Year":                        {"fee": 180000, "duration": 24},
    "Career in Graphic & Video Editing":            {"fee": 115000, "duration": 14},
    "Career in UI/UX & Graphic Design":             {"fee": 115000, "duration": 14},
    "Career in Full Stack Web Development":         {"fee": 115000, "duration": 14},
    "Career in Video Editing & 3D Animation":       {"fee": 115000, "duration": 14},
    "Business Administration & Commerce":           {"fee":  85000, "duration": 12},
    "Graphic Design_AI":                            {"fee":  45000, "duration":  5},
    "UI/UX & Graphic Design_AI":                    {"fee": 180000, "duration": 24},
    "Video Editing & 3D Animation_AI":              {"fee":  90000, "duration": 10},
    "Web Front End Development":                    {"fee":  75000, "duration":  8},
    "Digital Marketing":                            {"fee":  32000, "duration":  3},
    "Data Analysis":                                {"fee":  49500, "duration":  6},
    "Web Back End Development":                     {"fee":  75000, "duration":  8},
    "UI/UX Design_AI":                              {"fee":  45000, "duration":  5},
    "Video Editing_AI":                             {"fee":  45000, "duration":  5},
    "Software Development Foundation With JS":      {"fee":  49500, "duration":  6},
    "Software Development Foundation With Java":    {"fee":  49500, "duration":  6},
    "Career in Sales & Marketing":                  {"fee":  50000, "duration":  6},
    "Career in Professional Development":           {"fee":  40000, "duration":  6},
    "Cyber Security":                               {"fee":  37000, "duration":  6},
    "C, C++, Python":                               {"fee":  29500, "duration":  5},
    "Career in Accounting and Taxation":            {"fee":  35000, "duration":  6},
    "C,C++,Core Java":                              {"fee":  25000, "duration":  5},
    "Project Training":                             {"fee":  29500, "duration":  4},
    "Software Development Foundation With Python":  {"fee":  49500, "duration":  6},
    "C,C++":                                        {"fee":  15000, "duration":  3},
}

TENOR_TABLE = {
     6: {"subvention": 5.15,  "roi_flat": 0.00},
     9: {"subvention": 7.15,  "roi_flat": 0.00},
    12: {"subvention": 9.10,  "roi_flat": 0.00},
    15: {"subvention": 9.10,  "roi_flat": 5.71},
    18: {"subvention": 9.10,  "roi_flat": 7.71},
    21: {"subvention": 9.10,  "roi_flat": 9.72},
    24: {"subvention": 9.10,  "roi_flat": 11.71},
}

# ─── FORMULAS ───────────────────────────────────────────────────────────────
def calculate(loan_amount: float, tenure: int) -> dict:
    t   = TENOR_TABLE[tenure]
    sub = t["subvention"]
    roi = t["roi_flat"]
    subvention_amount = loan_amount * sub / 100
    net_disbursement  = loan_amount - subvention_amount
    interest_amount   = loan_amount * (roi / 100) * (tenure / 12)
    total_payable     = loan_amount + interest_amount
    monthly_emi       = total_payable / tenure
    return {
        "subvention_pct":    sub,
        "roi_flat":          roi,
        "subvention_amount": subvention_amount,
        "net_disbursement":  net_disbursement,
        "interest_amount":   interest_amount,
        "total_payable":     total_payable,
        "monthly_emi":       monthly_emi,
    }

# BUG FIX: use flat-rate amortization (not reducing-balance)
def build_amortization(loan_amount: float, roi_flat: float, tenure: int, monthly_emi: float) -> pd.DataFrame:
    rows, balance     = [], loan_amount
    total_interest    = loan_amount * (roi_flat / 100) * (tenure / 12)
    monthly_interest  = total_interest / tenure
    monthly_principal = monthly_emi - monthly_interest
    for m in range(1, tenure + 1):
        opening = balance
        closing = max(round(opening - monthly_principal, 2), 0)
        balance = closing
        rows.append({
            "Month":               m,
            "Opening Balance (₹)": round(opening, 2),
            "EMI (₹)":             round(monthly_emi, 2),
            "Principal (₹)":       round(monthly_principal, 2),
            "Interest (₹)":        round(monthly_interest, 2),
            "Closing Balance (₹)": closing,
        })
    return pd.DataFrame(rows)

# ─── GLOBAL CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #FFFFFF !important;
    color: #333333;
}
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton,
#stDecoration { display: none !important; visibility: hidden !important; }

.block-container {
    padding-top: 0.5rem !important;
    margin-top: 0rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}
[data-testid="stHeader"] { display: none !important; }

/* ── RESPONSIVE HEADER ── */
.app-header {
    background: linear-gradient(135deg, #c0392b 0%, #E04B4B 60%, #e85d5d 100%);
    border-radius: 14px; padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem; display: flex; align-items: center;
    justify-content: space-between; gap: 1rem;
    box-shadow: 0 6px 24px rgba(224,75,75,0.25);
    flex-wrap: wrap;
}
.app-header-logo {
    background: #FFFFFF; border-radius: 10px;
    padding: 10px 20px; display:flex; align-items:center; justify-content:center;
    flex-shrink: 0; box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    min-width: 200px; max-width: 300px;
}
.app-header-logo img { height: 130px; width: auto; }
.app-header-center { flex: 1; min-width: 180px; }
.app-header-center h1 { font-family:'Poppins',sans-serif; font-size:clamp(1rem, 3vw, 1.55rem); color:#FFFFFF; margin:0; line-height:1.2; font-weight:700; }
.app-header-center p  { color:rgba(255,255,255,0.85); font-size:clamp(0.65rem, 1.5vw, 0.8rem); margin:5px 0 0; }
.app-header-badge { 
    background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.35);
    color:#FFFFFF; font-size:0.68rem; font-weight:600; padding:4px 12px;
    border-radius:20px; letter-spacing:0.06em; text-transform:uppercase;
    white-space:nowrap; flex-shrink:0;
}

/* ── FILTER PANEL ── */
.filter-panel {
    background:#FFFFFF; border:1.5px solid #EFE6E6; border-radius:14px;
    padding:1.4rem 1.5rem; box-shadow:0 4px 18px rgba(224,75,75,0.08); height:fit-content;
}
.filter-panel-title {
    font-family:'Poppins',sans-serif; font-size:1rem; font-weight:700; color:#FFFFFF;
    background:#E04B4B; margin:-1.4rem -1.5rem 1.2rem; padding:0.8rem 1.5rem;
    border-radius:12px 12px 0 0; display:flex; align-items:center; gap:8px;
}
.filter-step { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#E04B4B; margin:1rem 0 4px; }
.filter-info { background:#F5F0F0; border-left:3px solid #E04B4B; border-radius:0 8px 8px 0; padding:0.65rem 0.9rem; font-size:0.78rem; color:#333333; line-height:1.6; margin:6px 0 4px; }
.filter-info b { color:#E04B4B; }
.filter-divider { border:none; border-top:1px solid #EFE6E6; margin:1rem 0; }
.filter-footer { font-size:0.68rem; color:#777777; text-align:center; margin-top:1rem; line-height:1.5; }

.badge-zero     { display:inline-block; background:#e6f4ea; color:#1e7e34; border:1px solid #b7dfbe; border-radius:20px; font-size:0.7rem; font-weight:700; padding:3px 10px; letter-spacing:0.04em; margin-bottom:12px; }
.badge-interest { display:inline-block; background:#fff4e5; color:#D32F2F; border:1px solid #fcd19c; border-radius:20px; font-size:0.7rem; font-weight:700; padding:3px 10px; letter-spacing:0.04em; margin-bottom:12px; }

/* ── RESPONSIVE CARDS ── */
.cards-row { display:grid; gap:12px; margin-bottom:12px; }
.cards-4 { grid-template-columns:repeat(4,1fr); }
.cards-3 { grid-template-columns:repeat(3,1fr); }

/* Tablet: 2 columns */
@media (max-width: 900px) {
    .cards-4 { grid-template-columns:repeat(2,1fr); }
    .cards-3 { grid-template-columns:repeat(2,1fr); }
    .app-header-badge { display: none; }
}

/* Mobile: 1 column */
@media (max-width: 540px) {
    .cards-4 { grid-template-columns:1fr; }
    .cards-3 { grid-template-columns:1fr; }
    .app-header { flex-direction: column; align-items: flex-start; padding: 0.9rem 1rem; }
    .app-header-logo { max-width: 100%; }
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
}

.card { background:#FFFFFF; border:1.5px solid #EFE6E6; border-radius:12px; padding:1rem 1.2rem; box-shadow:0 2px 10px rgba(51,51,51,0.06); transition:box-shadow 0.2s,transform 0.2s; }
.card:hover { box-shadow:0 4px 18px rgba(224,75,75,0.12); transform:translateY(-2px); }
.card .c-label { font-size:0.68rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:#777777; margin-bottom:6px; }
.card .c-value { font-size:clamp(1.1rem, 2.5vw, 1.45rem); font-weight:700; color:#333333; line-height:1.1; }
.card .c-note  { font-size:0.7rem; color:#777777; margin-top:4px; }

.card-hero { background:#E04B4B; border:none; border-radius:12px; padding:1rem 1.2rem; box-shadow:0 6px 20px rgba(224,75,75,0.30); }
.card-hero .c-label { color:rgba(255,255,255,0.75); }
.card-hero .c-value { color:#FFFFFF; font-size:clamp(1.3rem, 3vw, 1.8rem); }
.card-hero .c-note  { color:rgba(255,255,255,0.60); }
.red-num { color:#D32F2F; font-weight:700; }

.sec-head { font-family:'Poppins',sans-serif; font-size:1rem; font-weight:700; color:#333333; border-left:4px solid #E04B4B; padding-left:10px; margin:1.4rem 0 0.7rem; }

.info-box { background:#F5F0F0; border:1px solid #EFE6E6; border-radius:8px; padding:0.75rem 1rem; font-size:0.78rem; color:#333333; line-height:1.7; margin-top:6px; }
.info-box b { color:#D32F2F; }

div[data-testid="stTabs"] button { font-weight:600; color:#555555; font-size:0.82rem; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#E04B4B !important; border-bottom-color:#E04B4B !important; }

/* ── RESPONSIVE TABLE ── */
.styled-table { width:100%; border-collapse:collapse; font-size:0.82rem; border-radius:10px; overflow:hidden; }
.styled-table thead tr { background:#E04B4B; color:#FFFFFF; font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; }
.styled-table thead th { padding:10px 12px; text-align:left; white-space:nowrap; }
.styled-table tbody tr:nth-child(odd)  { background:#FFFFFF; }
.styled-table tbody tr:nth-child(even) { background:#F5F0F0; }
.styled-table tbody td { padding:8px 12px; color:#333333; border-bottom:1px solid #EFE6E6; white-space:nowrap; }
.styled-table tbody tr:hover { background:#EFE6E6; }
.styled-table .status-upcoming { color:#2F6F9F; font-weight:600; }
.styled-table .status-ongoing  { color:#444444; font-weight:600; }
.selected-row td { background:#ffe0e0 !important; font-weight:700; }

.table-scroll { overflow-x:auto; -webkit-overflow-scrolling:touch; border-radius:10px; border:1px solid #EFE6E6; }

.stDownloadButton button { background:#E04B4B !important; color:#FFFFFF !important; border:none !important; border-radius:8px !important; font-weight:600 !important; padding:0.4rem 1.2rem !important; margin-top:8px; }
.stDownloadButton button:hover { background:#c93a3a !important; }

/* ── RESPONSIVE STREAMLIT COLUMNS ── */
@media (max-width: 768px) {
    [data-testid="column"] { min-width: 100% !important; }
    div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
}
</style>
""", unsafe_allow_html=True)

# ─── HEADER ─────────────────────────────────────────────────────────────────
LOGO_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAFSBlADASIAAhEBAxEB/8QAHQABAAIDAQEBAQAAAAAAAAAAAAcIBAUGAwIJAf/EAFsQAAEDAwEDBQwGBAoHBgQHAAABAgMEBREGBxIhCBMxQVEVFhciVVZhcYGRk9EUGDKUodJCorGyIzdSYnJzgpKzwTM2Y3R1lcI0NTiE4fAkJUN2ZGWDtNPi8f/EABwBAQEAAgMBAQAAAAAAAAAAAAABAgMEBQYHCP/EAD0RAQABAwEEBgcFCAIDAQAAAAABAgMRBAUSITETFUFRUqEGFlRhcYGRBxQisfAXMkKSwdHS4VPiI4LxJP/aAAwDAQACEQMRAD8AuWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//Z"

st.markdown(f"""
<div class="app-header">
  <div class="app-header-logo">
    <img src="data:image/png;base64,{LOGO_B64}" alt="Red & White Skill Education" 
         style="height:90px; width:auto; object-fit:contain; display:block;" />
  </div>
  <div class="app-header-center">
    <h1>    Loan Calculator</h1>
    <p>Education Finance &nbsp;·&nbsp; Student EMI Planner &nbsp;·&nbsp; Subvention &amp; Interest Calculator</p>
  </div>
  <span class="app-header-badge">Red & White Education Pvt. Ltd.</span>
</div>
""", unsafe_allow_html=True)

# ─── LAYOUT ──────────────────────────────────────────────────────────────────
filter_col, main_col = st.columns([1, 2.1], gap="medium")

# ════════════════════════════════════════════════════════════════════════════
# RIGHT — FILTER PANEL
# ════════════════════════════════════════════════════════════════════════════
with filter_col:
    st.markdown("""
    <div class="filter-panel">
      <div class="filter-panel-title">⚙️ Loan Configuration</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="filter-step">Step 1 — Select Course</div>', unsafe_allow_html=True)
    course_name = st.selectbox("Course", list(COURSES.keys()), label_visibility="collapsed", key="course_sel")
    course     = COURSES[course_name]
    course_fee = course["fee"]
    duration   = course["duration"]

    st.markdown(f"""
    <div class="filter-info">
      📚 <b>{course_name}</b><br>
      💰 Course Fee: <b>₹{course_fee:,.0f}</b><br>
      ⏱ Duration: <b>{duration} months</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="filter-divider">', unsafe_allow_html=True)

    st.markdown('<div class="filter-step">Step 2 — Enter Loan Amount (₹)</div>', unsafe_allow_html=True)
    loan_amount = st.number_input(
        "Loan Amount",
        min_value=1000,
        max_value=course_fee,
        value=min(round(course_fee * 0.90), course_fee),
        step=1000,
        label_visibility="collapsed",
        key="loan_amt",
    )

    if loan_amount > course_fee:
        st.error(f"⚠️ Loan amount cannot exceed course fee ₹{course_fee:,.0f}")
        st.stop()

    pct_used = round(loan_amount / course_fee * 100, 1)
    st.markdown(f"""
    <div class="filter-info">
      <span class="red-num">{pct_used}%</span> of course fee
      &nbsp;·&nbsp; Max: ₹{course_fee:,.0f}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="filter-divider">', unsafe_allow_html=True)

    st.markdown('<div class="filter-step">Step 3 — Select EMI Tenure</div>', unsafe_allow_html=True)
    if duration <= 12:
      allowed_tenures = [t for t in TENOR_TABLE.keys() if t <= 18]  
    else:
      allowed_tenures = list(TENOR_TABLE.keys())
    tenure = st.selectbox(
    "Tenure",
    allowed_tenures,   # FIXED
    index=min(3, len(allowed_tenures)-1),
    format_func=lambda x: f"{x} Months",
    label_visibility="collapsed",
    key="tenure_sel",
)
    tv         = TENOR_TABLE[tenure]
    type_label = "Zero-Cost EMI ✅" if tv["roi_flat"] == 0 else "Interest-Bearing 📈"
    st.markdown(f"""
    <div class="filter-info">
      Subvention %: <b>{tv['subvention']}%</b><br>
      Student ROI (Flat): <b>{tv['roi_flat']}%</b><br>
      Type: <b>{type_label}</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="filter-footer">
      <br>
      All figures indicative · Subject to credit approval
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# LEFT — MAIN CONTENT 
# ════════════════════════════════════════════════════════════════════════════
with main_col:
    res = calculate(loan_amount, tenure)

    if res["roi_flat"] == 0:
        st.markdown('<span class="badge-zero">✅ Zero-Cost EMI — No Interest Charged</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="badge-interest">📈 Interest @ {res["roi_flat"]}% Flat p.a. · {tenure} Months</span>', unsafe_allow_html=True)

    # ── Row 1: 4 cards ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center;">
    <div class="cards-row cards-4">
      <div class="card card-hero">
        <div class="c-label">Monthly EMI</div>
        <div class="c-value">₹{res['monthly_emi']:,.2f}</div>
        <div class="c-note">for {tenure} months</div>
      </div>
      <div class="card">
        <div class="c-label">Student ROI % (Flat Rate)</div>
        <div class="c-value" style="color:#2F6F9F;">{res['roi_flat']}%</div>
        <div class="c-note">flat rate per annum</div>
      </div>
      <div class="card">
        <div class="c-label">Student Interest Amount</div>
        <div class="c-value"><span class="red-num">₹{res['interest_amount']:,.2f}</span></div>
        <div class="c-note">P × ROI% × (n/12)</div>
      </div>
      
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Row 2: 3 cards ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center;">
    <div class="cards-row cards-3">
    <div class="card">
        <div class="c-label">Total Payable by Customer</div>
        <div class="c-value">₹{res['total_payable']:,.2f}</div>
        <div class="c-note">Principal + Interest</div>
    </div>
    <div class="card">
        <div class="c-label">Loan Amount (Principal)</div>
        <div class="c-value">₹{loan_amount:,.0f}</div>
        <div class="c-note">of ₹{course_fee:,.0f} course fee</div>
      </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🔄 Tenor Comparison", "📅 Amortization Schedule", "📐 Formulas"])

    # ── TAB 1: Tenor Comparison + Plotly Chart ───────────────────────────────
    with tab1:
        st.markdown('<div class="sec-head">🔄 All Tenors Comparison</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span style="font-size:.78rem;color:#777777;">Loan: <b>₹{loan_amount:,.0f}</b> · Course: <b>{course_name}</b></span>',
            unsafe_allow_html=True,
        )

        rows_html2 = ""
        for t, tv2 in TENOR_TABLE.items():
            r2  = calculate(loan_amount, t)
            sel = 'class="selected-row"' if t == tenure else ""
            typ = '<span class="status-upcoming">Zero-Cost ✅</span>' if tv2["roi_flat"] == 0 \
                  else '<span class="status-ongoing">Interest-Bearing</span>'
            rows_html2 += f"""
            <tr {sel}>
              <td><b>{t} Months</b></td>
              <td>{tv2['subvention']}%</td>
              <td style="color:#2F6F9F;">{tv2['roi_flat']}%</td>
              <td class="red-num">₹{r2['interest_amount']:,.2f}</td>
              <td>₹{r2['total_payable']:,.2f}</td>
              <td class="red-num">₹{r2['monthly_emi']:,.2f}</td>
              <td>₹{r2['subvention_amount']:,.2f}</td>
              <td>₹{r2['net_disbursement']:,.2f}</td>
              <td>{typ}</td>
            </tr>"""

        st.markdown(f"""
        <div class="table-scroll">
        <table class="styled-table">
          <thead>
            <tr>
              <th>Tenure</th><th>Subvention %</th><th>ROI % Flat</th>
              <th>Interest Amt</th><th>Total Payable</th><th>Monthly EMI</th>
              <th>Subvention Amt</th><th>Net Disburse</th><th>Type</th>
            </tr>
          </thead>
          <tbody>{rows_html2}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        # PLOTLY BAR CHART — EMI by Tenure
        # ════════════════════════════════════════════════════════════════════
        st.markdown(
            '<div class="sec-head" style="margin-top:1.4rem;">📊 EMI by Tenure — Visual Comparison</div>',
            unsafe_allow_html=True,
        )

        tenors     = list(TENOR_TABLE.keys())
        emi_vals   = [calculate(loan_amount, t)["monthly_emi"] for t in tenors]
        x_labels   = [f"{t} Months" for t in tenors]

        bar_colors = [
            "#E04B4B" if t == tenure else "#BFC8D6"
            for t in tenors
        ]
        border_colors = [
            "#b83232" if t == tenure else "#9aaabb"
            for t in tenors
        ]
        hover_texts = [
            (
                f"<b>{t} Months</b><br>"
                f"Monthly EMI : <b>₹{emi:,.2f}</b><br>"
                f"ROI (Flat)  : <b>{TENOR_TABLE[t]['roi_flat']}%</b><br>"
                f"Type        : <b>{'Zero-Cost ✅' if TENOR_TABLE[t]['roi_flat'] == 0 else 'Interest-Bearing'}</b>"
                + ("<br><br>⭐ <b>Currently Selected</b>" if t == tenure else "")
            )
            for t, emi in zip(tenors, emi_vals)
        ]

        fig = go.Figure()

        # Main bars
        fig.add_trace(go.Bar(
            x=x_labels,
            y=emi_vals,
            marker=dict(
                color=bar_colors,
                line=dict(color=border_colors, width=1.5),
                opacity=0.95,
            ),
            text=[f"₹{e:,.0f}" for e in emi_vals],
            textposition="outside",
            textfont=dict(size=12, color="#333333", family="Inter, sans-serif"),
            hovertext=hover_texts,
            hoverinfo="text",
            hoverlabel=dict(
                bgcolor="#FFFFFF",
                bordercolor="#E04B4B",
                font=dict(size=12, color="#222222", family="Inter, sans-serif"),
            ),
            cliponaxis=False,
        ))

        # Dotted reference line at selected EMI
        sel_emi = emi_vals[tenors.index(tenure)]
        fig.add_hline(
            y=sel_emi,
            line=dict(color="#E04B4B", width=1.8, dash="dot"),
            annotation_text=f"  Selected: ₹{sel_emi:,.0f}",
            annotation_position="top left",
            annotation_font=dict(size=11, color="#E04B4B", family="Inter, sans-serif"),
        )

        # "Selected" arrow annotation on the chosen bar
        fig.add_annotation(
            x=f"{tenure} Months",
            y=sel_emi,
            text="<b>Selected</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=2,
            arrowcolor="#E04B4B",
            ax=0,
            ay=-52,
            font=dict(size=11, color="#E04B4B", family="Inter, sans-serif"),
            bgcolor="rgba(224,75,75,0.10)",
            bordercolor="#E04B4B",
            borderwidth=1.2,
            borderpad=5,
        )

        fig.update_layout(
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#FFFFFF",
            height=340,
            margin=dict(t=60, b=40, l=60, r=20),
            xaxis=dict(
                title=dict(text="Tenure (Months)", font=dict(size=12, color="#555", family="Inter, sans-serif")),
                tickfont=dict(size=12, color="#333", family="Inter, sans-serif"),
                showgrid=False,
                zeroline=False,
                linecolor="#EFE6E6",
                linewidth=1.5,
            ),
            yaxis=dict(
                title=dict(text="Monthly EMI (₹)", font=dict(size=12, color="#555", family="Inter, sans-serif")),
                tickfont=dict(size=11, color="#555", family="Inter, sans-serif"),
                tickformat=",.0f",
                tickprefix="₹",
                gridcolor="#EEEEEE",
                gridwidth=1,
                zeroline=False,
                range=[0, max(emi_vals) * 1.25],
            ),
            showlegend=False,
            bargap=0.35,
            font=dict(family="Inter, sans-serif"),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Chart legend strip
        st.markdown("""
        <div style="display:flex;align-items:center;gap:24px;font-size:0.74rem;
                    color:#666666;margin-top:-10px;padding:4px 2px 10px;">
          <span>
            <span style="display:inline-block;width:13px;height:13px;background:#E04B4B;
                         border-radius:3px;margin-right:5px;vertical-align:middle;"></span>
            Selected Tenure
          </span>
          <span>
            <span style="display:inline-block;width:13px;height:13px;background:#BFC8D6;
                         border-radius:3px;margin-right:5px;vertical-align:middle;"></span>
            Other Tenures
          </span>
          <span style="margin-left:auto;font-style:italic;">
            💡 Lower tenure = Higher EMI &nbsp;·&nbsp; Higher tenure = Lower EMI but more interest
          </span>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 2: Amortization ─────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="sec-head">📅 Month-by-Month Repayment Schedule</div>', unsafe_allow_html=True)
        amort = build_amortization(loan_amount, res["roi_flat"], tenure, res["monthly_emi"])

        rows_html = ""
        for _, row in amort.iterrows():
            m = int(row["Month"])
            rows_html += f"""
            <tr>
              <td>{m}</td>
              <td>₹{row['Opening Balance (₹)']:,.2f}</td>
              <td class="red-num">₹{row['EMI (₹)']:,.2f}</td>
              <td>₹{row['Principal (₹)']:,.2f}</td>
              <td style="color:#2F6F9F;">₹{row['Interest (₹)']:,.2f}</td>
              <td>₹{row['Closing Balance (₹)']:,.2f}</td>
            </tr>"""

        st.markdown(f"""
        <div class="table-scroll" style="max-height:400px; overflow-y:auto;">
        <table class="styled-table">
          <thead>
            <tr>
              <th>Month</th><th>Opening Bal.</th><th>EMI (₹)</th>
              <th>Principal</th><th>Interest</th><th>Closing Bal.</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-box" style="margin-top:10px;">
          📌 <b>Totals</b> &nbsp;·&nbsp;
          Total EMI: <b>₹{res['monthly_emi'] * tenure:,.2f}</b> &nbsp;|&nbsp;
          Total Principal: <b>₹{loan_amount:,.2f}</b> &nbsp;|&nbsp;
          Total Interest: <b class="red-num">₹{res['interest_amount']:,.2f}</b>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            "⬇️ Download Schedule (CSV)",
            amort.to_csv(index=False).encode(),
            "amortization_schedule.csv", "text/csv",
        )

    # ── TAB 3: Formulas ─────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="sec-head">📐 Formula Reference</div>', unsafe_allow_html=True)
        st.markdown(f"""
**Current Inputs:**
- Loan Amount **(P)** = ₹{loan_amount:,.0f}
- Subvention % = {res['subvention_pct']}%
- Student ROI % Flat **(r)** = {res['roi_flat']}% p.a.
- Tenure **(n)** = {tenure} months

---
**1. Partner Subvention Amount**
```
= P × (Subvention% ÷ 100)
= {loan_amount:,.0f} × ({res['subvention_pct']} ÷ 100)
= ₹{res['subvention_amount']:,.2f}
```
**2. Net Disbursement**
```
= Loan Amount − Subvention Amount
= {loan_amount:,.0f} − {res['subvention_amount']:,.2f}
= ₹{res['net_disbursement']:,.2f}
```
**3. Student Interest Amount**
```
= P × (r ÷ 100) × (n ÷ 12)
= {loan_amount:,.0f} × ({res['roi_flat']} ÷ 100) × ({tenure} ÷ 12)
= ₹{res['interest_amount']:,.2f}
```
> ℹ️ Tenors 6, 9, 12 months → ROI = 0% → Interest = ₹0

**4. Total Payable by Customer**
```
= Loan Amount + Student Interest Amount
= {loan_amount:,.0f} + {res['interest_amount']:,.2f}
= ₹{res['total_payable']:,.2f}
```
**5. Monthly EMI**
```
= Total Payable ÷ Tenure Months
= {res['total_payable']:,.2f} ÷ {tenure}
= ₹{res['monthly_emi']:,.2f}
```

---
**Northern Arc Tenor Rate Table**

| Tenure | Subvention % | Student ROI (Flat) | Type |
|--------|-------------|---------------------|------|
| 6 months  | 5.15% | 0.00% | Zero-Cost EMI |
| 9 months  | 7.15% | 0.00% | Zero-Cost EMI |
| 12 months | 9.10% | 0.00% | Zero-Cost EMI |
| 15 months | 9.10% | 5.71% | Interest-Bearing |
| 18 months | 9.10% | 7.71% | Interest-Bearing |
| 21 months | 9.10% | 9.72% | Interest-Bearing |
| 24 months | 9.10% | 11.71% | Interest-Bearing |
""")

# ─── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#EFE6E6; margin-top:2rem;">
<p style="text-align:center; font-size:0.72rem; color:#777777;">
  · Education Finance Division · All figures are indicative and subject to credit approval.
</p>
""", unsafe_allow_html=True)
