"""Step-by-step trace of the last patient request, shown in the Tech panel."""
import time

import streamlit as st


def begin(message: str, lang: str):
    st.session_state["trace"] = {"message": message, "lang": lang, "steps": []}


def add(stage, agent, used, result, ms=None, status="ok", detail=None):
    tr = st.session_state.setdefault("trace", {"message": "", "lang": "", "steps": []})
    tr["steps"].append({"stage": stage, "agent": agent, "used": used, "result": result,
                        "ms": ms, "status": status, "detail": detail})


def current():
    return st.session_state.get("trace")


def since(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)
