import streamlit as st
from auth.session_manager import SessionManager
from components.footer import show_footer

def show_sidebar():
    with st.sidebar:
        # Logout button
        st.markdown("---")
        if st.button("Logout"):
            SessionManager.logout()
            st.rerun()
        
        # Add footer to sidebar
        show_footer(in_sidebar=True)
