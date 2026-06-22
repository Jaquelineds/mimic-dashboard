import streamlit as st

from data_loader import load_data
import sidebar

from tabs import demography as demography_tab
from tabs import exams as exams_tab
from tabs import admissions as admissions_tab
from tabs import prescriptions as prescriptions_tab

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard MIMIC-IV", layout="wide")


# ── Carregamento de dados ─────────────────────────────────────────────────────
patients, admissions, labevents, prescriptions, d_labitems = load_data()


# ── Cabeçalho principal ───────────────────────────────────────────────────────
st.title("🏥 Dashboard Interativo MIMIC-IV")
st.markdown("Visualização desenvolvida para a disciplina de **Visualização de Dados**.")
st.caption(
    "Integrantes: Francisco João Lucca Neto · Jaqueline Dahmer Steffenon · "
    "João Vitor Gularte · Letícia Brasil Flores"
)

st.caption("""
**Dados utilizados**

Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023).
*MIMIC-IV Clinical Database Demo* (Version 2.2). PhysioNet.
DOI: https://doi.org/10.13026/dp1f-ex47

Este dashboard utiliza exclusivamente o conjunto de dados **MIMIC-IV Demo**,
composto por dados clínicos desidentificados de uma amostra de 100 pacientes,
disponibilizados para fins educacionais e de pesquisa.
""")
st.markdown("---")


# ── Filtros na barra lateral ──────────────────────────────────────────────────
gender_filter, age_range, adm_filter, top_n, min_freq = sidebar.render_sidebar(patients, admissions)


# ── Filtragem dos dados conforme os filtros selecionados ──────────────────────
patients = patients[
    patients["gender"].isin(gender_filter)
    & patients["anchor_age"].between(age_range[0], age_range[1])
]

filtered_subjects = patients["subject_id"]

admissions_filtered = admissions[
    admissions["subject_id"].isin(filtered_subjects)
    & admissions["admission_type"].isin(adm_filter)
]

labevents_filtered = labevents[labevents["subject_id"].isin(filtered_subjects)]

prescriptions_filtered = prescriptions[prescriptions["subject_id"].isin(filtered_subjects)]

if patients.empty:
    st.warning("Nenhum paciente encontrado para os filtros selecionados.")
    st.stop()


# ── Métricas resumidas no topo ────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Pacientes",
    len(patients)
)

col2.metric(
    "Internações",
    len(admissions_filtered)
)

col3.metric(
    "Tipos de exames",
    labevents_filtered["itemid"].nunique()
)

col4.metric(
    "Medicamentos",
    prescriptions_filtered["drug"].nunique()
)

# Resumo complementar
total_exames = f"{len(labevents_filtered):,}".replace(",", ".")
total_prescricoes = f"{len(prescriptions_filtered):,}".replace(",", ".")

st.caption(
    f"**Registros analisados:** "
    f"{total_exames} exames laboratoriais e "
    f"{total_prescricoes} prescrições."
)


# ── Abas principais ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 Demografia",
    "🏥 Internações",
    "🧪 Exames",
    "💊 Medicamentos",
])

with tab1:
    demography_tab.render(patients)

with tab2:
    admissions_tab.render(admissions_filtered)

with tab3:
    exams_tab.render(labevents_filtered, d_labitems, top_n, min_freq)

with tab4:
    prescriptions_tab.render(prescriptions_filtered, top_n, min_freq)
