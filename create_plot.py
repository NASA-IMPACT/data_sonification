import pandas as pd
import plotly.graph_objects as go
import matplotlib.pylab as plt
import streamlit as st
import matplotlib as mpl
from matplotlib.colors import ListedColormap, Normalize
import numpy as np


def make_chart(df: pd.DataFrame, index, y_col, ymin, ymax, xmin, xmax):
    fig = go.Figure(layout_yaxis_range=[ymin, ymax])
    fig.add_trace(
        go.Scatter(x=df["date_time"][:index], y=df[y_col][:index], mode="markers")
    )
    fig.update_layout(
        width=900,
        height=570,
        xaxis_title="time",
        yaxis_title=y_col,
        xaxis=dict(range=[xmin, xmax]),
    )
    st.write(fig)


def draw_plot(title, times, param_slct, xlabel, ylabel, scale):
    fig, ax = plt.subplots()
    ax.scatter(times, param_slct, s=scale)
    plt.style.use("./pitayasmoothie-light.mplstyle")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    fig.autofmt_xdate()
    plt.title(title)
    st.pyplot(fig)


def map_range(value, inMin, inMax, outMin, outMax, convert_to_ints=False):
    result = outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))
    ret_result = result.round().astype(int) if convert_to_ints else result
    return ret_result


def make_chart_go_bar_up(df, index, parameter, up_and_down = False):
    x = df["time_years"]
    y = df[parameter]
    max_y_lim = 1
    min_y_lim = 0
    max_x_lim = max(x)
    min_x_lim = min(x)
    y_indx = np.ones(len(df))
    y_title = "Normalized"
    
    if up_and_down:
        y_indx = df[parameter]
        max_y_lim = max(y_indx)
        min_y_lim = min(y_indx)
        y_title = "tmp (°C)"

        
    fig = go.Figure(layout_yaxis_range=[min_y_lim, max_y_lim])
    cmap = ListedColormap(
        [
            "#08306b",
            "#08519c",
            "#2171b5",
            "#4292c6",
            "#6baed6",
            "#9ecae1",
            "#c6dbef",
            "#deebf7",
            "#fee0d2",
            "#fcbba1",
            "#fc9272",
            "#fb6a4a",
            "#ef3b2c",
            "#cb181d",
            "#a50f15",
            "#67000d",
        ]
    )
    norm = Normalize(df[parameter].min(), df[parameter].max())
    colors = [mpl.colors.to_hex(cmap(norm(val))) for val in y]
    fig.add_trace(
        go.Bar(x=x[:index], y=y_indx[:index], marker=dict(color=colors))
    )
    fig.update_layout(
        xaxis_title="years",
        yaxis_title=f"{parameter}:{y_title}",
        xaxis=dict(range=[min_x_lim, max_x_lim]),
        yaxis=dict(range=[min_y_lim, max_y_lim])
    )
    st.write(fig)
