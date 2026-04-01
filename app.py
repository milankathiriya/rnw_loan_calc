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
    # emi_max = max allowed EMI tenure per NSDC Student EMI Apply column
    "Animation & VFX 2Year":                        {"fee": 180000, "duration": 24, "emi_max": 24},
    "Career in Graphic & Video Editing":            {"fee": 115000, "duration": 14, "emi_max": 24},
    "Career in UI/UX & Graphic Design":             {"fee": 115000, "duration": 14, "emi_max": 24},
    "AI/ML & Data Science":                         {"fee": 130000, "duration": 16, "emi_max": 24},
    "Career in Full Stack Web Development":         {"fee": 115000, "duration": 14, "emi_max": 24},
    "Career in Video Editing & 3D Animation":       {"fee": 115000, "duration": 14, "emi_max": 24},
    "Business Administration & Commerce":           {"fee":  85000, "duration": 12, "emi_max": 24},
    "Graphic Design_AI":                            {"fee":  45000, "duration":  5, "emi_max": 18},
    "UI/UX & Graphic Design_AI":                    {"fee": 180000, "duration": 24, "emi_max": 24},
    "Video Editing & 3D Animation_AI":              {"fee":  90000, "duration": 10, "emi_max": 24},
    "Web Front End Development":                    {"fee":  75000, "duration":  8, "emi_max": 18},
    "Data Analysis":                                {"fee":  49500, "duration":  6, "emi_max": 18},
    "Web Back End Development":                     {"fee":  75000, "duration":  8, "emi_max": 18},
    "UI/UX Design_AI":                              {"fee":  45000, "duration":  5, "emi_max": 18},
    "Video Editing_AI":                             {"fee":  45000, "duration":  5, "emi_max": 18},
    "Software Development Foundation With JS":      {"fee":  49500, "duration":  6, "emi_max": 18},
    "Software Development Foundation With Java":    {"fee":  49500, "duration":  6, "emi_max": 18},
    "Career in Sales & Marketing":                  {"fee":  50000, "duration":  6, "emi_max": 18},
    "Career in Professional Development":           {"fee":  40000, "duration":  6, "emi_max": 18},
    "Cyber Security":                               {"fee":  37000, "duration":  6, "emi_max": 18},
    "C, C++, Python":                               {"fee":  29500, "duration":  5, "emi_max": 18},
    "Career in Accounting and Taxation":            {"fee":  35000, "duration":  6, "emi_max": 18},
    "C,C++,Core Java":                              {"fee":  25000, "duration":  5, "emi_max": 18},
    "Project Training":                             {"fee":  29500, "duration":  4, "emi_max": 18},
    "Software Development Foundation With Python":  {"fee":  49500, "duration":  6, "emi_max": 18},
    "C,C++":                                        {"fee":  15000, "duration":  3, "emi_max": 18},
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
.app-header-center { flex: 1; min-width: 180px; text-align: center; }
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

st.markdown("""
<div class="app-header">
  <div class="app-header-center">
    <h1>Loan Calculator</h1>
    <p>Education Finance &nbsp;·&nbsp; Student EMI Planner &nbsp;·&nbsp; Subvention &amp; Interest Calculator</p>
  </div>
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

    emi_max = course["emi_max"]
    st.markdown(f"""
    <div class="filter-info">
      📚 <b>{course_name}</b><br>
      💰 Course Fee: <b>₹{course_fee:,.0f}</b><br>
      ⏱ Duration: <b>{duration} months</b><br>
      📋 Max EMI Tenure: <b>{emi_max} months</b>
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
    # Allowed tenures: based on NSDC Student EMI Apply column (emi_max per course)
    allowed_tenures = [t for t in TENOR_TABLE.keys() if t <= emi_max]
    if not allowed_tenures:
        allowed_tenures = [min(TENOR_TABLE.keys())]
    tenure = st.selectbox(
        "Tenure",
        allowed_tenures,
        index=min(len(allowed_tenures) - 1, len(allowed_tenures) - 1),
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
        <div class="c-note">Principal    + Interest</div>
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
        for t in allowed_tenures:
            tv2 = TENOR_TABLE[t]
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

        tenors     = allowed_tenures
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
