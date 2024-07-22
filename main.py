"""Batch Video Converter

This script will allow users to select multiple video files and convert them to a desired format using ffmpeg.

Programmer:     Louis Bersine
Company:        The Party Zone VR
Date:           07/21/2024
Description:    Handle batch converting video files with ffmpeg
Rev:            0

Theme-Editor:   Use ttkbootstrap to easily create a nice looking gui
Theme-Editor-cmd:   python -m ttkcreator

"""




from typing import ClassVar
from serial.tools.list_ports import comports
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import PhotoImage,filedialog
import subprocess
import subprocess, glob, os
import configparser
import pyglet
from PIL import Image, ImageTk
import threading


#Get config file
config = configparser.ConfigParser()
config.read('settings.cfg')
ffmpeg_path=config.get("Path","ffmpeg")
ffprobe_path=config.get("Path","ffprobe")
ffplay_path=config.get("Path","ffplay")

output_extensions=config.get("Extensions","output_extensions").split(', ')

#Global Variables
inputDirectory = ""
outputDirectory = ""
file_list = []




"""ExitApp

This function will destroy the root process and exit the app.

"""

def ExitApp():
    print('Quitting App')
    root.destroy

"""BrowseInputDirectory

Select input directory for video conversion.
    
"""

def BrowseInputDirectory():
    global outputDirectory
    global inputDirectory
    inputDirectory = filedialog.askdirectory(initialdir="/",
                                       title="Select Directory",
                                       )
    
    #Change Label
    selectInputDirLabel.configure(text=f'{inputDirectory}')
    if  outputDirectory == "":
        print(f'Setting output directory to {inputDirectory}')
        outputDirectory = inputDirectory
        selectOutputDirLabel.configure(text=f'{outputDirectory}')
    print('Input selected, now get the files into an array')
    StartGetFiles()
"""BrowseOutputDirectory

Select output directory for video conversion.
    
"""

def BrowseOutputDirectory():
    global outputDirectory
    outputDirectory = filedialog.askdirectory(initialdir="/",
                                       title="Select Directory",
                                       )
    
    #Change Label
    selectOutputDirLabel.configure(text=f'{outputDirectory}')

"""GetFiles

This function will create an array of all the files in the directory and child directory
"""
def GetFiles():
    global file_list
    
    # Get the list of video extensions from the config file
    video_extensions = config.get('Extensions', 'output_extensions').split(', ')
    
    directory = inputDirectory
    #Instantiate file list when new directory is selected
    file_list = []
    
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(tuple(video_extensions)):
                full_path = os.path.join(root, file)
                full_path = full_path.replace('\\', '/')
                file_list.append(full_path)
    ffmpeg_output_box.delete(1.0,END)
    ffmpeg_output_box.insert(tk.END, 'Files Found:\n')

             
    for file in file_list:
        print(file)  
        ffmpeg_output_box.insert(tk.END, file + '\n')
        ffmpeg_output_box.yview(tk.END)
        

"""ConvertVideo

Function will first add all the files to an array. It will then convert each file and output it to the output folder.

"""

def ConvertVideo():
    extension = selectExtensionCombobox.get()
    print(extension)
    ffmpeg_output_box.delete(1.0,END)
    if extension != "":
        if file_list:   
            for file in file_list:
                filename, _ = os.path.splitext(os.path.basename(file))
                output_file = os.path.join(outputDirectory, f'{filename}{extension}')
                output_file = output_file.replace('\\', '/')
                print(f'Output filename is  {output_file}')
                cmd = [ffmpeg_path, '-i', file, output_file, '-y']
                print(cmd)
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                output, error = process.communicate()
                ffmpeg_output_box.delete(1.0,END)
                ffmpeg_output_box.insert(tk.END, f'Converting {file} to {output_file}\n')
                ffmpeg_output_box.insert(tk.END, output + '\n' + error + '\n')
                ffmpeg_output_box.yview(tk.END)
        else:
            print("No video files found.")
            ffmpeg_output_box.insert(tk.END, f'No files found.')
    else:
        print('Must select an output format to run the script')
        ffmpeg_output_box.insert(tk.END, f'Please select an output extension.')

def StartConvertVideo():
    #create separate thread for converting video
    print('Starting convert video thread')
    t_convert = threading.Thread(target=lambda: ConvertVideo())
    t_convert.start()
    
