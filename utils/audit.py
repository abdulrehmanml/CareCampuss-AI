"""Audit trail of every agent action (the white paper's 'observability' control)."""
import datetime as dt

import pandas as pd
import streamlit as st


def log(agent: str, action: str, detail: str = "", level: str = "info"):
    st.session_state.setdefault("audit", []).append(
        {"time": dt.datetime.now().strftime("%H:%M:%S"), "agent": agent,
         "action": action, "detail": detail[:300], "level": level}
    )


def frame() -> pd.DataFrame:
    cols = ["time", "agent", "action", "detail", "level"]
    return pd.DataFrame(st.session_state.get("audit", []), columns=cols)
