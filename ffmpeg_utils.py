import os
import subprocess
import traceback
from tkinter import END
import threading
import sys
import time

def convert_video(file_list, output_directory, extension, ffmpeg_path, ffmpeg_output_box):
    try:
        for file in file_list:
            filename, _ = os.path.splitext(os.path.basename(file))
            output_file = os.path.join(output_directory, f'{filename}{extension}').replace('\\', '/')
            print('Displaying current file to user.')
            ffmpeg_output_box.delete(1.0, END)
            ffmpeg_output_box.insert(END, f'Converting {file} to {output_file}\n')
            
            print('Starting ffmpeg')
            cmd = [ffmpeg_path, '-i', file, output_file, '-y']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in process.stdout:
                ffmpeg_output_box.delete(1.0, END)
                ffmpeg_output_box.insert(END, line)
            ffmpeg_output_box.delete(1.0, END)
            ffmpeg_output_box.insert(END, f'{file} conversion completed.')
                
                
    except Exception as e:
        print(f"Error in thread: {e}")
        traceback.print_exc()

def start_convert_video(file_list, output_directory, extension, ffmpeg_path, ffmpeg_output_box):
    print('Creating thread for video conversion.')
    thread = threading.Thread(target=convert_video, args=(file_list, output_directory, extension, ffmpeg_path, ffmpeg_output_box))
    print('Thread created')
    thread.start()