def StartGetFiles():
    #create separate thread for getting files
    print('Getting FIles')
    t_getfiles = threading.Thread(target=lambda: GetFiles())
    t_getfiles.start()

'''GUI Creation

Code that creates the GUI

'''
#Create Window
root = ttk.Window(themename='darkly')
root.title('Batch Video Converter')
root.geometry('960x800')

#create icon
ico = Image.open('Assets\\icons\\app.ico')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
# Create the icon

#Create button icons
#Create icons for buttons
browse_icon = ImageTk.PhotoImage(Image.open('Assets\\icons\\Browse.png').resize((25,25)))



#Title Frame
titleFrame = ttk.Frame(root)
titleFrame.pack(side=TOP,pady=10)

#Header
titleHeader = ttk.Label(titleFrame,text='Batch Video Converter', font=("Arial",20))
titleHeader.pack(side=TOP)

#Description
titleDescription = ttk.Label(titleFrame,text='Powered by FFMPEG', font=("Consolas",8))
titleDescription.pack(side=TOP)

#Input Select File Frame
selectInputFrame = ttk.Frame(root)
selectInputFrame.pack(side=TOP,pady=20)

#Input Select Label
selectInputLabel = ttk.Label(selectInputFrame, text='Select Input Folder', font=("Arial",14))
selectInputLabel.pack(side=TOP,pady=5)

#Input Select File Label
selectInputDirLabel = ttk.Label(selectInputFrame, text='',font=("Consolas",14),bootstyle='inverse',width=40)
selectInputDirLabel.pack(side=LEFT, padx=5)

#Input Select File Button
selectInputDirButton = ttk.Button(selectInputFrame, image=browse_icon, command=BrowseInputDirectory)
selectInputDirButton.pack(side=LEFT)

#Output Select File Frame
selectOutputFrame = ttk.Frame(root)
selectOutputFrame.pack(side=TOP,pady=20)

#Output Select Label
selectOutputLabel = ttk.Label(selectOutputFrame, text='Select Output Folder', font=("Arial",14))
selectOutputLabel.pack(side=TOP,pady=5)

#Output Select File Label
selectOutputDirLabel = ttk.Label(selectOutputFrame, text='',font=("Consolas",14),bootstyle='inverse',width=40)
selectOutputDirLabel.pack(side=LEFT, padx=5)

#Output Select Directory Button
selectOutputDirButton = ttk.Button(selectOutputFrame, image=browse_icon, command=BrowseOutputDirectory)
selectOutputDirButton.pack(side=LEFT)

#Output Select Frame
selectExtensionFrame = ttk.Frame(root)
selectExtensionFrame.pack(side=TOP, pady=20)

selectExtensionLabel = ttk.Label(selectExtensionFrame, text="Output Extension", font=('.',16))
selectExtensionLabel.pack(side=LEFT)

#Output Format Select
selectExtensionCombobox = ttk.Combobox(selectExtensionFrame,values=output_extensions,state=READONLY)
selectExtensionCombobox.pack(side=LEFT)


#Convert Frame
convertFrame = ttk.Frame(root)
convertFrame.pack(side=TOP,pady=20)

#Convert Button
convertButton = ttk.Button(convertFrame,text='START',command=StartConvertVideo,width=15)
convertButton.pack(side=TOP)

# FFmpeg Output Frame
ffmpegOutputFrame = ttk.Frame(root)
ffmpegOutputFrame.pack(side=TOP, pady=20)

# FFmpeg Output Label
ffmpegOutputLabel = ttk.Label(ffmpegOutputFrame, text='FFmpeg Output', font=("Arial", 14))
ffmpegOutputLabel.pack(side=TOP, pady=5)

# FFmpeg Output Text Box
ffmpeg_output_box = ttk.ScrolledText(ffmpegOutputFrame, wrap=tk.WORD, width=60, height=3, font=("Consolas", 10))
ffmpeg_output_box.pack(side=TOP, padx=5, pady=5)

#Exit Frame
exitFrame = ttk.Frame(root)
exitFrame.pack(side=BOTTOM,pady=40)

#Exit Button
exitButton = ttk.Button(exitFrame,text='EXIT',command=root.destroy,width=15)
exitButton.pack(side=TOP)



#Run Program
root.mainloop()

