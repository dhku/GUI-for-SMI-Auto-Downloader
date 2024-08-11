import sys
import os
from cx_Freeze import setup, Executable

# ADD FILES
files = ['icon.ico','themes/','anime.yml','settings.yml','downloads/','log']

# ADD PACKAGE
build_exe_options = {
    "excludes":[
    	"tkinter","matplotlib"
    ],
    "include_files" : files,
    "optimize": 2
}

# TARGET
target = Executable(
    script="main.py",
    base="Win32GUI",
    icon="icon.ico"
)

# SETUP CX FREEZE
setup(
    name = "SMI-AUTO-DOWNLOADER",
    version = "1.0",
    description = "SMI-AUTO-DOWNLOADER",
    author = "KUDONG",
    options = {'build_exe' : build_exe_options},
    executables = [target]
    
)
