import pygame
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pylab as plt
import streamlit as st
from audiolazy import str2midi
from midiutil import MIDIFile
import uuid
from pygame import mixer

def generate_audio_file(bpm, t_data, midi_data, vel_data):
    my_midi_file = MIDIFile(1) # One track
    my_midi_file.addTempo(track=0, time=0, tempo=bpm)
    for i in range(len(t_data)):
        my_midi_file.addNote(track=0, channel=0, pitch=midi_data[i], time=t_data[i], duration=2, volume=vel_data[i])
    
    file_path = f"./music_notes/{uuid.uuid4()}.mid"
    with open(file_path, "wb") as f:
        my_midi_file.writeFile(f)
    return file_path

def play_music(file_path):
    mixer.init()
    pygame.init()
    pygame.mixer
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def stop_music():
    pygame.mixer.music.stop()

def make_chart(df, index, y_col, ymin, ymax, xmin, xmax):
    fig = go.Figure(layout_yaxis_range=[ymin, ymax] )
    fig.add_trace(go.Scatter(x=df['time'][:index], y=df[y_col][:index],  mode='lines+markers'))
    fig.update_layout(width=900, height=570, xaxis_title='time',
    yaxis_title=y_col, xaxis=dict(range=[xmin,xmax]))
    st.write(fig)


def draw_plot(title, times, param_slct, xlabel, ylabel, scale):
    fig, ax = plt.subplots()
    ax.scatter(times, param_slct, s=scale)
    plt.style.use('./pitayasmoothie-light.mplstyle')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    fig.autofmt_xdate()
    plt.title(title)
    st.pyplot(fig)

def read_data(
    csv_file_path, columns_to_drop=None, columns_to_include=None, index_col=None
):
    if not columns_to_drop:
        columns_to_drop = []
    if not columns_to_include:
        columns_to_include = []
    df = pd.read_csv(csv_file_path, index_col=index_col)
    cols = list(df.columns) + columns_to_drop
    for ele in columns_to_include:
        cols.remove(ele)
    return df.drop(list(set(cols)), axis=1)


def get_cusomized_data(csv_file_path, columns_to_include):
    df = read_data(
        csv_file_path=csv_file_path, columns_to_include=columns_to_include
    )

    df["time"] = pd.to_datetime(df["time"])
    df.sort_values(by=["time"], inplace=True)
    df.reset_index(inplace=True)
    df["time_elapsed_minutes"] = df["time"] - min(df["time"])
    df["time_elapsed_minutes"] = df["time_elapsed_minutes"].apply(
        lambda row: (row.days * 24 * 60) + (row.seconds // 60)
    )
    df.drop(["index"], axis=1, inplace=True)
    return df


def map_range(value, inMin, inMax, outMin, outMax, convert_to_ints=False):
    result = outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))
    ret_result = result.round().astype(int) if convert_to_ints else result
    return ret_result

if __name__=="__main__":
    print("working")