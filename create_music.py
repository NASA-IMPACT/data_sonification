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
    my_midi_file = MIDIFile(1)  # One track
    my_midi_file.addTempo(track=0, time=0, tempo=bpm)
    for i in range(len(t_data)):
        my_midi_file.addNote(
            track=0,
            channel=0,
            pitch=midi_data[i],
            time=t_data[i],
            duration=2,
            volume=vel_data[i],
        )

    file_path = f"./music_notes/note.mid"
    with open(file_path, "wb") as f:
        my_midi_file.writeFile(f)
    return file_path


def play_music(file_path):
    pygame.init()
    pygame.mixer
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


def stop_music():
    pygame.mixer.music.stop()
