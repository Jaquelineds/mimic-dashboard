import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render(patients):
    """Renderiza a pirâmide etária, boxplot de idade e donut de gênero."""

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
        .reindex(labels, fill_value=0)
        .rename_axis("age_group")
        .reset_index(name="count")
    )
    fem["count_neg"] = -fem["count"]  # espelha para a esquerda

    male = (
        patients_pyramid[patients_pyramid["gender"] == "M"]
        .groupby("age_group", observed=True)
        .size()
        .reindex(labels, fill_value=0)
        .rename_axis("age_group")
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
        title=dict(
            text="Pirâmide Etária por Gênero",
            x=0.5,
            xanchor="center",
            xref="paper",
        ),
        barmode="relative",
        bargap=0.15,
        xaxis=dict(
            tickvals=tick_vals,
            ticktext=[str(abs(v)) for v in tick_vals],
            title_text="Nº de pacientes",
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
                "M": "#7F77DD",
            },
            title="Distribuição de Idade por Gênero",
            labels={
                "anchor_age": "Idade",
                "gender": "Gênero",
            },
        )

        fig.update_layout(showlegend=False, title_x=0.5, title_xanchor="center", title_xref="paper")

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
            title_x=0.5,
            title_xanchor="center",
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
