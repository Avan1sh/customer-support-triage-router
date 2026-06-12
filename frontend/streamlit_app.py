"""Streamlit frontend for the Customer Support Triage & Resolution Router.

This is a pure CLIENT of the FastAPI service: it only makes HTTP calls, exactly
like any other consumer would. Run the API first, then:

    # 1) start the API (either one):
    #    docker compose up           -> API on http://localhost:8001
    #    python -m uvicorn app.api.main:app   -> API on http://localhost:8000
    # 2) start this UI:
    streamlit run frontend/streamlit_app.py
"""
import os

import requests
import pandas as pd
import streamlit as st

# set_page_config MUST be the first Streamlit command.
st.set_page_config(page_title="Support Triage Router", page_icon="🎫", layout="wide")

PRIORITY_ICON = {"Critical": "🔴", "High": "🟠", "Medium": "🔵", "Low": "🟢"}

# Default API URL can be overridden by env (e.g. point at the Docker port 8001).
_DEFAULT_API = os.getenv("API_BASE_URL", "http://localhost:8000")


# --- Sidebar: which API to talk to + a live health indicator ----------------
st.sidebar.title("⚙️ Connection")
api_base = st.sidebar.text_input("API base URL", value=_DEFAULT_API)
st.sidebar.caption("Use http://localhost:8001 if running via Docker.")


def api_get(path: str) -> requests.Response:
    return requests.get(f"{api_base}{path}", timeout=60)


def api_post(path: str, payload: dict) -> requests.Response:
    return requests.post(f"{api_base}{path}", json=payload, timeout=60)


# Health check runs on every rerun (cheap) so the badge is always current.
try:
    if api_get("/health").ok:
        st.sidebar.success("API: connected ✅")
    else:
        st.sidebar.error("API: reachable but unhealthy")
except Exception:
    st.sidebar.error("API: unreachable ❌")
    st.sidebar.caption("Start it with `docker compose up` or uvicorn.")


# --- Header -----------------------------------------------------------------
st.title("🎫 Customer Support Triage & Resolution Router")
st.caption(
    "Classify · prioritize · summarize · route · escalate · draft — "
    "an LLM workflow built with LangChain + LangGraph on Groq."
)

tab_triage, tab_history, tab_analytics = st.tabs(["🧭 Triage", "📜 History", "📊 Analytics"])


# === TAB 1: Triage a ticket =================================================
with tab_triage:
    st.subheader("Submit a ticket")

    # Streamlit reruns the whole script on every interaction, so we keep the
    # textbox content in session_state - that's how a button click can fill it.
    if "ticket_text" not in st.session_state:
        st.session_state.ticket_text = ""

    examples = {
        "💳 Billing": "I was charged twice for my subscription this month and I want a refund.",
        "😡 Angry / churn": "Third time reporting this! Cancel my account today, I'm switching providers and telling everyone on Twitter.",
        "🔧 Technical": "The mobile app crashes every time I try to upload a photo.",
        "👤 Account": "How do I add another team member to my workspace?",
    }
    st.caption("Try an example:")
    cols = st.columns(len(examples))
    for (label, txt), col in zip(examples.items(), cols):
        if col.button(label, use_container_width=True):
            st.session_state.ticket_text = txt  # filled in on the next rerun

    text = st.text_area("Ticket text", key="ticket_text", height=120,
                        placeholder="Paste a customer support ticket here…")

    if st.button("Triage ticket", type="primary"):
        if len(text.strip()) < 3:
            st.warning("Please enter a ticket (at least 3 characters).")
        else:
            with st.spinner("Triaging… (RAG → classify → escalate → draft)"):
                try:
                    r = api_post("/tickets", {"text": text})
                except Exception as e:
                    st.error(f"Could not reach the API: {e}")
                    st.stop()

            if r.status_code == 200:
                d = r.json()

                if d["escalated"]:
                    signals = ", ".join(d["escalation_signals"]) or "senior attention needed"
                    st.error(f"🚨 ESCALATED — {signals} (severity: {d['escalation_severity']})")
                else:
                    st.success("Triaged and routed to the normal queue.")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Category", d["category"])
                c2.metric("Priority", f"{PRIORITY_ICON.get(d['priority'], '')} {d['priority']}")
                c3.metric("Assigned team", d["assigned_team"])
                c4.metric("SLA", f"{d['sla_hours']} h")

                st.markdown(f"**Summary:** {d['summary']}")
                with st.expander("Why this triage? (model reasoning)"):
                    st.write(d["reasoning"])

                if d["draft_reply"]:
                    st.markdown("#### ✍️ Suggested reply  *(draft — for a human to review & send)*")
                    st.text_input("Subject", value=d["draft_reply"]["subject"])
                    st.text_area("Body", value=d["draft_reply"]["body"], height=200)
                    st.caption(f"Tone: {d['draft_reply']['tone']}")
                else:
                    st.info("No draft generated — escalated tickets are answered personally by a human agent.")
            else:
                st.error(f"API returned {r.status_code}: {r.text}")


# === TAB 2: History =========================================================
with tab_history:
    st.subheader("Ticket history")
    st.button("🔄 Refresh")  # any click reruns the script, re-fetching below
    try:
        r = api_get("/tickets?limit=100")
        if r.ok:
            rows = r.json()
            if rows:
                df = pd.DataFrame(rows)[
                    ["id", "priority", "category", "assigned_team", "sla_hours", "status", "summary"]
                ]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No tickets yet — triage one in the first tab.")
        else:
            st.error(f"API returned {r.status_code}")
    except Exception as e:
        st.error(f"Could not reach the API: {e}")


# === TAB 3: Analytics =======================================================
with tab_analytics:
    st.subheader("Analytics")
    try:
        r = api_get("/analytics")
        if r.ok:
            a = r.json()
            st.metric("Total tickets", a["total"])
            left, right = st.columns(2)
            with left:
                st.caption("By priority")
                st.bar_chart(pd.DataFrame({"count": a["by_priority"]}))
                st.caption("By status")
                st.bar_chart(pd.DataFrame({"count": a["by_status"]}))
            with right:
                st.caption("By category")
                st.bar_chart(pd.DataFrame({"count": a["by_category"]}))
                st.caption("By team")
                st.bar_chart(pd.DataFrame({"count": a["by_team"]}))
        else:
            st.error(f"API returned {r.status_code}")
    except Exception as e:
        st.error(f"Could not reach the API: {e}")
