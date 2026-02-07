import streamlit as st
from utils.pdf_extractor import extract_text_from_pdf_safe
from services.lab_service import process_lab_report
from safety.guardrails import DISCLAIMER

def show_lab_report_form():
    st.title("Medical Lab Report Explainer")
    st.caption(DISCLAIMER)

    st.info("Upload a lab report PDF to extract values and get educational explanations.")

    user_id = st.text_input("User id", value="demo_user")
    uploaded_file = st.file_uploader("Upload lab report PDF", type=["pdf"])

    question = st.text_input("Optional educational question about the report")

    if uploaded_file and st.button("Process report"):
        pdf_out = extract_text_from_pdf_safe(uploaded_file)
        if "error" in pdf_out:
            st.error(pdf_out["error"])
            return

        result = process_lab_report(
            user_id=user_id,
            filename=uploaded_file.name,
            report_text=pdf_out["safe_text"],
            user_question=question,
        )

        if not result["success"]:
            st.error(result["error"])
            return

        extraction = result["extraction"]
        explanation = result["explanation"]
        trends = result.get("trends", [])

        st.subheader("Structured results")
        st.dataframe(extraction["results"], width=True)

        if trends:
            st.subheader("Trends compared to previous report")
            st.dataframe(trends, width=True)

        st.subheader("Educational explanations")
        for item in explanation.get("items", []):
            st.markdown(f"### {item.get('test_name','')}")
            st.write(item.get("summary",""))
            st.write(item.get("what_it_measures",""))

            qs = item.get("how_to_discuss_with_doctor", [])
            if qs:
                st.write("Questions for doctor")
                for q in qs:
                    st.write(q)

            st.caption(item.get("grounded_in_report",""))

        st.subheader("General questions for doctor")
        for q in explanation.get("general_questions_for_doctor", []):
            st.write(q)
