import streamlit as st
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import re


# ---------------------------------------
# Safety rules for chat mode (NEW)
# ---------------------------------------
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
        "I cannot help with diagnosis or treatment decisions. "
        "I can explain what lab values generally measure and common non definitive reasons "
        "they can be high or low. Ask about a marker from your uploaded report or ask for "
        "a summary of abnormal values."
    )


# ---------------------------------------
# Strict system prompt (NEW)
# ---------------------------------------
EDU_ONLY_SYSTEM_PROMPT = """
Educational only. Not medical advice.

You are a lab report tutor. The user has uploaded a lab report. You answer follow up questions about that report.

Safety rules
- No diagnosis. No treatment. No medication or dosage advice.
- Do not tell the user what they should do medically.
- If asked for diagnosis or treatment, refuse and suggest discussing with a clinician.

Answer rules
- Answer only the user question. Do not re explain the whole report unless asked.
- If the question is about one test, focus only on that test.
- If asked about risk, explain general associations and what the marker relates to, not personal risk.
- If asked for next steps, give safe discussion points for a clinician, not instructions.

Style
- Vary structure based on the question.
- Be specific and concise. Avoid repetitive templates.
""".strip()


class ChatAgent:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        self.model_name = "llama-3.3-70b-versatile"

    def initialize_vector_store(self, text_content):
        """Create vector store from text content."""
        if not text_content or text_content.strip() == "":
            text_content = "No report context available."

        texts = self.text_splitter.split_text(text_content)
        if not texts:
            texts = [text_content]

        vectorstore = FAISS.from_texts(texts, self.embeddings)
        return vectorstore

    def _format_chat_history(self, chat_history):
        """Format chat history for Groq API."""
        messages = []
        for msg in chat_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        return messages

    def _contextualize_query(self, query, chat_history):
        """Reformulate query considering chat history."""
        if not chat_history:
            return query

        recent_history = chat_history[-4:]
        history_text = "\n".join(
            [
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in recent_history
            ]
        )

        contextualize_prompt = f"""Given a chat history and the latest user question, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is.

Chat History:
{history_text}

Latest User Question: {query}

Standalone Question:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You reformulate questions to be standalone."},
                    {"role": "user", "content": contextualize_prompt},
                ],
                temperature=0.1,
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return query

    def get_response(self, query, vectorstore, chat_history=None, full_text_context=None):
        """Get response using RAG with full text fallback."""
        if chat_history is None:
            chat_history = []

        # Safety short circuit (NEW)
        if is_unsafe_chat_query(query):
            return unsafe_chat_message()

        # 1 Contextualize query
        contextualized_query = self._contextualize_query(query, chat_history)

        # Safety again after contextualization (NEW)
        if is_unsafe_chat_query(contextualized_query):
            return unsafe_chat_message()

        # 2 Retrieve relevant documents
        try:
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.get_relevant_documents(contextualized_query)
            context = "\n\n".join([doc.page_content for doc in docs])

            if "No report context available" in context:
                context = ""
        except Exception:
            context = ""
        
        # Fallback to full text if RAG returns nothing and text is reasonable size
        if (not context or not context.strip()) and full_text_context:
            # Use full text if < 15k chars (approx 3-4k tokens)
            if len(full_text_context) < 15000:
                context = full_text_context

        # 3 Build safe prompt
        qa_system_prompt = EDU_ONLY_SYSTEM_PROMPT

        messages = [{"role": "system", "content": qa_system_prompt}]

        # Add limited chat history
        if chat_history:
            formatted_history = self._format_chat_history(chat_history[-6:])  # type: ignore
            # Strip system messages from history to avoid prompt injection
            for m in formatted_history:
                if m.get("role") == "system":
                    continue
                messages.append(m)

        # Add context and current question
        if context and context.strip():
             user_message = (
                "Use only the provided report context.\n"
                "If the context does not contain what you need, say you do not know.\n\n"
                f"Report context:\n{context}\n\n"\
                f"User question:\n{query}\n\n"
                "Return the answer in this format\n"
                "Direct answer: 2 to 6 sentences\n"
                "If a reference range is present in context, mention it\n"
                "If multiple tests are relevant, list only those tests\n"
    )
        else:
           user_message = (
                f"User question:\n{query}\n\n"
                "No report context is available. Answer only if it is general education, otherwise say you do not know."
            )

        messages.append({"role": "user", "content": user_message})

        # 4 Call Groq
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.65,
                max_tokens=650,
            )
            answer = response.choices[0].message.content or ""

            # Post safety filter (NEW)
            lower = answer.lower()
            if any(
                s in lower
                for s in [
                    "you should take",
                    "start taking",
                    "stop taking",
                    "increase the dose",
                    "decrease the dose",
                    "i recommend",
                    "take this medication",
                ]
            ):
                return unsafe_chat_message()

            # Always prepend disclaimer (NEW)
            if "educational only" not in lower:
                answer = "Educational only. Not medical advice.\n\n" + answer

            return answer

        except Exception as e:
            return f"Error generating response: {str(e)}"
