import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import re

# Set page config
st.set_page_config(
    page_title="AI Employee Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Configuration
BASE_DIR = Path(__file__).parent.parent.resolve()
VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
LOGS_DIR = BASE_DIR / "Logs"
DASHBOARD_MD = BASE_DIR / "Dashboard.md"
ACTION_LOG = LOGS_DIR / "action.log"
ERRORS_LOG = LOGS_DIR / "errors.log"

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
    if not ACTION_LOG.exists():
        return []
    with open(ACTION_LOG, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines[-limit:][::-1]

def get_error_summary():
    if not ERRORS_LOG.exists():
        return "No errors logged."
    with open(ERRORS_LOG, "r", encoding="utf-8") as f:
        content = f.read()
    error_count = content.count("[ERROR]")
    return error_count

# Sidebar
st.sidebar.title("🤖 AI Employee v2.0")
st.sidebar.markdown("---")
st.sidebar.info("Autonomous Business Agent with Multi-Tier intelligence.")

if st.sidebar.button("Refresh Data"):
    st.rerun()

# Main Header
st.title("🚀 Operational Command Center")
st.markdown(f"**Last Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Metrics Row
counts = get_task_counts()
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📥 Inbox", counts["Inbox"])
col2.metric("📋 Needs Action", counts["Needs_Action"])
col3.metric("⚖️ Pending Approval", counts["Needs_Approval"], delta_color="inverse")
col4.metric("✅ Completed", counts["Done"])
col5.metric("⚠️ Errors", counts["Errors"], delta=-counts["Errors"], delta_color="inverse")

# Main Content
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📜 Activity Logs", "🛠️ System Health"])

with tab1:
    st.header("System Overview")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Task Distribution")
        df = pd.DataFrame({
            'Status': list(counts.keys()),
            'Count': list(counts.values())
        })
        st.bar_chart(df.set_index('Status'))
        
    with col_right:
        st.subheader("Current Priorities")
        # Read Needs_Action files to find priorities
        priorities = {"High": 0, "Medium": 0, "Low": 0}
        for f in (VAULT_DIR / "Needs_Action").glob("*.md"):
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()
                if "priority: high" in content.lower(): priorities["High"] += 1
                elif "priority: low" in content.lower(): priorities["Low"] += 1
                else: priorities["Medium"] += 1
        
        st.write(f"🔴 High Priority: {priorities['High']}")
        st.write(f"🟡 Medium Priority: {priorities['Medium']}")
        st.write(f"🟢 Low Priority: {priorities['Low']}")

with tab2:
    st.header("Recent Actions")
    actions = get_recent_actions(20)
    for action in actions:
        if "ERROR" in action:
            st.error(action)
        elif "COMPLETE" in action or "SUCCESS" in action:
            st.success(action)
        else:
            st.info(action)

with tab3:
    st.header("System Diagnostics")
    error_count = get_error_summary()
    st.warning(f"Total System Errors Detected: {error_count}")
    
    if st.button("View Error Log Details"):
        if ERRORS_LOG.exists():
            with open(ERRORS_LOG, "r", encoding="utf-8") as f:
                st.code(f.read()[-2000:], language="text")
        else:
            st.write("No error log file found.")

# Footer
st.markdown("---")
st.markdown("<div align='center'>Built by Imam Sanghaar Chandio & Gemini CLI</div>", unsafe_allow_html=True)
