"""
filename : Seshat.py
This script is the starting point for the execution of this project.

command to run : streamlit run Seshat.py

This file holds the structure of entire project and
calls the necessary function as per requested page.
"""

import streamlit as st

from utils import get_client, header
from app import generate_text_results, display_stored_results

header()

client = get_client()

page = st.sidebar.selectbox("Select a page",
                            ["APP", "My Results"])

if page == "APP":
    generate_text_results(client)

else:
    display_stored_results()
