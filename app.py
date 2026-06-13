# ── Imports ───────────────────────────────────────────────────────────────────
import os
from itertools import combinations

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard MIMIC-IV", layout="wide")

BASE_PATH = "dataset"


# ── Carregamento de dados ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    patients = pd.read_csv(os.path.join(BASE_PATH, "hosp/patients.csv.gz"))
    admissions = pd.read_csv(os.path.join(BASE_PATH, "hosp/admissions.csv.gz"))
    labevents = pd.read_csv(os.path.join(BASE_PATH, "hosp/labevents.csv.gz"))
    prescriptions = pd.read_csv(os.path.join(BASE_PATH, "hosp/prescriptions.csv.gz"))
    d_labitems = pd.read_csv(os.path.join(BASE_PATH, "hosp/d_labitems.csv.gz"))
    return patients, admissions, labevents, prescriptions, d_labitems


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

min_freq = st.sidebar.slider("Frequência mínima das conexões", 1, 20, 2)

st.sidebar.markdown("---")


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
col1.metric("Pacientes", len(patients))
col2.metric("Internações", len(admissions_filtered))
col3.metric("Exames", labevents_filtered["itemid"].nunique())
col4.metric("Prescrições", prescriptions_filtered["drug"].nunique())


# ── Função auxiliar: grafo de coocorrência ────────────────────────────────────
def plot_network(df, source_col, target_col, weight_col, title):
    """Constrói e retorna um grafo interativo de coocorrência usando NetworkX + Plotly."""

    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row[source_col], row[target_col], weight=row[weight_col])

    pos = nx.spring_layout(G, k=1.5, seed=42)

    # Traço das arestas
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1),
        hoverinfo="none",
    )

    # Traço dos nós
    node_x, node_y, node_text, node_size = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        degree = G.degree(node)
        node_size.append(10 + degree * 5)
        node_text.append(f"{node}<br>Conexões: {degree}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=list(G.nodes()),
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            size=node_size,
            color=node_size,
            colorscale="Viridis",
            showscale=True,
        ),
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=title,
        showlegend=False,
        height=700,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
    )

    return fig


# ── Função auxiliar: pares de coocorrência ────────────────────────────────────
def build_pairs(df, group_col, item_col, max_items_per_group=20):
    """Gera todos os pares de itens que coocorrem dentro do mesmo grupo (ex: internação)."""
    pairs = []
    for items in df.groupby(group_col)[item_col].apply(lambda x: x.unique()[:max_items_per_group]):
        for pair in combinations(sorted(items), 2):
            pairs.append(pair)
    return pairs


# ── Abas principais ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 Demografia",
    "🏥 Internações",
    "🧪 Exames",
    "💊 Medicamentos",
])


# ── Aba 1: Demografia ─────────────────────────────────────────────────────────
with tab1:

    # ── Pirâmide etária ──
    bins = [0, 18, 30, 40, 50, 60, 70, 80, 90, 120]
    labels = ["0–17", "18–29", "30–39", "40–49",
              "50–59", "60–69", "70–79", "80–89", "90+"]

    patients_pyramid = patients.copy()
    patients_pyramid["age_group"] = pd.cut(
        patients_pyramid["anchor_age"], bins=bins, labels=labels, right=False
    )

    fem = (
        patients_pyramid[patients_pyramid["gender"] == "F"]
        .groupby("age_group", observed=True)
        .size()
        .reset_index(name="count")
    )
    fem["count_neg"] = -fem["count"] # espelha para a esquerda

    male = (
        patients_pyramid[patients_pyramid["gender"] == "M"]
        .groupby("age_group", observed=True)
        .size()
        .reset_index(name="count")
    )

    fig_pyramid = go.Figure()

    fig_pyramid.add_trace(go.Bar(
        y=fem["age_group"].astype(str),
        x=fem["count_neg"],
        name="Feminino",
        orientation="h",
        marker_color="#5DCAA5",
        customdata=fem["count"],
        hovertemplate="%{customdata} pacientes<extra>Feminino</extra>",
    ))

    fig_pyramid.add_trace(go.Bar(
        y=male["age_group"].astype(str),
        x=male["count"],
        name="Masculino",
        orientation="h",
        marker_color="#7F77DD",
        hovertemplate="%{x} pacientes<extra>Masculino</extra>",
    ))

    fem_max = fem["count"].max() if not fem.empty else 0
    male_max = male["count"].max() if not male.empty else 0

    max_val = int(max(fem_max, male_max)) + 2
    tick_vals = list(range(-max_val, max_val + 1, 2))

    fig_pyramid.update_layout(
        title="Pirâmide Etária por Gênero",
        barmode="relative",
        bargap=0.15,
        xaxis=dict(
            tickvals=tick_vals,
            ticktext=[str(abs(v)) for v in tick_vals],
            title="Nº de pacientes",
            zeroline=True,
            zerolinewidth=1,
        ),
        yaxis=dict(title="Faixa etária"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
    )

    st.plotly_chart(fig_pyramid, use_container_width=True)

    c1, c2 = st.columns(2)

    # ── Boxplot de idade por gênero ──
    with c1:
        fig = px.box(
            patients,
            x="gender",
            y="anchor_age",
            color="gender",
            points="outliers",
            color_discrete_map={
                "F": "#5DCAA5",
                "M": "#7F77DD"
            },
            title="Distribuição de Idade por Gênero",
            labels={
                "anchor_age": "Idade",
                "gender": "Gênero"
            }
        )

        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    # ── Donut de gênero ──
    with c2:
        gender_counts = patients["gender"].value_counts().reset_index()
        gender_counts.columns = ["gender", "count"]

        fig_donut = go.Figure(go.Pie(
            labels=gender_counts["gender"],
            values=gender_counts["count"],
            hole=0.55,
            marker_colors=["#5DCAA5", "#7F77DD"],
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} pacientes (%{percent})<extra></extra>",
        ))

        fig_donut.update_layout(
            title="Proporção por Gênero",
            showlegend=False,
            height=400,
            annotations=[dict(
                text=f"{len(patients)}<br>pacientes",
                x=0.5,
                y=0.5,
                font_size=14,
                showarrow=False,
            )],
        )

        st.plotly_chart(fig_donut, use_container_width=True)


