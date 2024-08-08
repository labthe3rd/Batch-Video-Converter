import os
import subprocess
import traceback
from tkinter import END
import threading
import sys
import time
from config import ffprobe_path, codecs
import re
import json

#Get available hardware accelerators
def get_gpu_accelerators():
    """Gets the available GPU accelerators using ffmpeg."""
    result = subprocess.run(['ffmpeg', '-hwaccels'], stdout=subprocess.PIPE)
    accelerators = result.stdout.decode('utf-8').strip().split('\n')[1:]
    return accelerators

#Remove white spaces that occur after the = sign so we can get the parts.
def remove_spaces_after_equals(input_string):
    print(f'Cleaning up string {input_string}')
    # Use regular expression to find and replace spaces after '='
    return re.sub(r'=\s+', '=', input_string)

def get_total_frames(file_input):
    print(f'Attempting to use {ffprobe_path} to get frames for {file_input}')
    # cmd = [ffprobe_path, '-v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0',file_input]
    cmd = [
        ffprobe_path,
        '-v', 'error',
        '-select_streams', 'v:0',
        '-count_frames',
        '-show_entries', 'stream=nb_read_frames',
        '-of', 'csv=p=0',
        file_input
    ]
    try:
        process = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        print(process.decode('utf-8').strip())
        
        return process.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f'Error occurred: {e.output.decode("utf-8")}')
        return None
    
def get_duration(file_input):
    print(f'Attempting to use {ffprobe_path} to get duration of {file_input}')
    # cmd = [ffprobe_path, '-v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0',file_input]
    cmd = [
        ffprobe_path,
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of','default=noprint_wrappers=1:nokey=1',
        file_input
    ]
    try:
        process = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        print(process.decode('utf-8').strip())
        
        return process.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f'Error occurred: {e.output.decode("utf-8")}')
        return None
    
def calculate_progress_time(duration,ffmpeg_output):
    #Calculate percentage of completion based on time values
    print(f'Calculating progress at output time {ffmpeg_output}')
    time_pattern = re.compile(r"(\d+):(\d+):(\d+)\.(\d+)")
    match = time_pattern.search(ffmpeg_output)
    if match:
        hours, minutes, seconds, centiseconds = map(int, match.groups())
        current_time = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
        percentage = (current_time / duration) * 100
        return percentage
    return None

def get_extension(filename):
    """
    Extracts the file extension from the given filename.
    
    Parameters
    ----------
    filename : str
        File name with it's extension
    
    Returns
    -------
    str
        The extension of the full filename
    """
    _, extension = os.path.splitext(filename)
    return extension

def check_codec(codec: str,ext: str):
    """
    Check if file extension is a container for a codec.
    
    Parameters
    ----------
    codec : str
            The file_codec that will be used to search for the extension.
    ext : str
            The file extension that will be tested.

    Returns
    -------
    bool
        The result of whether the file extensions share the same codec.
    """
    ext = ext.lstrip('.')
    print(f'Checking if {ext} is a container for {codec}')
    if codec in codecs:
        print(f'Codec {codec} found in config file')
        containers = [container.strip() for container in codecs[codec].split(',')]
        print(f'{codec} containers {containers}')
        if ext in containers:
            print(f'{ext} is a container for {codec}')
            return True
        else:
            print(f'{ext} is not a container for {codec}')
            return False
    else:
        print(f'Codec {codec} not found in config file')
        return False

