import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path
import re

# =============================================================================
# SET PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="AI Employee v2.0 - Command Center",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS (Attractive & Professional Theme)
# =============================================================================
st.markdown("""
<style>
    /* Main Background and Text */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Custom Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #58a6ff;
        font-size: 2.5rem;
    }
    
    /* Tier Headers */
    .tier-header {
        background: linear-gradient(90deg, #1f6feb 0%, #161b22 100%);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #58a6ff;
    }
    
    /* Feature Tags */
    .feature-tag {
        background-color: #21262d;
        color: #8b949e;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.8rem;
        border: 1px solid #30363d;
        margin-right: 5px;
    }
    
    /* Logs and Code Blocks */
    .stCodeBlock {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
    }

    /* Success/Error/Info Boxes Customization */
    .stAlert {
        border-radius: 8px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONFIGURATION & DATA HELPERS
# =============================================================================
BASE_DIR = Path(__file__).parent.parent.resolve()
VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
LOGS_DIR = BASE_DIR / "Logs"
SKILLS_DIR = BASE_DIR / ".claude" / "skills"
ACTION_LOG = LOGS_DIR / "action.log"
ERRORS_LOG = LOGS_DIR / "errors.log"
RETRY_QUEUE = LOGS_DIR / "retry_queue.json"
RALPH_STATE = SKILLS_DIR / "ralph-wiggum" / "state.json"

def load_json(path):
    if not path.exists(): return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_task_counts():
    counts = {
        "Inbox": len(list((VAULT_DIR / "Inbox").glob("*.md"))),
        "Needs_Action": len(list((VAULT_DIR / "Needs_Action").glob("*.md"))),
        "Needs_Approval": len(list((VAULT_DIR / "Needs_Approval").glob("*.md"))),
        "Done": len(list((VAULT_DIR / "Done").glob("*.md"))),
        "Errors": len(list((VAULT_DIR / "Errors").glob("*")))
    }
    return counts

def get_recent_actions(limit=10):
    if not ACTION_LOG.exists(): return []
    with open(ACTION_LOG, "r", encoding="utf-8") as f:
        return f.readlines()[-limit:][::-1]

# =============================================================================
# SIDEBAR - NAVIGATION & STATUS
# =============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("AI Employee v2.0")
    st.markdown("---")
    
    menu = st.radio("🛰️ Navigation", ["Dashboard", "🥉 Bronze: Core", "🥈 Silver: Advanced", "🥇 Gold: Autonomous", "⚙️ System Logs"])
    
    st.markdown("---")
    st.subheader("📡 System Status")
    st.success("✅ Main Scheduler: ONLINE")
    st.success("✅ Vault Watcher: ACTIVE")
    st.info("🕒 Next Sync: 2:45 mins")
    
    if st.button("🔄 Sync Operations"):
        st.rerun()

# =============================================================================
# MAIN CONTENT - DASHBOARD OVERVIEW
# =============================================================================
if menu == "Dashboard":
    st.title("🚀 Operational Command Center")
    st.markdown(f"**Last Unified Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Unified Metrics
    counts = get_task_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📥 Total Inbox", counts["Inbox"])
    c2.metric("📋 Active Tasks", counts["Needs_Action"])
    c3.metric("✅ Successfully Completed", counts["Done"])
    c4.metric("⚠️ Quarantine (Errors)", counts["Errors"], delta_color="inverse")

    st.markdown("---")
    
    # Intelligence Row
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📊 Task Lifecycle Visual")
        df = pd.DataFrame({
            'Stage': ['Inbox', 'Needs Action', 'Needs Approval', 'Completed'],
            'Count': [counts['Inbox'], counts['Needs_Action'], counts['Needs_Approval'], counts['Done']]
        })
        st.bar_chart(df.set_index('Stage'))
        
    with col_right:
        st.subheader("🧠 Strategic Reasoning")
        latest_plans = list((VAULT_DIR / "Needs_Action").glob("Plan_*.md"))
        if latest_plans:
            latest_plan = sorted(latest_plans, key=os.path.getmtime)[-1]
            st.info(f"**Latest Logic Chain:** {latest_plan.name}")
            with open(latest_plan, "r", encoding="utf-8") as f:
                content = f.read()
                reasoning = re.search(r"## 🧠 Reasoning \(Chain-of-Thought\)\n\n(.*?)\n\n##", content, re.DOTALL)
                if reasoning:
                    st.markdown(reasoning.group(1))
                else:
                    st.write("Strategic deliberation in progress...")
        else:
            st.write("No active plans to display.")

# =============================================================================
# BRONZE: CORE FOUNDATION
# =============================================================================
elif menu == "🥉 Bronze: Core":
    st.markdown('<div class="tier-header"><h2>🥉 Bronze Tier: Vault & File Infrastructure</h2></div>', unsafe_allow_html=True)
    st.markdown('<span class="feature-tag">Folder Watcher</span><span class="feature-tag">Interactive CLI</span><span class="feature-tag">Inbox Processing</span>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📥 Inbox Status")
        files = list((VAULT_DIR / "Inbox").glob("*.md"))
        if files:
            for f in files: st.markdown(f"- 📄 `{f.name}`")
        else:
            st.write("Inbox is clean.")
            
    with col2:
        st.subheader("📂 Vault Structure")
        st.json({
            "AI_Employee_Vault/": ["Inbox", "Needs_Action", "Needs_Approval", "Done", "Errors", "Reports", "Reposts", "Accounting"]
        })

# =============================================================================
# SILVER: ADVANCED AUTOMATION
# =============================================================================
elif menu == "🥈 Silver: Advanced":
    st.markdown('<div class="tier-header"><h2>🥈 Silver Tier: Communication & Reasoning</h2></div>', unsafe_allow_html=True)
    st.markdown('<span class="feature-tag">Plan.md Generator</span><span class="feature-tag">LinkedIn Auto-Post</span><span class="feature-tag">Human Approval</span>', unsafe_allow_html=True)
    
    tab_a, tab_b = st.tabs(["📝 Strategic Planning", "⚖️ Approval Workflow"])
    
    with tab_a:
        st.subheader("Active Execution Plans")
        plans = list((VAULT_DIR / "Needs_Action").glob("Plan_*.md"))
        if plans:
            for p in plans:
                with st.expander(f"🔍 {p.name}"):
                    with open(p, "r", encoding="utf-8") as f:
                        st.markdown(f.read())
        else:
            st.write("No active plans found.")
            
    with tab_b:
        st.subheader("Pending Human Approvals")
        approvals = list((VAULT_DIR / "Needs_Approval").glob("*.md"))
        if approvals:
            for a in approvals:
                st.warning(f"⚠️ **Action Required:** {a.name}")
                if st.button(f"View Details: {a.name}"):
                    with open(a, "r", encoding="utf-8") as f:
                        st.code(f.read(), language="markdown")
        else:
            st.success("All approvals cleared!")

# =============================================================================
# GOLD: AUTONOMOUS EMPLOYEE
# =============================================================================
elif menu == "🥇 Gold: Autonomous":
    st.markdown('<div class="tier-header"><h2>🥇 Gold Tier: Autonomous loop & Recovery</h2></div>', unsafe_allow_html=True)
    st.markdown('<span class="feature-tag">Ralph Wiggum Loop</span><span class="feature-tag">Exponential Backoff</span><span class="feature-tag">CEO Briefing</span>', unsafe_allow_html=True)
    
    # Load Ralph State
    state = load_json(RALPH_STATE)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("🔁 Current Iteration", state.get("current_iteration", 0))
    c2.metric("🤖 Active Loops", len(state.get("active_tasks", [])))
    c3.metric("📊 Reports Generated", len(list((VAULT_DIR / "Reports").glob("*.md"))))
    
    st.markdown("---")
    
    st.subheader("🛠️ Self-Healing (Error Recovery)")
    queue = load_json(RETRY_QUEUE)
    pending_retries = queue.get("pending_retries", [])
    if pending_retries:
        st.dataframe(pd.DataFrame(pending_retries)[["filename", "attempts", "retry_time", "category"]])
    else:
        st.success("No errors in retry queue. System running optimally.")

# =============================================================================
# SYSTEM LOGS
# =============================================================================
elif menu == "⚙️ System Logs":
    st.markdown('<div class="tier-header"><h2>⚙️ System Audit Logs</h2></div>', unsafe_allow_html=True)
    
    log_type = st.selectbox("Select Log Stream", ["Action Log", "Error Log"])
    
    if log_type == "Action Log":
        actions = get_recent_actions(50)
        st.code("".join(actions), language="text")
    else:
        if ERRORS_LOG.exists():
            with open(ERRORS_LOG, "r", encoding="utf-8") as f:
                st.error(f.read())
        else:
            st.info("No system errors recorded.")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
col_f1, col_f2 = st.columns(2)
col_f1.markdown("**AI Employee v2.0 - Command Center**")
col_f2.markdown("<div align='right'>Powered by <b>Gemini CLI</b> | Architect: <b>Imam Sanghaar Chandio</b></div>", unsafe_allow_html=True)
