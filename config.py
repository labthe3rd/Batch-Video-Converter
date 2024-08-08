# config.py

import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('settings.cfg')

ffmpeg_path = config.get("Path", "ffmpeg")
ffprobe_path = config.get("Path", "ffprobe")
ffplay_path = config.get("Path", "ffplay")
output_extensions = config.get("Extensions", "output_extensions").split(', ')

#Codecs and containers
codecs = config['Codecs']
