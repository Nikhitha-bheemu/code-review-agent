import os
import streamlit as st
import pandas as pd
from detector import detect_bugs
from ga_engine import evolve_fix
from validator import validate_fix
from memory import save_fix, recall_similar_fix
from report import generate_report

# Page Config
st.set_page_config(
    page_title="Code Review Agent",
    page_icon="🤖",
    layout="wide"
)

# Sample Buggy Codes
SAMPLE_BUG_1 = """def divide_numbers(a, b):
    # Potential division by zero bug
    return a / b
"""

SAMPLE_BUG_2 = """def read_config(filepath):
    # Resource leak: file not closed
    f = open(filepath, 'r')
    data = f.read()
    return data
"""

SAMPLE_BUG_3 = """def factorial(n):
    # Infinite recursion if n is negative
    if n == 0:
        return 1
    return n * factorial(n - 1)
"""

# Initialize session state variables
if "code" not in st.session_state:
    st.session_state["code"] = ""
if "input_code" not in st.session_state:
    st.session_state["input_code"] = ""
if "bugs" not in st.session_state:
    st.session_state["bugs"] = None
if "fixes" not in st.session_state:
    st.session_state["fixes"] = {}
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

# --- SIDEBAR ---
st.sidebar.title("Configuration")

api_key = st.sidebar.text_input(
    "Anthropic API Key",
    type="password",
    value=st.session_state["api_key"],
    help="Enter your Anthropic API Key to use Claude"
)

if api_key:
    st.session_state["api_key"] = api_key
    st.sidebar.success("✅ API Key Set")

generations = st.sidebar.slider("GA Generations", min_value=3, max_value=5, value=3)
pop_size = st.sidebar.slider("GA Population Size", min_value=4, max_value=6, value=4)

# --- HEADER ---
st.title("🤖 Autonomous Code Review & Bug Fix Agent")
st.caption("Powered by Claude AI + Genetic Algorithms")

# Create Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Code Input",
    "🐛 Bug Detection",
    "🧬 Fix Evolution (GA)",
    "📄 Results & Report"
])

# --- TAB 1: Code Input ---
with tab1:
    st.subheader("Python Code to Review")
    
    st.write("Load a sample buggy code snippet:")
    col_s1, col_s2, col_s3 = st.columns(3)
    if col_s1.button("Load Bug 1: Division by Zero"):
        st.session_state["input_code"] = SAMPLE_BUG_1
    if col_s2.button("Load Bug 2: File Not Closed"):
        st.session_state["input_code"] = SAMPLE_BUG_2
    if col_s3.button("Load Bug 3: Infinite Recursion"):
        st.session_state["input_code"] = SAMPLE_BUG_3
        
    code_input = st.text_area(
        "Enter/Edit Python Code",
        value=st.session_state["input_code"],
        height=300
    )
    
    if st.button("🔍 Start Analysis"):
        if not st.session_state["api_key"]:
            st.warning("Please enter your Anthropic API Key in the sidebar.")
        elif not code_input.strip():
            st.warning("Please enter some Python code to analyze.")
        else:
            st.session_state["code"] = code_input
            st.session_state["fixes"] = {}  # Clear previous fixes
            
            try:
                with st.spinner("Analyzing code for bugs..."):
                    detected = detect_bugs(code_input, st.session_state["api_key"])
                st.session_state["bugs"] = detected
                st.success(f"Analysis complete! Found {len(detected)} bug(s).")
            except Exception as e:
                st.error(f"Error during bug detection: {e}")

# --- TAB 2: Bug Detection ---
with tab2:
    bugs = st.session_state["bugs"]
    if bugs is None:
        st.info("No bugs detected yet. Go to 'Code Input' and click 'Start Analysis'.")
    elif len(bugs) == 0:
        st.success("No bugs found in the code!")
    else:
        st.subheader("Bug Detection Summary")
        st.metric("Total Bugs Found", len(bugs))
        
        # Calculate severity counts
        severities = [b.get("severity", "low").lower() for b in bugs]
        counts = {"high": 0, "medium": 0, "low": 0}
        for s in severities:
            if s in counts:
                counts[s] += 1
                
        df_sev = pd.DataFrame({
            "Severity": ["High", "Medium", "Low"],
            "Count": [counts["high"], counts["medium"], counts["low"]]
        }).set_index("Severity")
        
        st.bar_chart(df_sev)
        
        # Bug details table
        display_bugs = []
        for bug in bugs:
            sev = bug.get("severity", "low").lower()
            emoji_sev = "🟢 Low"
            if sev == "high":
                emoji_sev = "🔴 High"
            elif sev == "medium":
                emoji_sev = "🟡 Medium"
                
            display_bugs.append({
                "Line": bug.get("line_number"),
                "Type": bug.get("bug_type"),
                "Severity": emoji_sev,
                "Description": bug.get("description")
            })
            
        st.dataframe(pd.DataFrame(display_bugs), use_container_width=True)

