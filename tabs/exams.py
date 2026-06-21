import pandas as pd
import plotly.express as px
import streamlit as st

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
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_labs, use_container_width=True)

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
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_pairs[["exam1", "exam2", "count"]], use_container_width=True)

        # Rede de coocorrência de exames filtrada por frequência mínima
        top_pairs_net = all_pair_counts[all_pair_counts["count"] >= min_freq]
        network_fig = plot_network(top_pairs_net, "exam1", "exam2", "count", "Rede de Coocorrência de Exames")
        st.plotly_chart(network_fig, use_container_width=True)
