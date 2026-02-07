import os
import sys
import re

CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import streamlit as st

st.set_page_config(
    page_title="Medical Lab Report Explainer",
    page_icon="🧪",
    layout="wide",
)

from auth.session_manager import SessionManager
from components.auth_pages import show_login_page
from components.sidebar import show_sidebar
from components.analysis_form import show_analysis_form
from components.footer import show_footer
from services.ai_service import get_chat_response


# -------------------------------
# Chat safety guard
# -------------------------------
BLOCK_RE = re.compile(
    r"\b(diagnos|do i have|what disease|treat|treatment|cure|medicat|dose|dosage|"
    r"should i take|should i stop|prescribe|antibiotic|steroid|insulin|metformin|"
    r"emergency|urgent|cancer|heart attack|stroke)\b",
    re.IGNORECASE,
)

def is_unsafe_chat_query(text: str) -> bool:
    return bool(BLOCK_RE.search(text or ""))

def unsafe_chat_message() -> str:
    return (
        "Educational only. Not medical advice.\n\n"
        "I can’t help with diagnosis or treatment decisions. "
        "I can explain what lab values generally measure and common non-definitive reasons "
        "they can be high or low. Ask about a marker from your uploaded report or ask for "
        "a summary of abnormal values."
    )


# Initialize session state
SessionManager.init_session()

# Hide Streamlit form helper text
st.markdown(
    """
    <style>
        div[data-testid="InputInstructions"] > span:nth-child(1) {
            visibility: hidden;
        }
    </style>
""",
    unsafe_allow_html=True,
)


def show_user_greeting():
    if st.session_state.get("user"):
        display_name = st.session_state.user.get("name") or st.session_state.user.get(
            "email", "demo_user"
        )
        st.markdown(
            f"""
            <div style='text-align: right; padding: 1rem; color: #64B5F6; font-size: 1.05em;'>
                👋 Hi, {display_name}
            </div>
        """,
            unsafe_allow_html=True,
        )


def _init_local_chat():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []


def render_chat_page():
    st.title("Chat about this report")
    st.caption("Educational only. Not medical advice.")

    _init_local_chat()

    context_text = st.session_state.get("current_report_text", "")

    if not context_text:
        st.info("First process a report in Lab Report Explainer mode. Then return here to ask follow-up questions.")
        return

    # Show chat history
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.info(msg["content"])
        else:
            st.success(msg["content"])

    prompt = st.chat_input("Ask a follow-up question about the report...")
    if prompt:
        # Safety check
        if is_unsafe_chat_query(prompt):
            refusal = unsafe_chat_message()
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.session_state.chat_messages.append({"role": "assistant", "content": refusal})
            st.rerun()
            return

        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            response = get_chat_response(prompt, context_text, st.session_state.chat_messages)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()


def main():
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        show_login_page()
        show_footer()
        return

    show_user_greeting()
    show_sidebar()

    mode = st.sidebar.radio("Mode", ["Lab Report Explainer", "Chat"], index=0)

    if mode == "Lab Report Explainer":
        show_analysis_form()
        show_footer()
        return

    # Chat mode is now a dedicated page
    render_chat_page()
    show_footer()


if __name__ == "__main__":
    main()
