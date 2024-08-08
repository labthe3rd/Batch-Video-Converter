# gui.py

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from tkinter.scrolledtext import ScrolledText

from config import output_extensions, ffmpeg_path
from file_utils import browse_directory, get_files
from ffmpeg_utils import start_convert_video,get_gpu_accelerators

import assets

class BatchVideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.input_directory = ""
        self.output_directory = ""
        self.file_list = []
        self.accelerators = get_gpu_accelerators()

        self.create_widgets()

    def create_widgets(self):
        #Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.exit_routine)
        
        # Create window
        self.root.title('Batch Video Converter')
        self.root.geometry('720x930')

        # Create icon
        # ico = Image.open('..\\Assets\\icons\\app.ico')
        # photo = ImageTk.PhotoImage(ico)
        assets.init()
        self.root.wm_iconphoto(False, assets.appIcon)

        # Title Frame
        title_frame = ttk.Frame(self.root)
        title_frame.pack(side=TOP, pady=10)

        title_header = ttk.Label(title_frame, text='Batch Video Converter', font=("Arial", 20))
        title_header.pack(side=TOP)

        title_description = ttk.Label(title_frame, text='Powered by FFMPEG', font=("Consolas", 8))
        title_description.pack(side=TOP)

        # Input Select File Frame
        select_input_frame = ttk.Frame(self.root)
        select_input_frame.pack(side=TOP, pady=20)

        select_input_label = ttk.Label(select_input_frame, text='Select Input Folder', font=("Arial", 14))
        select_input_label.pack(side=TOP, pady=5)

        self.select_input_dir_label = ttk.Label(select_input_frame, text='', font=("Consolas", 14), bootstyle='inverse', width=40)
        self.select_input_dir_label.pack(side=LEFT, padx=5)

        select_input_dir_button = ttk.Button(select_input_frame, image=assets.browseIcon, command=self.browse_input_directory)
        select_input_dir_button.pack(side=LEFT)

        # Output Select File Frame
        select_output_frame = ttk.Frame(self.root)
        select_output_frame.pack(side=TOP, pady=20)

        select_output_label = ttk.Label(select_output_frame, text='Select Output Folder', font=("Arial", 14))
        select_output_label.pack(side=TOP, pady=5)

        self.select_output_dir_label = ttk.Label(select_output_frame, text='', font=("Consolas", 14), bootstyle='inverse', width=40)
        self.select_output_dir_label.pack(side=LEFT, padx=5)

        select_output_dir_button = ttk.Button(select_output_frame, image=assets.browseIcon, command=self.browse_output_directory)
        select_output_dir_button.pack(side=LEFT)

        # Extension Select Frame
        select_extension_frame = ttk.Frame(self.root)
        select_extension_frame.pack(side=TOP, pady=20)

        select_extension_label = ttk.Label(select_extension_frame, text="Output Extension", font=('.', 16))
        select_extension_label.pack(side=LEFT)

        self.select_extension_combobox = ttk.Combobox(select_extension_frame, values=output_extensions, state=READONLY)
        self.select_extension_combobox.pack(side=LEFT)
        
        # GPU Acceleration Frame
        gpu_accel_frame = ttk.Frame(self.root)
        gpu_accel_frame.pack(side=TOP, pady=20)

        use_gpu_label = ttk.Label(gpu_accel_frame, text="Use GPU Acceleration", font=('.', 16))
        use_gpu_label.pack(side=LEFT)

        self.use_gpu_var = tk.StringVar()
        self.use_gpu_var.set("No")

        radio_yes = ttk.Radiobutton(gpu_accel_frame, text="Yes", variable=self.use_gpu_var, value="Yes", command=self.toggle_accel_options)
        radio_yes.pack(side=LEFT, padx=10)
        
        radio_no = ttk.Radiobutton(gpu_accel_frame, text="No", variable=self.use_gpu_var, value="No", command=self.toggle_accel_options)
        radio_no.pack(side=LEFT, padx=10)

        # GPU Accelerator Dropdown
        self.accel_var = tk.StringVar()
        self.accel_var.set(self.accelerators[0])  # Set the default option


        accel_menu = ttk.OptionMenu(gpu_accel_frame, self.accel_var, self.accelerators[0],*self.accelerators)
        accel_menu.config(width=10)
        accel_menu.pack(side=LEFT, padx=5)


        # Convert Frame
        convert_frame = ttk.Frame(self.root)
        convert_frame.pack(side=TOP, pady=20)

        convert_button = ttk.Button(convert_frame, text='START', command=self.start_convert_video, width=15)
        convert_button.pack(side=TOP)

        # FFmpeg Output Frame
        ffmpeg_output_frame = ttk.Frame(self.root)
        ffmpeg_output_frame.pack(side=TOP, pady=20)

        ffmpeg_output_label = ttk.Label(ffmpeg_output_frame, text='FFmpeg Output', font=("Arial", 14))
        ffmpeg_output_label.pack(side=TOP, pady=5)

        self.ffmpeg_output_box = ScrolledText(ffmpeg_output_frame, wrap=tk.WORD, width=60, height=3, font=("Consolas", 10))
        self.ffmpeg_output_box.pack(side=TOP, padx=5, pady=5)
        
        # Debug Display Size
        self.size_label = ttk.Label(self.root, text=f"Window Size: {self.root.winfo_width()}x{self.root.winfo_height()} px", font=("Arial", 10))
        self.size_label.pack(side=BOTTOM, pady=5)

        # Exit Frame
        exit_frame = ttk.Frame(self.root)
        exit_frame.pack(side=BOTTOM, pady=40)

        exit_button = ttk.Button(exit_frame, text='EXIT', command=self.exit_routine, width=15)
        exit_button.pack(side=TOP)
        
        # Bind the resize event
        self.root.bind("<Configure>", self.update_size_label)


    def browse_input_directory(self):
        self.input_directory = browse_directory()
        self.select_input_dir_label.configure(text=f'{self.input_directory}')
        if not self.output_directory:
            self.output_directory = self.input_directory
            self.select_output_dir_label.configure(text=f'{self.output_directory}')
        self.file_list = get_files(self.input_directory, output_extensions)
        self.update_file_list_display()

    def browse_output_directory(self):
        self.output_directory = browse_directory()
        self.select_output_dir_label.configure(text=f'{self.output_directory}')

    def start_convert_video(self):
        extension = self.select_extension_combobox.get()
        start_convert_video(self.file_list, self.output_directory, extension, ffmpeg_path, self.ffmpeg_output_box)

    def update_file_list_display(self):
        self.ffmpeg_output_box.delete(1.0, tk.END)
        self.ffmpeg_output_box.insert(tk.END, 'Files Found:\n')
        for file in self.file_list:
            self.ffmpeg_output_box.insert(tk.END, file + '\n')
            self.ffmpeg_output_box.yview(tk.END)
            
    def toggle_accel_options(self):
        if self.use_gpu_var.get() == "Yes":
            print(f'Showing gpu acceleration frame {self.accelerators}')
        else:
            print(f'Hiding gpu acceleration frame')
            
    def update_size_label(self, event):
        """
        Update the size label with the current window size in pixels.

        Args:
            event: The event object containing information about the resize event.
        """
        self.size_label.configure(text=f"Window Size: {self.root.winfo_width()}x{self.root.winfo_height()} px")



    def exit_routine(self):
        print('Application exit routine started')
        self.root.destroy()

# if __name__ == "__main__":
#     root = ttk.Window(themename='darkly')
#     app = BatchVideoConverterApp(root)
#     root.mainloop()
