#!/bin/env python

import PyInstaller.__main__
import platform

OS = platform.system()                      #Get the OS type ('Linux', 'Darwin' >>Mac<<, 'Windows')
exe_name = 'classify'
args = [
    'classify.py',                          # Script to be bundled
    '--name='+exe_name,                     # equivalent to '-n': The name of the executable
    '--onefile',                            # equivalent to '-F': one exe file build
    '--windowed',                           # equivalent to '-w': no console
    '--hidden-import=PIL._tkinter_finder'
]
PyInstaller.__main__.run(args)
print("[DONE]: "+exe_name+' built.')

args.remove('--windowed')
args.remove('--name='+exe_name)
exe_name = 'classify_cmd'
args.append('--name='+exe_name)
PyInstaller.__main__.run(args)
print("[DONE]: "+exe_name+' built.')

print("[FINISH]")