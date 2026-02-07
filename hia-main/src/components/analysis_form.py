import streamlit as st
from utils.pdf_extractor import extract_text_from_pdf_safe
from services.lab_service import process_lab_report
from safety.guardrails import DISCLAIMER
from config.app_config import MAX_UPLOAD_SIZE_MB


def show_analysis_form():
    st.title("Medical Lab Report Explainer")
    st.caption(DISCLAIMER)

    st.info(
        "This tool provides educational explanations of lab report values only. "
        "It does not diagnose conditions or recommend treatment."
    )

    user_id = st.text_input("User ID", value="demo_user")

    uploaded_file = st.file_uploader(
        f"Upload lab report PDF (Max {MAX_UPLOAD_SIZE_MB}MB)",
        type=["pdf"],
        help="Upload a medical lab report PDF containing test values and reference ranges",
    )

    user_question = st.text_input(
        "Optional educational question about the report",
        placeholder="Example: What does this test generally measure?",
    )

    if uploaded_file and st.button("Process Report"):
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > MAX_UPLOAD_SIZE_MB:
            st.error(
                f"File size ({file_size_mb:.1f}MB) exceeds the {MAX_UPLOAD_SIZE_MB}MB limit."
            )
            return

        with st.spinner("Extracting and analyzing report..."):
            pdf_out = extract_text_from_pdf_safe(uploaded_file)

            if "error" in pdf_out:
                st.error(pdf_out["error"])
                return

            # -------------------------------
            # NEW: store report text for Chat mode
            # -------------------------------
            st.session_state.current_report_text = pdf_out.get("safe_text", "") or ""

            # NEW: reset chat when new report is processed
            st.session_state.chat_messages = []

            result = process_lab_report(
                user_id=user_id,
                filename=uploaded_file.name,
                report_text=pdf_out["safe_text"],
                user_question=user_question,
            )

        if not result["success"]:
            st.error(result["error"])
            return

        extraction = result["extraction"]
        explanation = result["explanation"]
        trends = result.get("trends", [])

        # ---------- User Question Answer ----------
        user_answer = explanation.get("user_question_answer")
        if user_answer:
            st.divider()
            st.markdown(f"### 💡 Answer to your question: *{user_question}*")
            st.success(user_answer)
            st.divider()

        # ---------- Structured Results ----------
        st.subheader("Extracted Lab Results")

        table_rows = []
        for r in extraction.get("results", []):
            table_rows.append(
                {
                    "Test": r.get("test_name"),
                    "Value": r.get("value_raw"),
                    "Unit": r.get("unit"),
                    "Reference Range": r.get("ref_text"),
                    "Out of Range": r.get("is_out_of_range"),
                }
            )

        st.dataframe(table_rows)

        # ---------- Trends ----------
        if trends:
            st.subheader("Trends Compared to Previous Report")
            st.dataframe(trends)

        # ---------- Explanations ----------
        st.subheader("Educational Explanations")

        for item in explanation.get("items", []):
            st.markdown(f"### {item.get('test_name', '')}")
            st.write(item.get("summary", ""))
            st.write(item.get("what_it_measures", ""))

            questions = item.get("how_to_discuss_with_doctor", [])
            if questions:
                st.write("Questions you could ask your doctor")
                for q in questions:
                    st.write(f"- {q}")

            st.caption(item.get("grounded_in_report", ""))

        # ---------- General Questions ----------
        general_qs = explanation.get("general_questions_for_doctor", [])
        if general_qs:
            st.subheader("General Questions for Doctor Discussion")
            for q in general_qs:
                st.write(f"- {q}")

        # ---------- Final Disclaimer ----------
        st.warning(DISCLAIMER)
