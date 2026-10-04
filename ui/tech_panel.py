"""Sidebar Tech panel for judges: live step trace and tech stack."""
import streamlit as st

from utils import safety, trace


def render():
    st.markdown("<div class='tp-chip'>TECH PANEL  |  for judges</div>", unsafe_allow_html=True)

    with st.expander("Live trace of the last message", expanded=True):
        tr = trace.current()
        if not tr or not tr["steps"]:
            st.caption("Send a message in the Patient assistant tab to see each step run here.")
        else:
            show = st.toggle("Show prompt and raw Gemini reply", value=False)
            for s in tr["steps"]:
                ms = f" - {s['ms']} ms" if s["ms"] is not None else ""
                st.markdown(f"<div class='tp-step {s['status']}'><b>{s['stage']}</b> {s['agent']}<small>{ms}</small><br>"
                            f"<small>Used:</small> {s['used']}<br><small>Result:</small> {s['result']}</div>",
                            unsafe_allow_html=True)
                if show and s["detail"]:
                    for title, body in s["detail"].items():
                        st.caption(title)
                        st.code(body, wrap_lines=True)

    with st.expander("Tech stack"):
        st.markdown(f"""
- **Language and UI:** Python, Streamlit
- **AI:** Google Gemini (`google-genai`)
- **Data:** pandas, fictional demo data
- **Safety:** rule-based emergency screen ({len(safety.EMERGENCY_TERMS)} terms) runs before any AI call
- **Privacy:** names and phone numbers are never sent to Gemini
""")