'''

Global variables

'''

from PIL import Image, ImageTk
def init():
    global appIcon, browseIcon
    #Define Icons for gui
    appIcon = ImageTk.PhotoImage(Image.open("Assets\\icons\\app.ico"))
    browseIcon = ImageTk.PhotoImage(Image.open('Assets\icons\Browse.png').resize((25, 25)))