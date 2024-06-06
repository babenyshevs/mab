import plotly.graph_objects as go


def get_scatters(trace_ids, x_name, y_name, title, log_yaxis=True):
    fig = go.Figure()
    fig.update_layout(
        xaxis_title=x_name,
        yaxis_title=y_name,
        title=title,
    )
    if log_yaxis:
        fig.update_yaxes(type="log")

    for trace_id in trace_ids:
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines", marker=dict(size=8), name=trace_id))
    return fig


def get_histograms(trace_ids, x_name, title):
    fig = go.Figure()
    fig.update_layout(
        xaxis_title=x_name,
        barmode="overlay",
        title=title,
    )
    for trace_id in trace_ids:
        fig.add_trace(go.Histogram(x=[], nbinsx=10, name=trace_id, opacity=0.5, histnorm="percent"))
    return fig


def get_bars(trace_ids, x_name, title, max_y=None):
    fig = go.Figure()
    fig.update_layout(xaxis_title=x_name, title=title)
    if max_y:
        fig.update_yaxes(range=[0, max_y])
    for trace_id in trace_ids:
        fig.add_trace(
            go.Bar(
                x=[],
                y=[],
                name=trace_id,
                opacity=0.5,
            )
        )
    return fig
