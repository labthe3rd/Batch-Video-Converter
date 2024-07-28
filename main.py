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
#At start add path to Modules folder
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, './Modules')
import assets
from gui import BatchVideoConverterApp # type: ignore
import ttkbootstrap as ttk

if __name__ == "__main__":
    print('Starting gui....')
    root = ttk.Window(themename='darkly')
    app = BatchVideoConverterApp(root)
    root.mainloop()

