
from itertools import combinations

import networkx as nx
import pandas as pd
import plotly.graph_objects as go


def plot_network(df, source_col, target_col, weight_col, title):
    """Constrói e retorna um grafo interativo de coocorrência usando NetworkX + Plotly."""

    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            height=500,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(
                    text="Sem conexões suficientes para exibir a rede.",
                    x=0.5,
                    y=0.5,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14),
                )
            ],
        )
        return fig

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


def build_pairs(df, group_col, item_col, max_items_per_group=20):
    """Gera todos os pares de itens que coocorrem dentro do mesmo grupo (ex: internação)."""
    pairs = []
    grouped_items = (
        df[[group_col, item_col]]
        .dropna(subset=[group_col, item_col])
        .groupby(group_col)[item_col]
        .apply(lambda x: pd.unique(x)[:max_items_per_group])
    )

    for items in grouped_items:
        for pair in combinations(sorted(items), 2):
            pairs.append(pair)
    return pairs
