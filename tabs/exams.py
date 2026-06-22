import pandas as pd
import plotly.express as px
import streamlit as st

from chord_utils import plot_chord
from network_utils import build_pairs, plot_network


def render(labevents_filtered, d_labitems, top_n, min_freq):
    """Renderiza ranking, combinações e rede de coocorrência de exames."""

    # Exames mais solicitados
    lab_counts = labevents_filtered["itemid"].value_counts().reset_index()
    lab_counts.columns = ["itemid", "count"]

    top_labs = (
        lab_counts
        .merge(d_labitems[["itemid", "label"]], on="itemid")
        .head(top_n)
    )

    if top_labs.empty:
        st.info("Sem exames para os filtros selecionados.")
    else:
        fig = px.bar(
            top_labs.sort_values("count"), x="count", y="label",
            orientation="h", title=f"Top {top_n} Exames Mais Solicitados",
            labels={"label": "Exame", "count": "Número de Solicitações"},
        )
        fig.update_layout(
            title_x=0.5,
            title_xanchor="center",
            title_xref="paper",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_labs, 
                     column_config={
                         "itemid": st.column_config.TextColumn(label="ID do Exame", alignment="left"),
                         "count": st.column_config.NumberColumn(label="Número de Solicitações", alignment="left"), 
                         "label": st.column_config.TextColumn(label="Exame", alignment="left"), 
                    }, 
                     use_container_width=True
        )

    # Pares de exames mais frequentes na mesma internação
    pairs = build_pairs(labevents_filtered, "hadm_id", "itemid")

    if not pairs:
        st.info("Sem combinações de exames suficientes para os filtros selecionados.")
    else:
        df_pairs = pd.DataFrame(pairs, columns=["lab1", "lab2"])
        all_pair_counts = df_pairs.value_counts().reset_index(name="count")

        all_pair_counts = (
            all_pair_counts
            .merge(d_labitems[["itemid", "label"]], left_on="lab1", right_on="itemid", how="left")
            .rename(columns={"label": "exam1"})
            .merge(d_labitems[["itemid", "label"]], left_on="lab2", right_on="itemid", how="left")
            .rename(columns={"label": "exam2"})
        )
        all_pair_counts["exam1"] = all_pair_counts["exam1"].fillna(all_pair_counts["lab1"].astype(str))
        all_pair_counts["exam2"] = all_pair_counts["exam2"].fillna(all_pair_counts["lab2"].astype(str))
        all_pair_counts["pair"] = all_pair_counts["exam1"] + " & " + all_pair_counts["exam2"]

        top_pairs = all_pair_counts.head(top_n)

        fig = px.bar(
            top_pairs.sort_values("count"), x="count", y="pair",
            orientation="h", title=f"Top {top_n} Combinações de Exames",
            labels={"pair": "Combinação de Exames", "count": "Número de Internações"},
        )
        fig.update_layout(
            title_x=0.5,
            title_xanchor="center",
            title_xref="paper",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_pairs[["exam1", "exam2", "count"]], use_container_width=True, 
                     column_config={
                         "exam1": st.column_config.TextColumn(label="Exame 1", alignment="left"),
                         "exam2": st.column_config.TextColumn(label="Exame 2", alignment="left"), 
                         "count": st.column_config.NumberColumn(label="Número de Internações", alignment="left"), 
                    }
        )

        # Diagrama de cordas de coocorrência de exames filtrada por frequência mínima
        top_pairs_net = all_pair_counts[all_pair_counts["count"] >= min_freq]

        chord_html = plot_chord(top_pairs_net, "exam1", "exam2", "count", "Diagrama de Cordas de Coocorrência de Exames")
        if chord_html is None:
            st.info("Sem conexões suficientes para exibir o diagrama de cordas.")
        else:
            st.components.v1.html(chord_html, height=720, scrolling=False)
