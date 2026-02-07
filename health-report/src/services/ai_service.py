import streamlit as st
from agents.analysis_agent import AnalysisAgent
import json
import groq

# -------------------------------
# Chat safety guard (NEW)
# -------------------------------
import re

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
        "I *can* explain what lab values generally measure and common non-definitive "
        "reasons they may be high or low. Ask about a marker from your report or request "
        "a summary of abnormal values."
    )


# -------------------------------
# Session initialization
# -------------------------------
def init_analysis_state():
    if "analysis_agent" not in st.session_state:
        st.session_state.analysis_agent = AnalysisAgent()

    if "chat_agent" not in st.session_state:
        try:
            from agents.chat_agent import ChatAgent

            if "GROQ_API_KEY" not in st.secrets:
                st.session_state.chat_agent = None
                st.session_state.chat_agent_error = (
                    "GROQ_API_KEY not found in secrets."
                )
            else:
                st.session_state.chat_agent = ChatAgent()
                st.session_state.chat_agent_error = None

        except Exception as e:
            st.session_state.chat_agent = None
            st.session_state.chat_agent_error = str(e)


# -------------------------------
# Rate limit check
# -------------------------------
def check_rate_limit():
    init_analysis_state()
    return st.session_state.analysis_agent.check_rate_limit()


# -------------------------------
# Lab report explainer (UNCHANGED)
# -------------------------------
def generate_analysis(data, system_prompt, check_only=False, session_id=None):
    init_analysis_state()

    if check_only:
        return st.session_state.analysis_agent.check_rate_limit()

    return st.session_state.analysis_agent.analyze_report(
        data=data,
        system_prompt=system_prompt,
        check_only=False,
    )


# -------------------------------
# Chat response (SAFETY ADDED)
# -------------------------------
def get_chat_response(query, context_text, chat_history):
    init_analysis_state()

    if is_unsafe_chat_query(query):
        return unsafe_chat_message()

    if st.session_state.chat_agent is None:
        return st.session_state.get(
            "chat_agent_error",
            "Chat unavailable. Check GROQ_API_KEY.",
        )

    if not context_text:
        context_text = "No report context available."

    if "vector_store" not in st.session_state or st.session_state.get(
        "vector_store_key"
    ) != len(context_text):
        try:
            st.session_state.vector_store = (
                st.session_state.chat_agent.initialize_vector_store(context_text)
            )
            st.session_state.vector_store_key = len(context_text)
        except Exception:
            return "Unable to process report context."

    return st.session_state.chat_agent.get_response(
        query,
        st.session_state.vector_store,
        chat_history,
        full_text_context=context_text,
    )


# -------------------------------
# Groq JSON call (UNCHANGED)
# -------------------------------
def call_groq_json(system: str, user: str, temperature: float = 0.2):
    if "GROQ_API_KEY" not in st.secrets:
        raise ValueError("GROQ_API_KEY not found")

    client = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )

    content = (resp.choices[0].message.content or "").strip()
    if content.startswith("```"):
        content = content.split("```", 2)[1].strip()
        if content.lower().startswith("json"):
            content = content[4:].strip()  # type: ignore

    return json.loads(content)
