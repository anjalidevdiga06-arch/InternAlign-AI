
import streamlit as st
from modules.ml_model import predict_suitability

st.set_page_config(
    page_title="InternAlign AI Model",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 InternAlign AI")
st.subheader("Machine Learning Internship Suitability Predictor")

st.write(
    "Enter your details below to check your suitability "
    "for an internship."
)

st.divider()

skill_match = st.slider(
    "Skill Match (%)",
    min_value=0,
    max_value=100,
    value=75
)

domain_match = st.slider(
    "Domain Match (%)",
    min_value=0,
    max_value=100,
    value=80
)

degree_match = st.selectbox(
    "Degree Match",
    [1, 0],
    format_func=lambda x: "Yes" if x == 1 else "No"
)

year_match = st.selectbox(
    "Year Eligibility",
    [1, 0],
    format_func=lambda x: "Eligible" if x == 1 else "Not Eligible"
)

experience_match = st.selectbox(
    "Experience Match",
    [1, 0],
    format_func=lambda x: "Yes" if x == 1 else "No"
)

if st.button("Predict Internship Suitability"):
    try:
        result = predict_suitability(
            skill_match=skill_match,
            domain_match=domain_match,
            degree_match=degree_match,
            year_match=year_match,
            experience_match=experience_match
        )

        st.divider()
        st.subheader("Prediction Result")

        if result["prediction"] == 1:
            st.success("Suitable Internship")
        else:
            st.warning("Not Suitable Internship")

        st.metric(
            "Suitability Probability",
            f'{result["probability"]}%'
        )

        st.caption(
            "Model: Logistic Regression"
        )

        st.caption(
            f'Model test accuracy: {result["accuracy"]}%'
        )

    except Exception as e:
        st.error(f"Prediction error: {e}")
