import streamlit as st

import pandas as pd
import time
import os
from helpers import (
    draw_plot,
    map_range,
    generate_audio_file,
    play_music,
    stop_music,
    make_chart,
    make_bar_chart,
    make_chart_go_bar,
    make_chart_go_bar_up
)
from audiolazy import str2midi

def get_cusomized_data(csv_file_path):
    df = pd.read_csv(csv_file_path, index_col=None)

    df["time"] = pd.to_datetime(df["time"])
    df['time_years'] = df['time'].dt.year
    df.sort_values(by=["time"], inplace=True)
    df.reset_index(inplace=True)
    df["time_elapsed_months"] = df["time"] - min(df["time"])
    df["time_elapsed_months"] = df["time_elapsed_months"].apply(
        lambda row: (row.days)
    )
    df.drop(["index"], axis=1, inplace=True)
    return df

input_file = st.file_uploader("Upload Data in CSV format", type="csv")
params_lst = st.container()
if input_file:
    df = get_cusomized_data(
        csv_file_path=input_file
    )
    #st.dataframe(df)
    times = df["time_elapsed_months"].values
    with params_lst:
        param_lst = list(df.columns)
        param_lst.remove("time")
        param_lst.remove("time_elapsed_months")
        default_value_indx = param_lst.index(param_lst[0])
        param_slct = st.selectbox(
            "Select Parameter", param_lst, index=default_value_indx
        )
    with st.sidebar.expander("🔎 Discover"):
        st.markdown(
            "<h2 style='color: yellow' >Data Discovery</h2>", unsafe_allow_html=True
        )
        show_dataframe = st.checkbox(label="show data")
        plot_data = st.checkbox(label="plot data")

    param_slct_values = df[param_slct].values
    if plot_data:
        draw_plot(
            title=f"[{param_slct}] data",
            times=df["time"].values,
            param_slct=param_slct_values,
            xlabel="Time",
            ylabel=param_slct,
            scale=param_slct_values * 50,
        )
    if show_dataframe:
        st.dataframe(df)
        #st.dataframe(df.loc[:, df.columns!='time_elapsed_months'])
    st.sidebar.markdown("---")
    with st.sidebar.expander("🗜️ Compress"):
        st.markdown(
            "<h2 style='color: yellow' > Data Compression </h2>", unsafe_allow_html=True
        )
        duration_beats = st.number_input(
            label="Duration of beats (seconds)",
            help="How long the full dataset should play",
            min_value=60,
            value=90,
        )
        bpm = st.number_input(
            label="Tempo",
            help="Beats per seconds (60 = 1 beat per second)",
            min_value=60,
        )
        plot_compressed_data = st.checkbox(label="plot compressed data")
    t_data = list()

    if duration_beats:
        t_data = map_range(times, 0, max(times), 0, duration_beats)
        minutes_per_beat = max(times) / duration_beats
        st.sidebar.write(
            f"Minutes per beat: <span style='color: red'> {minutes_per_beat} </span>",
            unsafe_allow_html=True,
        )
        logic_diff = [0]
        for ele in range(1, len(df)):
            logic_diff.append(t_data[ele] - t_data[ele - 1])
        df["logic_diff"] = logic_diff
    if bpm:
        duration_sec = duration_beats * 60 / bpm
        st.sidebar.write(
            f"Duration: <span style='color: red'> {duration_sec} seconds </span>",
            unsafe_allow_html=True,
        )
    if plot_compressed_data:
        draw_plot(
            title=f"[{param_slct}] compressed data",
            times=t_data,
            param_slct=param_slct_values,
            xlabel="Time [beats]",
            ylabel=param_slct,
            scale=param_slct_values * 50,
        )
    st.sidebar.markdown("---")
    with st.sidebar.expander("🧘‍♂️ Normalize"):
        st.markdown(
            "<h2 style='color: yellow' > Data Normalization </h2>",
            unsafe_allow_html=True,
        )
        y_scaling = st.number_input(
            label="Scale",
            help="Scale the data so you can deferentiate the beats",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
        )
        plot_normalized_data = st.checkbox(label="plot normalized data")
    st.sidebar.write(
        f"Data scaled to: <span style='color: red'> {y_scaling} </span>",
        unsafe_allow_html=True,
    )
    y_data = map_range(
        param_slct_values, min(param_slct_values), max(param_slct_values), 0, 1
    )
    y_data = y_data**y_scaling
    if plot_normalized_data:
        draw_plot(
            title=f"{param_slct} normalized data",
            times=times,
            param_slct=y_data,
            xlabel=f"Time [minutes] since {min(df['time']).strftime('%Y-%m-%d %H:%M')}",
            ylabel=f"{param_slct} [normalized]",
            scale=50 * y_data,
        )
    with st.sidebar.expander("🎶 Sonify"):
        st.markdown(
            "<h2 style='color: yellow' > Data Sonification </h2>",
            unsafe_allow_html=True,
        )
        vel_min = st.number_input(
            label="velocity min", help="Minimum Velocity", min_value=35, max_value=50
        )
        vel_max = st.number_input(
            label="velocity max", help="Maximum Velocity", min_value=127, max_value=300
        )
        plot_midi_data = st.checkbox(label="plot midi data per beat")
    note_names = [
        "C1",
        "C2",
        "G2",
        "C3",
        "E3",
        "G3",
        "A3",
        "B3",
        "D4",
        "E4",
        "G4",
        "A4",
        "B4",
        "D5",
        "E5",
        "G5",
        "A5",
        "B5",
        "D6",
        "E6",
        "F#6",
        "G6",
        "A6",
    ]
    note_midis = [str2midi(n) for n in note_names]
    n_notes = len(note_midis)
    st.sidebar.write(
        f"Resolution <span style='color: red'> {n_notes} </span> notes",
        unsafe_allow_html=True,
    )
    midi_data = []
    for ele in y_data:
        note_index = map_range(ele, 0, 1, n_notes - 1, 0, convert_to_ints=True)
        midi_data.append(note_midis[note_index])

    vel_data = []
    for ele in y_data:
        note_velocity = map_range(ele, 0, 1, vel_min, vel_max, convert_to_ints=True)
        vel_data.append(note_velocity)
    if plot_midi_data:
        draw_plot(
            title=f"{param_slct} MIDI per beats",
            times=t_data,
            param_slct=midi_data,
            xlabel="Time [beats]",
            ylabel="Midi note number",
            scale=vel_data,
        )
    
    with st.sidebar.expander("🎹 Listen"):
        file_path = generate_audio_file(bpm, t_data, midi_data, vel_data)
        play_with_plot_button = st.button(
            label="Play (plot)", on_click=play_music, kwargs={"file_path": file_path, "type_display": "plot"}
        )
        play_with_bar_button = st.button(
            label="Play (bar)", on_click=play_music, kwargs={"file_path": file_path, "type_display": "bar"}
        )
        stop_button = st.button(label="Stop", on_click=stop_music)
        with open(file_path, "rb") as file_to_download:
            st.download_button(
                "Download audio",
                file_to_download,
                file_name=os.path.basename(file_path),
            )
    n = len(df)
    #st.dataframe(df)
    plot_spot = st.empty()
    plot_spot_bar = st.empty()

    function_to_use = make_chart
    if play_with_bar_button:
        function_to_use = make_bar_chart
        
    if stop_button:
        n = 0
        plot_spot = st.empty()
    
        
    if play_with_bar_button or play_with_plot_button:
        ymax = max(df[param_slct])+0.1
        ymin = min(df[param_slct])-0.1
        xmax = max(df["time"])
        xmin = min(df["time"])
        cursor_time = df['time'][0].year
        scale = 0      
        for ele in range(n):
            with plot_spot:
                make_chart_go_bar(df, ele)
            with plot_spot_bar:
                make_chart_go_bar_up(df,ele)                

            time.sleep(df["logic_diff"][ele] - scale)
            scale = 0.05
              
