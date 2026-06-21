import pandas as pd
import plotly.express as px
import streamlit as st

from network_utils import build_pairs, plot_network


def render(prescriptions_filtered, top_n, min_freq):
    """Renderiza ranking, combinações e rede de co-prescrição de medicamentos."""

    # Medicamentos mais prescritos
    med_counts = prescriptions_filtered["drug"].value_counts().reset_index()
    med_counts.columns = ["drug", "count"]

    if med_counts.empty:
        st.info("Sem medicamentos para os filtros selecionados.")
    else:
        fig = px.bar(
            med_counts.head(top_n).sort_values("count"), x="count", y="drug",
            orientation="h", title=f"Top {top_n} Medicamentos Prescritos",
            labels={"drug": "Medicamento", "count": "Número de Prescrições"},
        )
        fig.update_layout(
            title_x=0.5,
            title_xanchor="center",
            title_xref="paper",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Normalização dos nomes de medicamentos antes de gerar pares
    prescriptions_pairs = prescriptions_filtered.copy()
    prescriptions_pairs["drug_cleaned"] = (
        prescriptions_pairs["drug"].fillna("").str.strip().str.lower()
    )
    prescriptions_pairs = prescriptions_pairs[prescriptions_pairs["drug_cleaned"] != ""]

    pairs = build_pairs(prescriptions_pairs, "hadm_id", "drug_cleaned")

    if not pairs:
        st.info("Não há dados suficientes para gerar combinações de medicamentos.")
    else:
        df_pairs = pd.DataFrame(pairs, columns=["drug1", "drug2"])
        all_pair_counts = df_pairs.value_counts().reset_index(name="count")
        top_pairs = all_pair_counts.head(top_n)
        top_pairs["pair"] = top_pairs["drug1"] + " & " + top_pairs["drug2"]

        fig = px.bar(
            top_pairs.sort_values("count"), x="count", y="pair",
            orientation="h", title=f"Top {top_n} Combinações de Medicamentos",
            labels={"pair": "Combinação de Medicamentos", "count": "Número de Internações"},
        )
        fig.update_layout(
            title_x=0.5,
            title_xanchor="center",
            title_xref="paper",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_pairs, use_container_width=True, 
                     column_config={
                         "drug1": st.column_config.TextColumn(label="Medicamento 1", alignment="left"),
                         "drug2": st.column_config.TextColumn(label="Medicamento 2", alignment="left"), 
                         "count": st.column_config.NumberColumn(label="Número de Internações", alignment="left"),
                         "pair": st.column_config.TextColumn(label="Combinação", alignment="left"),
                    }
        )

        # Rede de co-prescrição filtrada por frequência mínima
        top_pairs_net = all_pair_counts[all_pair_counts["count"] >= min_freq]
        network_fig = plot_network(top_pairs_net, "drug1", "drug2", "count", "Rede de Co-prescrição de Medicamentos")
        st.plotly_chart(network_fig, use_container_width=True)