# ── Aba 2: Internações ────────────────────────────────────────────────────────
with tab2:
    admission_counts = admissions_filtered["admission_type"].value_counts().reset_index()
    admission_counts.columns = ["admission_type", "count"]

    fig = px.bar(
        admission_counts, x="admission_type", y="count",
        color="count", title="Distribuição dos Tipos de Admissão",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cálculo do tempo de permanência em horas
    admissions_filtered = admissions_filtered.copy()
    admissions_filtered["admittime"] = pd.to_datetime(admissions_filtered["admittime"])
    admissions_filtered["dischtime"] = pd.to_datetime(admissions_filtered["dischtime"])
    admissions_filtered["los_hours"] = (
        admissions_filtered["dischtime"] - admissions_filtered["admittime"]
    ).dt.total_seconds() / 3600

    los = admissions_filtered.groupby("admission_type")["los_hours"].mean().reset_index()

    fig = px.bar(
        los.sort_values("los_hours"),
        x="los_hours", y="admission_type",
        orientation="h", title="Tempo Médio de Permanência (horas)",
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Aba 3: Exames ─────────────────────────────────────────────────────────────
with tab3:
    # Exames mais solicitados
    lab_counts = labevents_filtered["itemid"].value_counts().reset_index()
    lab_counts.columns = ["itemid", "count"]

    top_labs = (
        lab_counts
        .merge(d_labitems[["itemid", "label"]], on="itemid")
        .head(top_n)
    )

    fig = px.bar(
        top_labs.sort_values("count"), x="count", y="label",
        orientation="h", title=f"Top {top_n} Exames Mais Solicitados",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_labs, use_container_width=True)

    # Pares de exames mais frequentes na mesma internação
    pairs = build_pairs(labevents_filtered, "hadm_id", "itemid")

    df_pairs = pd.DataFrame(pairs, columns=["lab1", "lab2"])
    top_pairs = df_pairs.value_counts().reset_index(name="count").head(top_n)

    top_pairs = (
        top_pairs
        .merge(d_labitems[["itemid", "label"]], left_on="lab1", right_on="itemid", how="left")
        .rename(columns={"label": "exam1"})
        .merge(d_labitems[["itemid", "label"]], left_on="lab2", right_on="itemid", how="left")
        .rename(columns={"label": "exam2"})
    )
    top_pairs["pair"] = top_pairs["exam1"] + " & " + top_pairs["exam2"]

    fig = px.bar(
        top_pairs.sort_values("count"), x="count", y="pair",
        orientation="h", title=f"Top {top_n} Combinações de Exames",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_pairs[["exam1", "exam2", "count"]], use_container_width=True)

    # Rede de coocorrência de exames filtrada por frequência mínima
    top_pairs_net = top_pairs[top_pairs["count"] >= min_freq]
    network_fig = plot_network(top_pairs_net, "exam1", "exam2", "count", "Rede de Coocorrência de Exames")
    st.plotly_chart(network_fig, use_container_width=True)


# ── Aba 4: Medicamentos ───────────────────────────────────────────────────────
with tab4:
    # Medicamentos mais prescritos
    med_counts = prescriptions_filtered["drug"].value_counts().reset_index()
    med_counts.columns = ["drug", "count"]

    fig = px.bar(
        med_counts.head(top_n).sort_values("count"), x="count", y="drug",
        orientation="h", title=f"Top {top_n} Medicamentos Prescritos",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Normalização dos nomes de medicamentos antes de gerar pares
    prescriptions_filtered = prescriptions_filtered.copy()
    prescriptions_filtered["drug_cleaned"] = (
        prescriptions_filtered["drug"].str.strip().str.lower()
    )

    pairs = build_pairs(prescriptions_filtered, "hadm_id", "drug_cleaned")

    if not pairs:
        st.warning("Não há dados suficientes para gerar combinações.")
        st.stop()

    df_pairs = pd.DataFrame(pairs, columns=["drug1", "drug2"])
    top_pairs = df_pairs.value_counts().reset_index(name="count").head(top_n)
    top_pairs["pair"] = top_pairs["drug1"] + " & " + top_pairs["drug2"]

    fig = px.bar(
        top_pairs.sort_values("count"), x="count", y="pair",
        orientation="h", title=f"Top {top_n} Combinações de Medicamentos",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_pairs, use_container_width=True)

    # Rede de co-prescrição filtrada por frequência mínima
    top_pairs_net = top_pairs[top_pairs["count"] >= min_freq]
    network_fig = plot_network(top_pairs_net, "drug1", "drug2", "count", "Rede de Co-prescrição de Medicamentos")
    st.plotly_chart(network_fig, use_container_width=True)

