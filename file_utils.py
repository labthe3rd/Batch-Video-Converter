# file_utils.py

import os
from tkinter import filedialog

def browse_directory(title="Select Directory"):
    return filedialog.askdirectory(initialdir="/", title=title)

def get_files(input_directory, video_extensions):
    file_list = []
    for root, _, files in os.walk(input_directory):
        for file in files:
            if file.lower().endswith(tuple(video_extensions)):
                full_path = os.path.join(root, file).replace('\\', '/')
                file_list.append(full_path)
    return file_list
