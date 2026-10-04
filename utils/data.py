import streamlit as st

from datasets.sample_data import HOSPITAL_DATA


@st.cache_data
def load() -> dict:
    return HOSPITAL_DATA
