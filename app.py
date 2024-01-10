import streamlit as st
from create_music import generate_audio_file, play_music, stop_music
from data_preprocessing import customized_data
from create_plot import draw_plot, map_range, make_chart, make_chart_go_bar_up
from audiolazy import str2midi
import datetime
import time
import os


if "audio_file" not in st.session_state:
    st.session_state["audio_file"] =""

params_lst = st.container()
# input_file = "None"
#st.sidebar.markdown("Select a variable")
param_lst =[os.path.basename(file_) for file_ in os.listdir("./examples") if file_.endswith('csv')] + ["<upload file>"]
is_global_warming = False
is_global_warming_per_country = False
param_slct = st.sidebar.selectbox("Select a file", param_lst)

input_file = f"./examples/{param_slct}"
if param_slct in ["globalwarming.csv", "Surface_temperature_per_country.csv"]:
    is_global_warming = True
if param_slct == "Surface_temperature_per_country.csv":
    is_global_warming_per_country = True
if param_slct == "<upload file>":

    input_file = st.sidebar.file_uploader("Upload Data in CSV Format", type="csv")
    is_global_warming = False
check_correct = False

if input_file:
    try:
        df_orgin, df = customized_data(
            csv_file_path=input_file, is_global_warming=is_global_warming
        )
        check_correct = True
    except KeyError:
        print(KeyError)
        st.error(
            "Please make sure the uploaded dataset has date_time as first column",
            icon="🚨",
        )
if check_correct:
    #st.dataframe(df)
    times = df["time_elapsed_minutes"].values
    with params_lst:
        param_lst = list(df.columns)
        param_lst.remove("date_time")
        param_lst.remove("time_elapsed_minutes")
        param_lst.remove("time_years")
        default_value_indx = param_lst.index(param_lst[0])
        param_slct = st.selectbox(
            "Select Parameter", param_lst, index=default_value_indx
        )
    with st.sidebar.expander("🔎 Discover"):
        st.markdown(
            "<h2 style='color: yellow' >Data Discovery</h2>", unsafe_allow_html=True
        )
        plot_data = st.checkbox(label="plot data")
        look_at_data = st.checkbox(label="data")

    param_slct_values = df[param_slct].values
    if look_at_data:
        st.dataframe(df_orgin)
    if plot_data:
        draw_plot(
            title=f"[{os.path.basename(str(input_file)).rstrip('.csv')}] data",
            times=df["date_time"].values,
            param_slct=param_slct_values,
            xlabel="date_time",
            ylabel=param_slct,
            scale=param_slct_values * 50,
        )
    st.sidebar.markdown("---")
    with st.sidebar.expander("🗜️ Compress"):
        st.markdown(
            "<h2 style='color: yellow' > Data Compression </h2>", unsafe_allow_html=True
        )
        duration_beats = st.number_input(
            label="Duration of beats (seconds)",
            help="How long the full dataset should play",
            min_value=60,
            value=150,
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
            xlabel=f"Time [minutes] since {min(df['date_time']).strftime('%Y-%m-%d %H:%M')}",
            ylabel=f"{param_slct} [normalized]",
            scale=50 * y_data,
        )
    with st.sidebar.expander("🎶 Sonify"):
        st.markdown(
            "<h2 style='color: yellow' > Data Sonification </h2>",
            unsafe_allow_html=True,
        )
        vel_min = st.number_input(
            label="velocity min", help="Minimum Velocity up to 50", min_value=35, max_value=50
        )
        vel_max = st.number_input(
            label="velocity max", help="Maximum Velocity up to 255", min_value=127, max_value=255
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
        
        play_button = st.button(
            label="Play", on_click=play_music, 
            kwargs={"bpm": bpm, "t_data": t_data,"midi_data":midi_data, "vel_data":vel_data}
        )
        stop_button = st.button(label="Stop", on_click=stop_music)
        if st.session_state["audio_file"]:
            with open(st.session_state["audio_file"], "rb") as file_to_download:
                st.download_button(
                    "Download audio",
                    file_to_download,
                    file_name=os.path.basename(st.session_state["audio_file"]),
                )
    n = len(df)
    gw_plot_spot = st.empty()
    plot_spot = st.empty()
    calibre = 0.03
    time_to_sleep = 0


    if stop_button:
        n = 0
        plot_spot = st.empty()
        if is_global_warming:
            gw_plot_spot = st.empty()
    if play_button:
        
        ymax = max(df[param_slct])
        ymin = min(df[param_slct])
        xmax = max(df["date_time"])
        xmin = min(df["date_time"])
        start = datetime.datetime.now()
        for ele in range(n):
            time_to_sleep = df["logic_diff"][ele] - calibre if df["logic_diff"][ele] - calibre > 0 else 0
            if is_global_warming:
                with gw_plot_spot:
                    make_chart_go_bar_up(df, ele, param_slct, up_and_down=is_global_warming_per_country)
            with plot_spot:
                make_chart(df, ele, param_slct, ymin, ymax, xmin, xmax)
            time.sleep(time_to_sleep)
