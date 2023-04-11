import pygame
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pylab as plt
import streamlit as st
from audiolazy import str2midi
from midiutil import MIDIFile
import uuid
from pygame import mixer
from streamlit.components.v1 import html

import os, glob
 

def generate_audio_file(bpm, t_data, midi_data, vel_data):
    my_midi_file = MIDIFile(1)  # One track
    my_midi_file.addTempo(track=0, time=0, tempo=bpm)
    for i in range(len(t_data)):
        my_midi_file.addNote(
            track=0,
            channel=0,
            pitch=midi_data[i],
            time=t_data[i],
            duration=1,
            volume=vel_data[i],
        )


    file_path = f"static/note-{uuid.uuid4()}.midi"
    print(f"file generated: {file_path}")
    with open(file_path, "wb") as f:
        my_midi_file.writeFile(f)
    return file_path


def play_music(bpm, t_data, midi_data, vel_data):
    for filename in glob.glob("static/note-*"):
        os.remove(filename) 
    st.session_state["audio_file"] = generate_audio_file(bpm, t_data, midi_data, vel_data)
    file_path = f"./app/{st.session_state.audio_file}"
    try:
        pygame.init()
        pygame.mixer
        pygame.mixer.music.load(st.session_state.audio_file)
        pygame.mixer.music.play()
    except:
        play_music_spot = st.empty()
        with play_music_spot:
            html(f"""
                <script src='http://www.midijs.net/lib/midi.js'></script>
                <script>MIDIjs.play('{file_path}');</script>
                """)
    return



def stop_music():
    try:
        pygame.mixer.music.stop()
    except:
        print("Running client side")
