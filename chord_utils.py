import holoviews as hv
import pandas as pd
from bokeh.embed import file_html
from bokeh.resources import CDN
from holoviews import dim, opts

hv.extension("bokeh")


def plot_chord(df, source_col, target_col, weight_col, title):
    """Constrói um diagrama de cordas (HoloViews + Bokeh) de coocorrência.

    Recebe um DataFrame de pares já contados (source, target, weight) e
    retorna o HTML de uma figura Bokeh interativa, pronto para ser embutido
    via ``st.components.v1.html``. Retorna ``None`` quando não há pares
    suficientes para desenhar o diagrama.
    """
    if df.empty:
        return None

    links = df[[source_col, target_col, weight_col]].rename(
        columns={source_col: "source", target_col: "target", weight_col: "value"}
    )

    node_names = pd.unique(links[["source", "target"]].values.ravel())
    nodes = hv.Dataset(pd.DataFrame({"index": node_names, "name": node_names}), "index")

    chord = hv.Chord((links, nodes)).opts(
        opts.Chord(
            labels="name",
            cmap="Category20",
            edge_cmap="Category20",
            edge_color=dim("source").str(),
            node_color=dim("index").str(),
            width=700,
            height=700,
            title=title,
        )
    )

    fig = hv.render(chord, backend="bokeh")

    # Centraliza o título para acompanhar o estilo dos demais gráficos do dashboard
    fig.title.align = "center"

    html = file_html(fig, CDN, title)

    # Centraliza horizontalmente a figura dentro do iframe (que ocupa toda a largura)
    html = html.replace(
        "<body>", '<body style="display:flex;justify-content:center;margin:0;">', 1
    )

    return html
