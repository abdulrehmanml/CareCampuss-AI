"""Coordinates the agents for one patient message: safety -> triage -> scheduling."""
import time

import streamlit as st

from agents import scheduler, triage
from utils import audit, trace


def handle(history: list[dict], lang: str) -> dict:
    text = history[-1]["content"]
    trace.begin(text, lang)
    trace.add("1. Input", "Chat interface", f"Patient message and selected language ({lang})",
              f"{len(text)} characters received", 0)
    result = triage.run(history, lang)
    audit.log("Triage", f"urgency={result['urgency']}", f"{result['department']} via {result['source']}",
              "alert" if result["urgency"] == "emergency" else "info")
    result["slots"] = []
    t0 = time.perf_counter()
    if result["urgency"] in ("urgent", "routine") and result["department"] != "Emergency":
        result["slots"] = scheduler.open_slots(result["department"])
        audit.log("Scheduler", "slots offered", f"{len(result['slots'])} for {result['department']}")
        trace.add("4. Scheduler", "Scheduling agent",
                  f"Department '{result['department']}', doctor roster, {len(st.session_state.get('appts', []))} existing bookings",
                  f"{len(result['slots'])} open slots offered to the patient", trace.since(t0))
    else:
        trace.add("4. Scheduler", "Scheduling agent", "Triage urgency", "Skipped: patient directed to emergency care", 0, "skipped")
    return result