# --- TAB 3: Fix Evolution (GA) ---
with tab3:
    bugs = st.session_state["bugs"]
    if bugs is None or len(bugs) == 0:
        st.info("No bugs available to evolve fixes for. Please run the analysis first.")
    else:
        st.subheader("Genetic Algorithm Fix Evolution")
        
        for idx, bug in enumerate(bugs):
            desc = bug.get("description", "")
            st.markdown(f"### Bug {idx+1}: {bug.get('bug_type')} (Line {bug.get('line_number')})")
            st.write(f"**Description:** {desc}")
            
            # Check memory or check session state
            if idx not in st.session_state["fixes"]:
                try:
                    recalled = recall_similar_fix(desc)
                    if recalled:
                        st.session_state["fixes"][idx] = recalled
                        st.success("✨ Similar fix recalled from memory!")
                except Exception as e:
                    st.error(f"Error checking memory: {e}")
                    
            if idx in st.session_state["fixes"]:
                fix = st.session_state["fixes"][idx]
                
                try:
                    val = validate_fix(st.session_state["code"], fix)
                    st.metric("Validation Quality Score", f"{val.get('score', 0.0):.2f}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Original Code:**")
                        st.code(st.session_state["code"], language="python")
                    with c2:
                        st.markdown("**Evolved Fix:**")
                        st.code(fix, language="python")
                        
                    st.markdown("**Unified Diff:**")
                    st.code(val.get("diff", ""), language="diff")
                except Exception as e:
                    st.error(f"Error validating evolved fix: {e}")
            else:
                if st.button(f"🧬 Evolve Fix for Bug {idx+1}", key=f"btn_evolve_{idx}"):
                    if not st.session_state["api_key"]:
                        st.warning("Please set the Anthropic API Key in the sidebar.")
                    else:
                        try:
                            with st.spinner("Evolving fix using Genetic Algorithm..."):
                                progress_bar = st.progress(0.0)
                                progress_bar.progress(0.2)
                                evolved = evolve_fix(st.session_state["code"], bug, st.session_state["api_key"])
                                progress_bar.progress(0.8)
                                save_fix(desc, evolved)
                                progress_bar.progress(1.0)
                                
                            st.session_state["fixes"][idx] = evolved
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error evolving fix: {e}")

# --- TAB 4: Results & Report ---
with tab4:
    bugs = st.session_state["bugs"]
    fixes_dict = st.session_state["fixes"]
    
    if bugs is None or len(bugs) == 0:
        st.info("No review reports available yet.")
    elif len(fixes_dict) < len(bugs):
        st.warning(f"Please evolve fixes for all detected bugs first (Evolved {len(fixes_dict)}/{len(bugs)}).")
    else:
        st.subheader("Review Report & Recommendations")
        
        # Determine overall recommendation status
        severities = [b.get("severity", "low").lower() for b in bugs]
        if "high" in severities:
            st.error("🚨 Final Recommendation: CRITICAL (High severity bugs detected)")
        elif "medium" in severities:
            st.warning("⚠️ Final Recommendation: NEEDS FIX (Medium severity bugs detected)")
        else:
            st.success("✅ Final Recommendation: PASS (Only low severity bugs detected)")
            
        fixes_list = [fixes_dict[idx] for idx in range(len(bugs))]
        
        try:
            with st.spinner("Generating final reports..."):
                md_report = generate_report(st.session_state["code"], bugs, fixes_list)
            st.markdown(md_report)
            
            # Offer PDF download button if file exists
            if os.path.exists("code_review_report.pdf"):
                with open("code_review_report.pdf", "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name="code_review_report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error generating report: {e}")
