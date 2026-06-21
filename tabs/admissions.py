import pandas as pd
import plotly.express as px
import streamlit as st


def render(admissions_filtered):
    """Renderiza distribuição dos tipos de admissão e tempo médio de permanência."""

    admission_counts = admissions_filtered["admission_type"].value_counts().reset_index()
    admission_counts.columns = ["admission_type", "count"]

    if admission_counts.empty:
        st.info("Sem internações para os filtros selecionados.")
    else:
        fig = px.bar(
            admission_counts, x="admission_type", y="count",
            color="count", title="Distribuição dos Tipos de Admissão",
            labels={"admission_type": "Tipo de Admissão", "count": "Número de Internações"},
        )
        
        fig.update_layout(
            title_x=0.5,
            title_xanchor="center",
            title_xref="paper",
        )

        st.plotly_chart(fig, use_container_width=True)

    # Cálculo do tempo de permanência em horas
    admissions_filtered = admissions_filtered.copy()
    admissions_filtered["admittime"] = pd.to_datetime(admissions_filtered["admittime"], errors="coerce")
    admissions_filtered["dischtime"] = pd.to_datetime(admissions_filtered["dischtime"], errors="coerce")
    admissions_filtered["los_hours"] = (
        admissions_filtered["dischtime"] - admissions_filtered["admittime"]
    ).dt.total_seconds() / 3600
    admissions_filtered = admissions_filtered[admissions_filtered["los_hours"] >= 0]

    los = admissions_filtered.groupby("admission_type")["los_hours"].mean().reset_index()

    if los.empty:
        st.info("Sem dados válidos para calcular tempo de permanência.")
    else:
        fig = px.bar(
            los.sort_values("los_hours"),
            x="los_hours", y="admission_type",
            orientation="h", title="Tempo Médio de Permanência (horas)",
            labels={"admission_type": "Tipo de Admissão", "los_hours": "Tempo Médio (horas)"},
        )

        fig.update_layout(
            title_x=0.5,
            title_xanchor="center",
            title_xref="paper",
        )

        st.plotly_chart(fig, use_container_width=True)