def get_codec(file_path: str):
    """
    Returns the codec for a filename
    
    Parameters
    ----------
    file_path : str
        full filename of the file to check
    
    Returns:
    --------
    str
        The codec of the file
    """
    try:
        print(f'Getting Codec for {file_path}...')
        result = subprocess.run(
            [ffprobe_path, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'json', file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        ffprobe_output = json.loads(result.stdout)
        print(f'FFPROBE Result\n{ffprobe_output}')
        codec_name = ffprobe_output['streams'][0]['codec_name']
        print(f'{codec_name} detected for {file_path}')
        return codec_name
    except Exception as e:
        print(f'Error running ffprobe...\n{e}')
        return f"An error occurred: {str(e)}"

def convert_video(file_list, output_directory, extension, ffmpeg_path, ffmpeg_output_box):
    try:
        for file in file_list:
            force_conversion = False
            skip_file = False
            filename, _ = os.path.splitext(os.path.basename(file))
            input_extension = get_extension(file)
            print(f'Input extension is {input_extension}')
            if input_extension == extension and not force_conversion:
                print(f'Skipping {file} since it is already {extension}')
                skip_file = True
                
            if not skip_file:
                input_codec = get_codec(file)
                codec_match = check_codec(input_codec,extension)
                duration = float(get_duration(file))
                print(f'Duration of file is\n{duration:.2f}')
                output_file = os.path.join(output_directory, f'{filename}{extension}').replace('\\', '/')
                print('Displaying current file to user.')
                ffmpeg_output_box.delete(1.0, END)
                ffmpeg_output_box.insert(END, f'Checking if {file} codec matches {output_file}\n')
                
                print(f'Starting ffmpeg with {output_file}')
                if codec_match:
                    print(f'Converting Container from {input_extension} to {extension}')
                    cmd = [ffmpeg_path,
                        '-i', file,
                        '-vcodec', 'copy', 
                        '-acodec', 'copy',
                        '-map', '0:v',
                        '-map', '0:a',
                        output_file,
                        '-y']
                    
                else:
                    print(f'Encoding {input_extension} to {extension} new format')
                    cmd = [ffmpeg_path, '-hwaccel' ,'cuda','-i', file, output_file, '-y']
                
                #Display to user what type of work is being performed
                if codec_match:
                    ffmpeg_output_box.delete(1.0, END)
                    ffmpeg_output_box.insert(END, f'Changing {file} container to {output_file}\n')
                else:
                    ffmpeg_output_box.delete(1.0, END)
                    ffmpeg_output_box.insert(END, f'Encoding {file} to {output_file}\n')
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                for line in process.stdout:
                    
                    if codec_match:
                        #Only display status by looking for Frame in line.
                        size = time = bitrate = speed = None
                        size_unit = 'KiB'
                        bitrate_unit = 'kbits/s'
                        speed_unit = 'x'
                        if "size=" in line:
                            line = remove_spaces_after_equals(line)
                            parts = line.split()
                            print(f'Parsing the following line:\n{line}')
                            for part in parts:
                                try:
                                    if '=' in part: 
                                        key, value = part.split('=')
                                        key = key.strip()
                                        value = value.strip()
                                        if key == 'size':
                                            # Handle size with unit
                                            size = int(value.replace(size_unit, ''))
                                        elif key == 'time':
                                            print(f'time value: {value}')
                                            time = value
                                        elif key == 'bitrate':
                                            if value:
                                                bitrate = float(value.replace(bitrate_unit, ''))
                                        elif key == 'speed':
                                            speed = float(value.replace(speed_unit, ''))
                                    else:
                                        print(f'skipping part: {part}')

                                except Exception as e:
                                    print(f'Error from part {part}\n{e}')
                                ffmpeg_output_box.delete(1.0, END)
                                ffmpeg_output_box.insert(END, f'Changin container in progress...')
                                if time:
                                    percent_complete = calculate_progress_time(duration,time)
                                    if percent_complete != None:
                                        ffmpeg_output_box.insert(END, f'Progress:{percent_complete:.2f}% speed:{speed}{speed_unit}/')
                                    else:
                                        ffmpeg_output_box.insert(END, f'speed:{speed}{speed_unit}/')
                                else:
                                    ffmpeg_output_box.insert(END,f'speed:{speed}{speed_unit}/')
                        else:
                            print(line)
                    
                    else:
                        #Only display status by looking for Frame in line.
                        frames = fps = q = size = time = bitrate = speed = None
                        size_unit = 'KiB'
                        bitrate_unit = 'kbits/s'
                        speed_unit = 'x'
                        if "frame=" in line:
                            line = remove_spaces_after_equals(line)
                            parts = line.split()
                            print(f'Parsing the following line:\n{line}')
                            for part in parts:
                                try:
                                    if '=' in part: 
                                        key, value = part.split('=')
                                        key = key.strip()
                                        value = value.strip()
                                        if key == 'frame':
                                            frames = int(value)
                                        elif key == 'fps':
                                            fps = float(value)
                                        elif key == 'q':
                                            q = float(value)
                                        elif key == 'Lsize':
                                            # Handle size with unit
                                            size = int(value.replace(size_unit, ''))
                                        elif key == 'time':
                                            print(f'time value: {value}')
                                            time = value
                                        elif key == 'bitrate':
                                            if value:
                                                bitrate = float(value.replace(bitrate_unit, ''))
                                        elif key == 'speed':
                                            speed = float(value.replace(speed_unit, ''))
                                    else:
                                        print(f'skipping part: {part}')

                                except Exception as e:
                                    print(f'Error from part {part}\n{e}')
                                ffmpeg_output_box.delete(1.0, END)
                                ffmpeg_output_box.insert(END, f'Encoding in progress...')
                                if time:
                                    percent_complete = calculate_progress_time(duration,time)
                                    if percent_complete != None:
                                        ffmpeg_output_box.insert(END, f'Progress:{percent_complete:.2f}% frames:{frames} speed:{speed}{speed_unit}/')
                                    else:
                                        ffmpeg_output_box.insert(END, f'frames:{frames} speed:{speed}{speed_unit}/')
                                else:
                                    ffmpeg_output_box.insert(END,f'frames:{frames} speed:{speed}{speed_unit}/')
                        else:
                            print(line)

                ffmpeg_output_box.delete(1.0, END)
                if codec_match:
                    ffmpeg_output_box.insert(END, f'{file} container changed successfully.')
                else:
                    ffmpeg_output_box.insert(END, f'{file} encoded successfully.')
                print('Complete')
            else:
                ffmpeg_output_box.delete(1.0, END)
                ffmpeg_output_box.insert(END, f'Skipping {file}')
                
                
    except Exception as e:
        print(f"Error in thread: {e}")
        traceback.print_exc()

def start_convert_video(file_list, output_directory, extension, ffmpeg_path, ffmpeg_output_box):
    print('Creating thread for video conversion.')
    thread = threading.Thread(target=convert_video, args=(file_list, output_directory, extension, ffmpeg_path, ffmpeg_output_box))
    print('Thread created')
    thread.start()
