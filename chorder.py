import os
import tkinter as tk
from pygame import mixer
import pandas as pd

# Initialize the mixer module for playing sounds.
mixer.init()

# Load chord continuations
continuations_df = pd.read_csv('continuations.csv')
# Initialize main window
window = tk.Tk()

# Get list of files
files = os.listdir('./chords')

# Get unique chord types and root notes
chord_types = sorted(set(f.split('_')[1] for f in files))
root_notes = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']

# Map each note to its semitone value for easy calculation of continuations
note_to_semitone = {note: i for i, note in enumerate(root_notes)}
semitone_to_note = {i: note for i, note in enumerate(root_notes)}

class ChordButton(tk.Button):
    def __init__(self, master=None, chord=None, **kwargs):
        super().__init__(master, **kwargs)
        self.chord = chord

# Define a function to highlight continuations
def highlight_continuations(current_chord):
    # Reset all button backgrounds to white
    for button in button_list:
        button.config(bg='white')

    # Extract current root note and chord type
    chord_root, chord_type = current_chord.split('_')[0], current_chord.split('_')[1]

    # Filter continuations for current chord type
    current_continuations = continuations_df[continuations_df['Current chord type'] == chord_type]
    print(current_continuations)

    # Iterate over each continuation rule
    for _, rule in current_continuations.iterrows():
        # Calculate new root note
        new_semitone = (note_to_semitone[chord_root] + rule['offset in semitones']) % 12
        new_note = semitone_to_note[new_semitone]

        # Highlight all matching buttons
        for button in button_list:
            button_chord = button.chord.split('_')[0]
            button_type = button.chord.split('_')[1]
            if new_note == button_chord and rule['target chord type'] == button_type:
                button.config(bg=rule['highlight color'])

# Define a function to play sound and highlight continuations
def play_sound(file_path, chord):
    # Play sound
    mixer.music.load(file_path)
    mixer.music.play()

    # Highlight continuations
    highlight_continuations(chord)

# Create list to keep track of all buttons
button_list = []

# Create table of buttons
for i, chord_type in enumerate(chord_types, start=1):
    # Add row header
    tk.Label(window, text=chord_type).grid(row=i, column=0)
    window.grid_rowconfigure(i, weight=1)  # allow the row to expand vertically

    for j, root_note in enumerate(root_notes):
        tk.Label(window, text=root_note.replace('s', '#')).grid(row=0, column=j+1)
        
        window.grid_columnconfigure(j+1, weight=1)  # allow the column to expand horizontally

        # Add chord buttons
        root_note_file = root_note
        matching_files = [f for f in files if f.startswith(f'{root_note_file}_{chord_type}')]

        # Create a frame for each cell
        cell_frame = tk.Frame(window)
        cell_frame.grid(row=i, column=j+1, sticky='nsew')

        for k, file in enumerate(matching_files):
            # Extract chord and fingering
            chord, fingering = file.split('.')[0], file.split('_')[2].split('.')[0]

            # Create button
            btn = ChordButton(cell_frame, text=f'{fingering}', chord=chord,
                            command=lambda f=file, c=chord: play_sound(f'./chords/{f}', c))
            
            # Save button to list
            button_list.append(btn)

            # Position button within the frame
            btn.pack(fill='both', expand=True)

# Start the Tkinter event loop
window.mainloop()
