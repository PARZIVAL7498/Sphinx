import sys
import os
import streamlit as st

# Custom Modules
from src.ui import hide_default_sidebar_nav
from src.sidebar import render_sidebar
from src.Main_Menu import main

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Project Sphinx | Stable v1.5", 
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Project Sphinx v1.5 - Stable Release"
    }
)

# --- SIDEBAR & NAVIGATION ---
hide_default_sidebar_nav()
render_sidebar()

# --- PATH SETUP & MAIN EXECUTION ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    main()