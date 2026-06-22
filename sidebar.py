import streamlit as st


def render_sidebar(patients, admissions):
    """Renderiza os controles da sidebar e retorna os valores selecionados."""
    st.sidebar.header("Filtros")

    gender_filter = st.sidebar.multiselect(
        "Gênero",
        options=patients["gender"].unique(),
        default=patients["gender"].unique(),
    )

    age_range = st.sidebar.slider(
        "Faixa etária",
        int(patients["anchor_age"].min()),
        int(patients["anchor_age"].max()),
        (int(patients["anchor_age"].min()), int(patients["anchor_age"].max())),
    )

    adm_filter = st.sidebar.multiselect(
        "Tipo de admissão",
        options=admissions["admission_type"].unique(),
        default=admissions["admission_type"].unique(),
    )

    top_n = st.sidebar.slider("Top N resultados", 5, 20, 10)

    min_freq = st.sidebar.slider("Frequência mínima das conexões", 20, 100, 40)

    st.sidebar.markdown("---")

    return gender_filter, age_range, adm_filter, top_n, min_freq
